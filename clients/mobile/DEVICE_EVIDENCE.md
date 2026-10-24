# `PHYSICAL_DEVICE_GATE` — evidence record

Schema `auren.n0.physical-device-evidence/1`, built by `src/lab/evidence.ts`, exported from
the app (⋯ → Journal local du labo → Exporter la preuve). **The same record and the same
thresholds on iOS and Android.** `measured` fields come from the lab instrumentation;
`operator` fields stay `null` until the operator fills them — nothing is guessed.

| Block | Field | Source | Threshold |
|---|---|---|---|
| DEVICE | `platform`, `model`, `model_id`, `os_version`, `physical` | OS (`expo-device`) | `physical` must be `true` to count |
| BUILD | `expo_sdk`, `react_native`, `app_version`, `build_id` | app config + runner (`git` SHA, `+uncommitted` when dirty) | — |
| UX | `g_val_ms` (tap → REST painted) | measured | p95 ≤ 100 ms |
| UX | `g_local_ms` (journal + outbox transaction) | measured | p95 ≤ 20 ms |
| UX | `thumb_reach`, `safe_area`, `keyboard`, `dynamic_text`, `reduced_motion.observation` | operator | — |
| STATE | `sets_planned`, `sets_validated`, `nominal_path_completed` | measured | 21 / 21 on Push A |
| STATE | `navigation_decisions` (secondary sheets opened) | measured | 0 on the nominal path |
| STATE | `automatic_set_transitions`, `automatic_exercise_transitions`, `rest_skips` | measured | — |
| PERSISTENCE | `journal_sets`, `outbox_pending`, `relaunch_restores`, `sets_restored_after_relaunch`, `commit_failures` | measured | after a force-kill: the validated set is restored · `commit_failures` = 0 |
| PERSISTENCE | `force_kill_observation` | operator | — |
| TIMER | `foreground_end_lateness_ms` | measured | worst ≤ 1000 ms |
| TIMER | `resume_end_lateness_ms` (end detected on return to the app) | measured, reported | — |
| TIMER | `background_locked_observation` | operator | — |
| NATIVE FEEDBACK | `rest_notifications_requested`, `rest_notification_delay_ms` | measured, reported — **not a gate** (OS delivery is not deterministic) | — |
| NATIVE FEEDBACK | `haptics_observation` | operator | — |
| GATE | `counts_as_physical_evidence`, `cross_platform: false`, `operator_verdict` | derived / operator | — |

The only documented platform difference is in the inputs, not in success: `model_id` is
iOS-only (`expo-device`), and Android's notification delivery depends on exact-alarm
policy, which the lab measures and never requests.
