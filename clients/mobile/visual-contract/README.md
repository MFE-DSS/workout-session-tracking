# Visual contract gate (DA-GOV-01)

Authority: `docs/strategy/AUREN_VISUAL_CONTRACT.md`.

The approved look of each governed component is kept here as a pixel baseline. The CI job
`visual-contract` compares every fixture against it.

## Run it

```
bash clients/mobile/visual-contract/run.sh test      # compare to the approved baselines
bash clients/mobile/visual-contract/run.sh approve   # OPERATOR ONLY — rewrites the baselines
```

Both modes run in the **pinned Playwright image**, the same one as CI. They share its Chromium,
its fonts and its platform (`linux/amd64`). The macOS Chromium is never used, because its fonts
would make every comparison fail for the wrong reason.

## A failure means VISUAL REVIEW REQUIRED

It does not mean "bug". The diffs are written to `test-results/`, and CI uploads them as an
artifact. Two outcomes only:

- **the change was not meant** → fix the code; the baseline stays;
- **the change was meant** → only the **operator** approves the new look. The steps are:
  1. run `run.sh approve`;
  2. update `baselines/manifest.json` with the new `sha256`, `approved_by` and `approved_on`;
  3. show the before / after.

  `tests/test_visual_contract_governance.py` fails if a PNG changes without its manifest entry.

The gate itself **never** writes a baseline: the config sets `updateSnapshots: 'none'`.

## Files

| File | Role |
|---|---|
| `visual.spec.ts` | one screenshot comparison per fixture of `src/ui/contract/fixtures.ts` |
| `playwright.config.ts` | viewport, reduced motion, locale, zero-pixel tolerance, never writes |
| `serve.mjs` | dependency-free static server for the `contract` web build |
| `run.sh` | the pinned-image runner (`test` / `approve`) |
| `baselines/*.png` + `manifest.json` | the approved renders and their provenance |
