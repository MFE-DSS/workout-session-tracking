#!/usr/bin/env node
/**
 * PHYSICAL_DEVICE_GATE runner — `npm --prefix clients/mobile run device`.
 *
 * One gate, platform adapters underneath. This script DISCOVERS and DIAGNOSES;
 * Expo BUILDS (`expo run:ios --device` / `expo run:android --device`). It never
 * edits credentials, never runs sudo, never treats a simulator or an emulator
 * as gate evidence.
 *
 *   npm --prefix clients/mobile run device              preflight, then build on the physical device
 *   npm --prefix clients/mobile run device -- --check   preflight only (read-only)
 *   npm --prefix clients/mobile run device -- --json    preflight as JSON (read-only)
 */
import { execFileSync, spawn } from 'node:child_process';
import { mkdtempSync, readdirSync, readFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { createInterface } from 'node:readline/promises';
import { fileURLToPath } from 'node:url';

const MOBILE = dirname(dirname(fileURLToPath(import.meta.url)));
const args = new Set(process.argv.slice(2));
const CHECK_ONLY = args.has('--check') || args.has('--json');

// ── tiny process helpers (no shell, no string interpolation into a shell) ─────

function run(cmd, argv, opts = {}) {
  try {
    return { ok: true, out: execFileSync(cmd, argv, { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'], timeout: 30_000, ...opts }) };
  } catch (e) {
    return { ok: false, out: String(e.stdout ?? ''), err: String(e.stderr ?? e.message ?? '') };
  }
}

function has(cmd) {
  return run('/usr/bin/which', [cmd]).ok;
}

// ── shared environment ───────────────────────────────────────────────────────

function common() {
  const pkg = JSON.parse(readFileSync(join(MOBILE, 'package.json'), 'utf8'));
  return {
    node: process.version,
    npm: run('npm', ['--version']).out.trim() || null,
    expo_sdk: pkg.dependencies?.expo ?? null,
    react_native: pkg.dependencies?.['react-native'] ?? null,
    native_dirs: { ios: exists(join(MOBILE, 'ios')), android: exists(join(MOBILE, 'android')) },
  };
}

function exists(path) {
  return run('/bin/test', ['-e', path]).ok;
}

// ── iOS adapter (read-only discovery) ────────────────────────────────────────

function iosAdapter() {
  const report = { available: false, devices: [], checks: {} };
  if (process.platform !== 'darwin' || !has('xcrun')) {
    report.checks.toolchain = 'absent (macOS + Xcode required for the iOS adapter)';
    return report;
  }
  const dir = run('xcode-select', ['-p']).out.trim();
  report.checks.developer_dir = dir || null;
  report.checks.xcode_selected = dir.includes('Xcode.app');
  const xv = run('xcodebuild', ['-version']);
  report.checks.xcode = xv.ok ? xv.out.split('\n')[0].trim() : null;
  report.checks.cocoapods = has('pod') ? run('pod', ['--version'], { env: { ...process.env, LANG: 'en_US.UTF-8' } }).out.trim() || 'present' : null;
  const ids = run('security', ['find-identity', '-v', '-p', 'codesigning']).out;
  const m = ids.match(/(\d+) valid identities found/);
  report.checks.signing_identities = m ? Number(m[1]) : null;
  const all = run('security', ['find-identity', '-p', 'codesigning']).out.match(/(\d+) identities found/);
  report.checks.signing_identities_total = all ? Number(all[1]) : null;
  // the team id lives in the certificate's OU (read-only); it is passed to Expo
  // through the environment, never written to the repository
  const devName = ids.match(/"(Apple Development: [^"]+)"/)?.[1];
  if (devName) {
    const pem = run('security', ['find-certificate', '-c', devName, '-p']).out;
    const subject = pem ? run('openssl', ['x509', '-noout', '-subject'], { input: pem, stdio: ['pipe', 'pipe', 'pipe'] }).out : '';
    report.checks.team_id = subject.match(/OU\s*=\s*([A-Z0-9]{10})/)?.[1] ?? null;
  }
  report.available = report.checks.xcode_selected && Boolean(report.checks.xcode);

  // physical devices — CoreDevice
  const tmp = join(mkdtempSync(join(tmpdir(), 'auren-device-')), 'devices.json');
  if (run('xcrun', ['devicectl', 'list', 'devices', '--json-output', tmp]).ok) {
    try {
      const data = JSON.parse(readFileSync(tmp, 'utf8'));
      for (const d of data?.result?.devices ?? []) {
        const hw = d.hardwareProperties ?? {};
        if (hw.platform !== 'iOS') continue;
        let conn = d.connectionProperties ?? {};
        let props = d.deviceProperties ?? {};
        // The list view can report a stale tunnel state and never reports
        // Developer Mode; the per-device detail view does (read-only).
        const detailFile = join(dirname(tmp), `${hw.udid ?? d.identifier}.json`);
        if (run('xcrun', ['devicectl', 'device', 'info', 'details', '--device', hw.udid ?? d.identifier, '--json-output', detailFile], { timeout: 60_000 }).ok
          || exists(detailFile)) {
          try {
            const detail = JSON.parse(readFileSync(detailFile, 'utf8'))?.result ?? {};
            conn = { ...conn, ...(detail.connectionProperties ?? {}) };
            props = { ...props, ...(detail.deviceProperties ?? {}) };
          } catch {
            /* keep the list view */
          }
        }
        report.devices.push({
          platform: 'ios',
          physical: true,
          id: hw.udid ?? d.identifier,
          name: props.name ?? null,
          model: hw.marketingName ?? hw.productType ?? null,
          os_version: props.osVersionNumber ?? null,
          paired: conn.pairingState === 'paired',
          reachable: conn.tunnelState === 'connected',
          developer_disk_image: props.ddiServicesAvailable ?? null,
          developer_mode: props.developerModeStatus ?? null,
        });
      }
    } catch {
      report.checks.devicectl = 'unreadable output';
    }
  }
  // Xcode's own verdict on each destination (read-only). It names a missing iOS
  // platform component and any device it cannot deploy to, with the reason.
  report.checks.ineligible = [];
  const iosDir = join(MOBILE, 'ios');
  const workspace = exists(iosDir) ? readdirSync(iosDir).find((f) => f.endsWith('.xcworkspace')) : undefined;
  if (workspace) {
    const scheme = workspace.replace('.xcworkspace', '');
    const dest = run('xcodebuild', ['-workspace', join(iosDir, workspace), '-scheme', scheme, '-showdestinations'], { timeout: 120_000 });
    const text = `${dest.out}\n${dest.err ?? ''}`;
    for (const line of text.split('\n')) {
      const at = line.indexOf('error:');
      const idAt = line.indexOf('id:');
      if (!line.includes('platform:iOS') || at < 0 || idAt < 0) continue;
      const id = line.slice(idAt + 3, line.indexOf(',', idAt)).trim();
      const error = line.slice(at + 6).replace(/\}\s*$/, '').trim();
      report.checks.ineligible.push({ id, error });
    }
  }
  report.checks.platform_component_missing = report.checks.ineligible.some((x) => /is not installed/.test(x.error));

  // simulators — listed so they can be named, never selected as gate devices
  const sim = run('xcrun', ['simctl', 'list', 'devices', 'booted', '-j']);
  if (sim.ok) {
    try {
      for (const list of Object.values(JSON.parse(sim.out).devices ?? {})) {
        for (const s of list) report.devices.push({ platform: 'ios', physical: false, id: s.udid, name: s.name, model: 'simulator', os_version: null });
      }
    } catch {
      /* no booted simulator */
    }
  }
  return report;
}

// ── Android adapter (read-only discovery) ────────────────────────────────────

function androidAdapter() {
  const report = { available: false, devices: [], checks: {} };
  if (!has('adb')) {
    report.checks.adb = null;
    return report;
  }
  report.available = true;
  report.checks.adb = run('adb', ['version']).out.split('\n')[0].trim();
  report.checks.android_home = process.env.ANDROID_HOME ?? process.env.ANDROID_SDK_ROOT ?? null;
  for (const line of run('adb', ['devices', '-l']).out.split('\n').slice(1)) {
    const [serial, state, ...rest] = line.trim().split(/\s+/);
    if (!serial) continue;
    const kv = Object.fromEntries(rest.map((p) => p.split(':')).filter((p) => p.length === 2));
    const emulator = serial.startsWith('emulator-') || (kv.product ?? '').includes('sdk');
    let os = null;
    if (state === 'device') os = run('adb', ['-s', serial, 'shell', 'getprop', 'ro.build.version.release']).out.trim() || null;
    report.devices.push({
      platform: 'android',
      physical: !emulator,
      id: serial,
      name: kv.model ?? serial,
      model: kv.model ?? null,
      os_version: os,
      authorized: state === 'device',
      reachable: state === 'device',
    });
  }
  return report;
}

// ── readiness: what blocks THIS device, as ONE next action ───────────────────

function blockerFor(device, ios, android) {
  if (device.platform === 'ios') {
    const c = ios.checks;
    if (!c.xcode_selected) return 'Sélectionner Xcode : `sudo xcode-select -s /Applications/Xcode.app/Contents/Developer` (une fois).';
    if (!c.cocoapods) return 'Installer CocoaPods : `brew install cocoapods`.';
    if (c.platform_component_missing) return 'Installer la plateforme iOS de Xcode : `xcodebuild -downloadPlatform iOS` (sans sudo, plusieurs Go) ou Xcode → Réglages → Composants.';
    const refused = (c.ineligible ?? []).find((x) => x.id === device.id || x.id.includes(device.id));
    if (refused) return `Xcode refuse cet iPhone : « ${refused.error} ».`;
    if (!device.paired) return `Appairer l’iPhone « ${device.name} » : le brancher, le déverrouiller, toucher « Faire confiance ».`;
    if (device.developer_mode && device.developer_mode !== 'enabled') return 'Activer le Mode développeur sur l’iPhone (Réglages → Confidentialité et sécurité → Mode développeur), redémarrer, puis confirmer « Activer » au réveil.';
    if (!device.reachable) return `Déverrouiller l’iPhone « ${device.name} » et le garder branché par câble (il n’est pas joignable pour l’instant).`;
    if (device.developer_disk_image === false) {
      // "not available" often only means "not mounted yet": ask Xcode to mount
      // it (what any device run does first) and report ITS reason, never a guess.
      const mount = run('xcrun', ['devicectl', 'device', 'info', 'apps', '--device', device.id], { timeout: 120_000 });
      const why = `${mount.out}\n${mount.err ?? ''}`;
      if (!mount.ok) {
        if (/DeviceLocked|device is locked/i.test(why)) return `Déverrouiller l’iPhone « ${device.name} » et le laisser déverrouillé pendant la préparation (Xcode doit y monter son image développeur).`;
        const line = why.split('\n').find((l) => l.includes('ERROR:')) ?? why.split('\n').find((l) => l.trim()) ?? 'erreur inconnue';
        return `Xcode n’a pas pu préparer l’iPhone : « ${line.replace('ERROR:', '').trim()} ».`;
      }
    }
    if (c.signing_identities === 0 && c.signing_identities_total > 0)
      return 'Le certificat de développement existe mais n’est pas valide : il manque l’intermédiaire Apple WWDR G3 dans le trousseau (https://www.apple.com/certificateauthority/ → « Worldwide Developer Relations - G3 »).';
    if (c.signing_identities === 0) return 'Ajouter votre identifiant Apple dans Xcode → Réglages → Comptes (une équipe personnelle gratuite suffit).';
    return null;
  }
  if (!android.checks.android_home) return 'Installer le SDK Android (Android Studio) et définir ANDROID_HOME.';
  if (!device.authorized) return `Autoriser le débogage USB sur « ${device.name} » (boîte de dialogue sur le téléphone).`;
  return null;
}

// ── main ─────────────────────────────────────────────────────────────────────

const ios = iosAdapter();
const android = androidAdapter();
const env = common();
const devices = [...ios.devices, ...android.devices];
const physical = devices.filter((d) => d.physical);

if (args.has('--json')) {
  console.log(JSON.stringify({ environment: env, ios: ios.checks, android: android.checks, devices }, null, 2));
  process.exit(0);
}

console.log('PHYSICAL_DEVICE_GATE — préflight');
console.log(`  node ${env.node} · npm ${env.npm} · expo ${env.expo_sdk} · react-native ${env.react_native}`);
console.log(`  adaptateur iOS     : ${ios.available ? `${ios.checks.xcode} · CocoaPods ${ios.checks.cocoapods ?? 'absent'} · identités de signature ${ios.checks.signing_identities ?? '?'}` : 'indisponible'}`);
console.log(`  adaptateur Android : ${android.available ? android.checks.adb : 'indisponible (adb absent)'}`);
for (const d of devices) {
  const kind = d.physical ? `${d.platform} PHYSIQUE` : `${d.platform} simulé`;
  const state = d.physical ? (d.reachable ? 'joignable' : 'NON joignable') : 'ignoré par la porte';
  console.log(`  • ${kind} — ${d.name ?? '?'} (${d.model ?? '?'}, OS ${d.os_version ?? '?'}) — ${state}`);
}
if (!devices.length) console.log('  • aucun appareil détecté');

if (!physical.length) {
  console.log('\nAUCUN APPAREIL PHYSIQUE : la porte ne peut pas tourner. Brancher un iPhone ou un Android (débogage USB).');
  process.exit(2);
}

let chosen = physical[0];
if (physical.length > 1) {
  physical.forEach((d, i) => console.log(`  [${i + 1}] ${d.platform} — ${d.name} (${d.model})`));
  const rl = createInterface({ input: process.stdin, output: process.stdout });
  const pick = Number(await rl.question('Appareil à utiliser : '));
  rl.close();
  chosen = physical[pick - 1] ?? physical[0];
}
console.log(`\nAppareil retenu : ${chosen.platform} — ${chosen.name} (${chosen.model}, OS ${chosen.os_version ?? '?'})`);

const blocker = blockerFor(chosen, ios, android);
if (blocker) {
  console.log(`\nBLOQUÉ — une seule action : ${blocker}`);
  console.log('Puis relancer : npm --prefix clients/mobile run device');
  process.exit(3);
}
if (CHECK_ONLY) {
  console.log('\nPRÊT — `npm --prefix clients/mobile run device` construit et installe la build de développement.');
  process.exit(0);
}

// ── delegate to Expo (the build is Expo's, not ours) ─────────────────────────
const buildId = run('git', ['-C', MOBILE, 'rev-parse', '--short', 'HEAD']).out.trim();
const dirty = run('git', ['-C', MOBILE, 'status', '--porcelain', '--', '.']).out.trim() ? '+uncommitted' : '';
const buildEnv = {
  ...process.env,
  LANG: process.env.LANG || 'en_US.UTF-8',
  EXPO_PUBLIC_BUILD_ID: `${buildId}${dirty}`,
  ...(chosen.platform === 'ios' && ios.checks.team_id ? { APPLE_TEAM_ID: ios.checks.team_id } : {}),
};

function delegate(argv) {
  console.log(`\n→ npx ${argv.join(' ')}`);
  return new Promise((resolve) => {
    spawn('npx', argv, { cwd: MOBILE, stdio: 'inherit', env: buildEnv }).on('exit', (code) => resolve(code ?? 1));
  });
}

// An existing native project generated before the team was known carries no
// DEVELOPMENT_TEAM: regenerate it once (Expo's prebuild), so signing is set.
if (chosen.platform === 'ios' && ios.checks.team_id && exists(join(MOBILE, 'ios'))) {
  const pbx = readdirSync(join(MOBILE, 'ios')).find((f) => f.endsWith('.xcodeproj'));
  const project = pbx ? readFileSync(join(MOBILE, 'ios', pbx, 'project.pbxproj'), 'utf8') : '';
  if (!project.includes('DEVELOPMENT_TEAM')) {
    const code = await delegate(['expo', 'prebuild', '--platform', 'ios']);
    if (code !== 0) process.exit(code);
  }
}

// iOS: `expo run:ios` does not let Xcode create the development provisioning
// profile. One Xcode build with provisioning updates allowed does it, using the
// account the operator added in Xcode (no credential passes through here); the
// following Expo build is then incremental.
if (chosen.platform === 'ios') {
  const iosDir = join(MOBILE, 'ios');
  const ws = readdirSync(iosDir).find((f) => f.endsWith('.xcworkspace'));
  if (ws) {
    console.log('\n→ xcodebuild (profil de développement, équipe personnelle)');
    const code = await new Promise((resolve) => {
      spawn('xcodebuild', [
        '-workspace', join(iosDir, ws), '-scheme', ws.replace('.xcworkspace', ''), '-configuration', 'Debug',
        '-destination', `id=${chosen.id}`, '-derivedDataPath', join(iosDir, 'build'),
        '-allowProvisioningUpdates', '-allowProvisioningDeviceRegistration', '-quiet', 'build',
      ], { stdio: 'inherit', env: buildEnv }).on('exit', (c) => resolve(c ?? 1));
    });
    if (code !== 0) process.exit(code);
  }
}

const expoArgs = chosen.platform === 'ios'
  ? ['expo', 'run:ios', '--device', chosen.id]
  : ['expo', 'run:android', '--device', chosen.name];
process.exit(await delegate(expoArgs));
