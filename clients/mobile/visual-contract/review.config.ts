/**
 * DA-02.4B.1 — captures CANDIDATE fixtures for the operator's review (`run.sh review`).
 *
 * The gate's own configuration, unchanged, with another test file: a candidate is
 * rendered exactly as its baseline would be, so what the operator approves is what
 * the gate will later compare. Nothing here is compared and nothing is written under
 * baselines/ — the captures land in review-output/ (git-ignored).
 */
import { defineConfig } from '@playwright/test';

import gate from './playwright.config';

export default defineConfig({ ...gate, testMatch: 'review.spec.ts', outputDir: './test-results-review' });
