# Fixtures

Frozen **synthetic** judge outputs used only by the deterministic aggregation regression tests
(`tests/test_auren_muscle_focus_synthetic_review.py`). These are hand-authored, schema-valid examples —
**not** real model outputs and **not** derived from any live run. They exist so the pure aggregation,
consensus, veto-confirmation, and status logic can be tested without any network or model call.

Real model outputs, mutated calibration copies, candidate images and reports are **not** stored here or
anywhere in Git — they live only in the external operator workspace under `08_synthetic_review/`.
