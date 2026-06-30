# SPIGNOS — Body Capture Quality Spec (MediaPipe Pose Landmarker)

**Sprint :** `Sx Body 02 — MediaPipe Capture Quality Spec`
**Branche :** `sx-body-02-mediapipe-capture-quality-spec`
**Date :** 2026-06-30
**Type :** SPEC-ONLY. **0 code applicatif, 0 route, 0 JS/CSS, 0 migration, 0 dépendance, 0 MediaPipe installé, 0 déploiement.**
**Amont :** `SPIGNOS_BODY_INTELLIGENCE_ROADMAP.md` (lot « Sb Body 02 — MediaPipe Capture Quality »), `SPIGNOS_BODY_PRIVACY_AND_CONSENT_SPEC.md`, `SPIGNOS_BODY_SIGNAL_MODEL_SPEC.md`.

---

## 1. Statut

| Champ | Valeur |
|---|---|
| Statut | ⚪ DRAFT — spec de cadrage du futur module **Capture Quality** |
| Engagement | Aucun. Prépare les builds `Sb Body 02.1 → 02.R`. Aucun build ouvert ici. |
| Rôle MediaPipe | **Outil de qualité de capture uniquement** : aider l'utilisateur à cadrer une photo/flux exploitable. **Jamais** un diagnostic, un body-fat, un score corporel, un morphotype-vérité. |
| Hard contracts | client-side only (pas d'upload image), aucune persistance image/vidéo/landmark, flag dédié OFF par défaut, vendored assets, wording « aide à la capture ». |

> **Garde-fou central :** la capture-quality évalue **l'image/la prise de vue**, jamais le corps. Tout message est une aide à la capture (« recule un peu »), jamais une évaluation corporelle.

---

## 2. Recherche documentaire (sources officielles)

Sources officielles consultées (Google AI Edge / MediaPipe) :
- Pose Landmarker overview — `developers.google.com/edge/mediapipe/solutions/vision/pose_landmarker`
- Pose Landmarker Web/JS — `developers.google.com/edge/mediapipe/solutions/vision/pose_landmarker/web_js`

**Faits techniques retenus (cités/condensés) :**
| Fait | Détail officiel |
|---|---|
| Landmarks | **33 landmarks** corporels, en **coordonnées image normalisées** ET **coordonnées monde** (world). |
| Segmentation | Masque de segmentation **optionnel** (`output_segmentation_masks`, défaut **False**). |
| Variantes modèle | **lite / full / heavy** (float16). Input 224×224×3 (détection) + 256×256×3 (localisation). |
| Modes | `IMAGE`, `VIDEO`, `LIVE_STREAM` (overview). **Web : IMAGE et VIDEO**. |
| Plateformes | Android, Python, **Web (JS/TS)**. |
| Optimisation | « optimized for on-device, real-time fitness applications » ; architecture BlazePose + GHUM 3D. |
| Package Web | `@mediapipe/tasks-vision` (`npm install @mediapipe/tasks-vision`). |
| Chargement | `FilesetResolver.forVisionTasks(<wasm path>)` + modèle `.task` via `modelAssetPath` (`createFromOptions`). |
| Boucle vidéo | `detectForVideo(video, timestamp)` appelé par `requestAnimationFrame`, une fois par frame. |
| Contrainte perf | **« each detection blocks the main thread »** → l'inférence est **synchrone** et bloque l'UI ; **web workers recommandés**. |

**Hypothèses / à confirmer (OQ) :**
- OQ-CDN/version : aucune version n'est **pinnée** dans ce sprint (interdit). Le pin se fera au build `Sb Body 02.3` avec hash d'intégrité.
- OQ-modèle : variante recommandée = **lite** (mobile, latence) — à valider perf sur device réel.
- OQ-délégué GPU/CPU : la doc Web ne détaille pas de délégué explicite ; à confirmer au build.

---

## 3. Décisions d'architecture (tranchées)

### D-1 — Client-side only (pas de serveur) ✅
**Décision :** inférence **100 % côté navigateur**. Aucun upload d'image/vidéo vers le serveur. Le serveur ne sert que (a) la page SSR coquille, (b) les assets statiques (wasm + modèle vendored), (c) le flag.
**Raison :** éviter tout transit/stockage d'image (privacy-by-design), pas de surface d'attaque upload, pas de coût serveur d'inférence. Cohérent avec `analyze_then_delete` du privacy model — ici on ne stocke même rien.

### D-2 — Assets **vendored/local**, PAS de CDN ✅
**Décision :** wasm (`@mediapipe/tasks-vision/wasm`) + modèle `.task` **servis localement** depuis `app/static/` (vendored), pas depuis jsdelivr.
**Raison comparée :**
| Critère | CDN (jsdelivr) | Vendored/local (retenu) |
|---|---|---|
| **CSP actuelle** (`default-src 'self'`) | ❌ bloqué (script/wasm/connect externes interdits) | ✅ compatible `'self'` |
| Privacy | ❌ appel externe (IP utilisateur exposée à un tiers) | ✅ aucun appel externe |
| Reproductibilité | ❌ `@latest` mouvant | ✅ version figée dans le repo |
| Disponibilité | ❌ dépend d'un tiers | ✅ même SLA que l'app |
| Intégrité | dépend de SRI | ✅ fichier versionné + hash |
> **Conséquence CSP (importante) :** la CSP actuelle est `default-src 'self'; ...` sans `script-src` externe ni `worker-src` ni autorisation WASM. Le build `Sb Body 02.3` devra **élargir la CSP de façon scopée** : `script-src 'self' 'wasm-unsafe-eval'` (compilation WASM) + `worker-src 'self'` (web worker). À documenter et restreindre au strict nécessaire. **Aucun changement CSP dans ce sprint spec.**

### D-3 — Stockage du modèle (si implémenté plus tard) ✅
**Décision :** modèle `.task` (variante **lite**) vendored sous `app/static/vendor/mediapipe/` ; chargé via `modelAssetPath` pointant vers l'asset local. Aucun appel réseau externe. Pas de pin de version dans ce sprint.
**Anti-fuite :** CSP `connect-src 'self'` (à ajouter au build) empêche tout fetch externe non maîtrisé.

### D-4 — Web worker, PAS le main thread ✅
**Décision :** l'inférence MediaPipe tourne dans un **web worker** (off-main-thread).
**Raison :** la doc officielle indique que `detectForVideo` **bloque le main thread** ; sur mobile cela gèle l'UI. Le worker reçoit les frames (ou un `OffscreenCanvas`/`ImageBitmap`), renvoie des **statuts de qualité éphémères** au thread principal. Conception **mobile-first** : aucun gel UI, feedback fluide.
**Fallback :** si web worker / OffscreenCanvas indisponible → message « capture indisponible sur ce navigateur », pas de dégradation silencieuse.

### D-5 — Feature flag dédié `BODY_CAPTURE_QUALITY_ENABLED=false` ✅
**Décision :** nouveau flag `body_capture_quality_enabled: bool = Field(default=False)`, **distinct** de `body_assessment_enabled` et `body_intelligence_enabled`.
**Raison :** trois surfaces orthogonales doivent pouvoir être activées indépendamment :
- `body_assessment_enabled` → Manual Body Profile (`/body`)
- `body_intelligence_enabled` → Body Intelligence v2 (`/body/intelligence`, snapshot coach)
- `body_capture_quality_enabled` → capture caméra + MediaPipe (`/body/capture`)
On doit pouvoir activer le profil manuel sans caméra, et tester la capture sans exposer le profil. Même discipline que `Sb_31.X` (router-level gate → 404 avant auth).

### D-6 — Données : rien n'est persisté ✅
**Décision :** **aucune** image stockée, **aucune** vidéo stockée, **landmarks NON persistés** en MVP. Seuls des **statuts de qualité éphémères** vivent côté navigateur (state en mémoire JS), jamais envoyés au serveur ni écrits sur disque.
**Conséquence :** pas de table, pas de migration, pas de champ DB pour ce module au MVP. (Une éventuelle « mesure confirmée » issue d'une capture relèverait d'un lot ultérieur — hors scope ici.)

### D-7 — Consentement caméra explicite ✅
**Décision :** permission caméra demandée **explicitement** via une UI claire **avant** `getUserMedia`. Texte : finalité « aide au cadrage », non médical, annulable à tout moment (kill switch qui coupe le flux). Le consentement caméra est **distinct** de `consent_body_measurements` (privacy model). Aucun usage médical, aucune conservation.

### D-8 — UX mobile-first ✅
**Décision :** utilisable à une main, feedback immédiat, messages courts, sans jargon, **sans jugement corporel**. Un seul statut « actif » à la fois, gros texte lisible, bouton stop visible.

---

## 4. Signaux de qualité (aide à la capture, jamais évaluation du corps)

Statuts éphémères côté navigateur. Chaque statut = `key` + message utilisateur court + (optionnel) consigne d'action.

| `key` | Détecté via | Message utilisateur (exemples) |
|---|---|---|
| `camera_unavailable` | pas de `getUserMedia` / pas de caméra | « Caméra indisponible sur cet appareil. » |
| `permission_denied` | promesse `getUserMedia` rejetée | « Autorise la caméra pour continuer. » |
| `no_person` | 0 pose détectée | « Place-toi devant la caméra. » |
| `multiple_persons` | >1 pose détectée | « Une seule personne doit être visible. » |
| `partially_out_of_frame` | landmarks clés hors [0,1] | « Recule légèrement pour voir tout le corps. » |
| `too_close` | bounding box landmarks trop grande | « Recule un peu. » |
| `too_far` | bounding box trop petite | « Rapproche-toi un peu. » |
| `low_light` | luminance moyenne frame faible | « La lumière est trop faible. » |
| `blur_or_motion` | variance inter-frames élevée | « Reste immobile deux secondes. » |
| `unstable_pose` | jitter landmarks élevé | « Stabilise la position. » |
| `wrong_orientation` | axe épaules/hanches incohérent avec front/side attendu | « Tourne-toi face à la caméra. » |
| `quality_ok` | tous les critères satisfaits N frames consécutives | « Cadrage correct. » |

**Wording — règles :**
- ✅ Autorisé : « Recule légèrement pour voir tout le corps. », « La lumière est trop faible. », « Reste immobile deux secondes. », « Une seule personne doit être visible. »
- ❌ Interdit : « Mauvaise posture. », « Morphologie défavorable. », « Taux de gras estimé. », « Score corporel faible. », tout diagnostic / body-fat / morphotype-vérité / jugement.
- Garde applicative (future) : réutiliser un set `FORBIDDEN_WORDING` (cf. `body_profile`) testé.
- Les seuils (trop près/loin, luminance, jitter) sont des **heuristiques de cadrage** sur les landmarks/frame, jamais des mesures corporelles confirmées.

---

## 5. Découpe build future (à NE PAS exécuter ici)

Chaque lot est **flag-gaté** (`BODY_CAPTURE_QUALITY_ENABLED=false` par défaut), router-level 404 avant auth, non exposé par défaut.

| Lot | Scope | Garde-fous |
|---|---|---|
| **Sb Body 02.1** | Flag `body_capture_quality_enabled` + route coquille `/body/capture` (SSR, **sans caméra**) + gate router-level (404 avant auth) | 0 caméra, 0 MediaPipe, 0 JS d'inférence |
| **Sb Body 02.2** | UI caméra locale : permission explicite + preview `getUserMedia` + **kill switch**, **sans MediaPipe** | 0 upload, 0 stockage, flux coupé à l'arrêt |
| **Sb Body 02.3** | MediaPipe Pose Landmarker **client-side** (vendored wasm+modèle, web worker), **qualité éphémère uniquement** ; élargissement CSP scopé (`wasm-unsafe-eval`, `worker-src 'self'`) | 0 persistance image/vidéo/landmark, 0 CDN, 0 provider externe |
| **Sb Body 02.4** | Hardening mobile / perf (p95, throttle frames) / privacy (revue CSP, teardown flux) | pas de régression mode séance |
| **Sb Body 02.R** | Recette privée opérateur (flag ON temporaire, test caméra, flag OFF) | comme `Sb Body 01.R` ; aucune donnée conservée |

**Dépendances :** 02.1 → 02.2 → 02.3 → 02.4 → 02.R, séquentiel. `Sb Body 02.3` est le seul lot qui ajoute une dépendance JS (`@mediapipe/tasks-vision`, vendored) et touche la CSP — à isoler et flag-gater.

---

## 6. Tests à spécifier pour les builds futurs

**Flag OFF (`BODY_CAPTURE_QUALITY_ENABLED=false`) :**
- `/body/capture` (et sous-routes) → **404 avant auth** (anonyme ET authentifié) ;
- aucun lien/nav vers la capture visible ;
- aucune ressource MediaPipe chargée (pas de `<script>`/wasm/worker capture sur les pages).

**Flag ON :**
- anonyme `/body/capture` → **303 login** ;
- authentifié `/body/capture` → page accessible (coquille puis caméra selon lot).

**Privacy :**
- aucun upload image (pas de requête `POST` avec payload image) ;
- aucun fichier image/vidéo écrit côté serveur ;
- aucun landmark persisté (ni DB, ni fichier) ;
- aucun provider externe appelé sans décision explicite (CSP `connect-src 'self'`).

**UI :**
- états `permission_denied` et `camera_unavailable` rendus proprement ;
- responsive mobile (≤ 360px) ;
- messages **non médicaux** (garde wording testée) ;
- kill switch coupe effectivement le flux (`MediaStreamTrack.stop()`).

**Non-régression :**
- `/body` (#17) et `/body/intelligence` (#19) inchangés ;
- mode séance inchangé ;
- CSP : les pages hors-capture conservent la CSP stricte (l'élargissement ne s'applique qu'à la surface capture ou reste minimal et documenté).

---

## 7. Privacy / consentement (rappel)

- Permission caméra **explicite**, finalité « aide au cadrage » non médicale, **annulable** (kill switch).
- **Rien n'est persisté** : pas d'image, pas de vidéo, pas de landmark. Statuts qualité éphémères en mémoire navigateur uniquement.
- Pas de provider externe, pas de Bodygram, pas d'upload.
- Consentement caméra distinct des consentements measurements/provider (privacy model §2).
- Aucune inférence de caractéristique protégée, aucun body-fat, aucun morphotype-vérité.

---

## 8. Ce qui ne doit PAS être codé maintenant

❌ route, template, JS, CSS · ❌ MediaPipe installé / dépendance / pin de version · ❌ Bodygram / provider · ❌ photo/vidéo/landmark upload ou stockage · ❌ migration / DB · ❌ changement CSP / `.env*` / `requirements.txt` / `pyproject.toml` · ❌ déploiement · ❌ ouverture de `Sb Body 02` build. Seuls livrables : cette spec (+ registry, + rapport optionnel).

---

## 9. Acceptance criteria
- [ ] Spec client-side-only, vendored (pas de CDN), justifiée vs CSP/privacy/repro.
- [ ] Flag dédié `BODY_CAPTURE_QUALITY_ENABLED` spécifié, distinct des deux autres flags Body.
- [ ] Web worker recommandé (sourcé : main-thread blocking officiel).
- [ ] Aucune persistance image/vidéo/landmark ; statuts éphémères uniquement.
- [ ] Consentement caméra explicite + kill switch.
- [ ] Signaux de qualité = aide à la capture, wording non médical (autorisé/interdit listés).
- [ ] Découpe build 02.1→02.R, chaque lot flag-gaté.
- [ ] Tests futurs listés (flag off/on, privacy, UI, non-régression).
- [ ] 0 code applicatif, reviewable sans exécuter l'app.

## 10. Rejection criteria
- [ ] Du code/route/JS/CSS/migration/dépendance est ajouté.
- [ ] MediaPipe/Bodygram installé ou pinné.
- [ ] CDN recommandé sans analyse CSP/privacy, ou recommandé tout court sans justification.
- [ ] Persistance image/vidéo/landmark proposée au MVP.
- [ ] Diagnostic médical / body-fat / morphotype-vérité / wording de jugement.
- [ ] Flag réutilisant `BODY_ASSESSMENT_ENABLED` ou `BODY_INTELLIGENCE_ENABLED`.
- [ ] Déploiement ou ouverture de build dans ce sprint.

## 11. Questions ouvertes
| OQ | Question | À trancher en |
|---|---|---|
| OQ-1 | Variante modèle (lite/full/heavy) selon perf device réel ? | `Sb Body 02.3` |
| OQ-2 | Pin de version `@mediapipe/tasks-vision` + intégrité (hash) ? | `Sb Body 02.3` |
| OQ-3 | Portée exacte de l'élargissement CSP (global vs par-route capture) ? | `Sb Body 02.3` / 02.4 |
| OQ-4 | Front-only vs front+side guidé (orientation) au MVP capture ? | `Sb Body 02.2` |
| OQ-5 | Délégué GPU vs CPU sur web (non détaillé par la doc) ? | `Sb Body 02.3` |
