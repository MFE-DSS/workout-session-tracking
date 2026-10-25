/**
 * DA-GOV-01 — the visual regression gate (docs/strategy/AUREN_VISUAL_CONTRACT.md).
 *
 * Runs ONLY inside the pinned Playwright image (see run.sh and the CI job
 * `visual-contract`): same Chromium, same fonts, same platform, so a difference
 * is a visual change, not an environment.
 *
 * `updateSnapshots: 'none'` — the gate NEVER writes a baseline. A new baseline
 * exists only through the operator's explicit approval (`run.sh approve`,
 * which passes --update-snapshots=all) and the manifest entry that records it.
 */
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: '.',
  testMatch: 'visual.spec.ts',
  outputDir: './test-results',
  snapshotPathTemplate: '{testDir}/baselines/{arg}{ext}',
  updateSnapshots: 'none',
  retries: 0,
  workers: 1,
  reporter: [['list']],
  expect: {
    // same image, same Chromium: the render is reproducible to the pixel; tolerance is
    // per-pixel colour noise only, never « a few pixels moved »
    toHaveScreenshot: { maxDiffPixels: 0, threshold: 0.1, animations: 'disabled', caret: 'hide' },
  },
  use: {
    baseURL: 'http://127.0.0.1:4719',
    browserName: 'chromium',
    viewport: { width: 480, height: 360 },
    deviceScaleFactor: 2,
    reducedMotion: 'reduce',
    colorScheme: 'dark',
    locale: 'fr-FR',
    timezoneId: 'Europe/Paris',
  },
  webServer: {
    command: 'node serve.mjs ../dist-contract 4719',
    url: 'http://127.0.0.1:4719',
    reuseExistingServer: false,
    timeout: 30_000,
  },
});
