# SPRINT Sx Body 02 — MediaPipe Capture Quality (SPEC REPORT)

**Branche :** `sx-body-02-mediapipe-capture-quality-spec` (worktree isolé sur le tip de référence `72f5215`)
**Type :** SPEC-ONLY. **0 code applicatif, 0 dépendance, 0 MediaPipe, 0 déploiement.**
**Spec produite :** `docs/strategy/SPIGNOS_BODY_CAPTURE_QUALITY_SPEC.md`

## Objet
Spécifier l'intégration future d'un module **Capture Quality** (MediaPipe Pose Landmarker, client-side) aidant l'utilisateur à produire une prise de vue exploitable, **sans analyse médicale, sans stockage d'image/vidéo/landmark, sans Bodygram, sans exposer de surface en production**.

## Recherche (sources officielles)
Docs Google AI Edge / MediaPipe Pose Landmarker (overview + Web/JS). Faits clés : 33 landmarks (image + world), segmentation optionnelle (défaut off), variantes lite/full/heavy, modes IMAGE/VIDEO/LIVE_STREAM (web : IMAGE/VIDEO), package `@mediapipe/tasks-vision`, `FilesetResolver` + `.task`, `detectForVideo` + `requestAnimationFrame`, **inférence bloque le main thread → web workers recommandés**, optimisé fitness on-device. Aucune version pinnée (interdit ce sprint).

## Décisions tranchées
- **Client-side only** (pas d'upload).
- **Assets vendored/local** (pas de CDN) — CDN incompatible avec la CSP actuelle `default-src 'self'` + privacy + reproductibilité.
- **Web worker** (pas main thread) — sourcé sur le blocage main-thread officiel.
- **Flag dédié** `BODY_CAPTURE_QUALITY_ENABLED=false`, distinct de `BODY_ASSESSMENT_ENABLED` et `BODY_INTELLIGENCE_ENABLED`.
- **0 persistance** image/vidéo/landmark ; statuts qualité éphémères navigateur uniquement.
- **Consentement caméra explicite** + kill switch ; usage non médical.
- Note CSP : `Sb Body 02.3` devra élargir la CSP de façon scopée (`script-src 'wasm-unsafe-eval'`, `worker-src 'self'`) — **pas dans ce sprint**.

## Signaux de qualité
12 statuts spécifiés (camera_unavailable, permission_denied, no_person, multiple_persons, partially_out_of_frame, too_close, too_far, low_light, blur_or_motion, unstable_pose, wrong_orientation, quality_ok), formulés comme **aide à la capture** ; wording autorisé/interdit listé (jamais diagnostic/body-fat/morphotype/jugement).

## Build plan (à NE PAS exécuter)
`Sb Body 02.1` (flag + route coquille) → `02.2` (caméra locale, sans MediaPipe) → `02.3` (MediaPipe client-side, qualité éphémère) → `02.4` (hardening mobile/perf/privacy) → `02.R` (recette privée). Chaque lot flag-gaté, non exposé par défaut. Tests futurs listés (flag off/on, privacy, UI, non-régression).

## Fichiers
- Ajouté : `docs/strategy/SPIGNOS_BODY_CAPTURE_QUALITY_SPEC.md`
- Ajouté : `docs/SPRINT_Sx_Body_02_capture_quality_SPEC_REPORT.md` (ce fichier)
- Modifié : `docs/strategy/SPEC_REGISTRY.md` (lignes Sx Body 02 + Sb Body 02)

## Confirmations
- 0 code applicatif / 0 route / 0 JS / 0 CSS / 0 migration / 0 DB
- 0 `requirements.txt` / 0 `pyproject.toml` / 0 `.env*`
- 0 MediaPipe installé / 0 Bodygram / 0 provider / 0 photo-vidéo-landmark
- 0 déploiement / 0 build `Sb Body 02` ouvert

## Verdict
🟡 **SPEC LIVRÉE — PR draft, non mergée, non déployée.** Documentation-only ; aucun test runtime ajouté. Prochaine étape (sur feu vert) : verrouiller la spec puis ouvrir `Sb Body 02.1` (flag + route coquille, flag-gaté OFF).
