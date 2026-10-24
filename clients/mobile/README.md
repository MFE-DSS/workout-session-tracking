# AUREN vNext — Native Experience Lab (N0)

`Sb_VNEXT_NATIVE_N0_EXPERIENCE_LAB` — **a lab, not production.** No auth, no network,
no production write, no migration. Five states only: MISSION / READY · EXECUTION /
CURRENT SET · EXECUTION / REST · EXECUTION / NEXT EXERCISE · SESSION COMPLETE.
Governing spec: `docs/strategy/Sx_AUREN_MOBILE_EXPERIENCE_VNEXT_SPEC.md` (ADR `ACCEPTED — C2`).

| | |
|---|---|
| Stack | Expo SDK 58 (`expo@58.0.17`) · React Native 0.88.0 · React 19.3.0 · TypeScript 6.0.3 — **every version pinned exactly** |
| Native services | journal + outbox (`expo-sqlite`) · feedback (`expo-haptics`) · rest notification (`expo-notifications`, local only) · keep-awake · device identity (`expo-device`) — each behind an adapter in `src/native/` |
| Data | `src/fixtures/lab_fixture.json`, produced by `scripts/generate_fixtures.py` from the **canonical FastAPI services** on a throwaway SQLite — never hand-written |

## Run on a physical device

```bash
npm --prefix clients/mobile install          # once
npm --prefix clients/mobile run device       # discovers, checks, builds, installs, starts
npm --prefix clients/mobile run device -- --check   # read-only preflight
```

The runner discovers every connected device, **prefers a physical one** (simulators and
emulators are listed but never used for the gate), selects it automatically when there is
exactly one, asks when there are several, and stops with **one** next action when
something blocks. It does not build anything itself: it hands over to Expo
(`expo run:ios --device` / `expo run:android --device`) with the device it chose.

Commands are written from the repository root; from anywhere else use the absolute path,
e.g. `npm --prefix /path/to/repo/clients/mobile run device`.

### When the runner says BLOQUÉ

| Adapter | What it needs (the runner names the missing one) |
|---|---|
| iOS | Xcode selected (`xcode-select`) · CocoaPods · iPhone paired, unlocked and connected · Developer Mode on · Xcode device support for the phone's iOS version · a signing team (a free personal Apple ID is enough for a local lab build) |
| Android | `adb` + Android SDK (`ANDROID_HOME`) · USB debugging authorised on the phone |

**iOS signing, first build only:** run the command from your own Terminal session. macOS asks
whether `codesign` may use your development key — answer **Always Allow** (it may ask once
per framework). A build started from a background/agent session cannot show that prompt and
fails with `errSecInternalComponent`. On the first launch, if iOS blocks the app: Settings →
General → VPN & Device Management → your account → **Trust**. The lab uses local
notifications only (`enableRemoteNotifications: false`): a personal team cannot sign the
Push capability.

No paid developer membership, TestFlight, store or cloud-build credential is involved at
this stage (D10, amended). No credential is ever written to this repository.

## The gate — one definition for every platform

`PHYSICAL_DEVICE_GATE` runs the same checklist and produces the same evidence record on
iOS and on Android (`src/lab/evidence.ts`, schema `auren.n0.physical-device-evidence/1`,
described in `DEVICE_EVIDENCE.md`). In the app: **⋯ → Journal local du labo → Exporter la
preuve (JSON)**.

An iOS run never validates Android, and the reverse. A simulator or emulator record is
marked `physical: false` and never counts.

## Expo Go — quick preview only

`npm --prefix clients/mobile start` + the Expo Go app gives a quick look at the screens.
It is **not** gate evidence: the gate judges the real native runtime (lifecycle,
persistence, haptics, notifications) of the development build.

## Checks

```bash
npm --prefix clients/mobile run typecheck
npm --prefix clients/mobile test
python clients/mobile/scripts/generate_fixtures.py   # regenerate fixtures from canonical services
```
