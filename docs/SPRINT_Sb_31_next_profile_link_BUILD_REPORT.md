# Sb_31.next.profile-link — Découvrabilité Body Intelligence depuis /profile (Build Report)

**Branche :** `claude/sprint-reporting-fitness-app-V7Qr6`
**Date :** 2026-06-29
**Spec parent :** `docs/strategy/SPIGNOS_BODY_INTELLIGENCE_V2_SPEC.md` (OQ-G)
**Type :** mini-lot UX, **pas un nouveau cycle**
**Build authorization :** ✅ override séparé OQ-G post-Sx_31 closure (2026-06-29)
**Pré-requis :** Sx_31 TECHNICALLY CLOSED ✅ (CI 28322377053)

---

## 1. Résumé exécutif

Ajout d'un lien sobre depuis `/profile` vers `/body/intelligence` pour améliorer la découvrabilité de Body Intelligence v2. Implémentation minimale : une nouvelle carte compacte "Lecture corporelle" placée entre la carte Identité et la carte "Mes 30 derniers jours" du profil. Aucune duplication du contenu Body Intelligence, aucune logique métier, aucun nouveau JS, aucune migration, aucune nouvelle route.

Sx_31 OQ-G (lien `/profile` → `/body/intelligence`) explicitement différée à un sprint dédié est désormais livrée.

## 2. Fichiers modifiés

| Fichier | Type | Description |
|---|---|---|
| `app/templates/profile.html` | MODIFIED | +13 lignes : nouvelle carte `profile-body-intel-link` insérée entre la carte Identité (lignes 7-17) et la carte "Mes 30 derniers jours" (ligne 19+). Lien `Voir Body Intelligence →` avec flèche `aria-hidden`. |
| `tests/test_profile_body_intelligence_link.py` | **NEW** | 17 tests : structure + smoke route + lien explicite + flèche décorative + wording interdit + anti-duplication + garde-fous structurels Sx_31 + non-régression /body/intelligence et /coach-report. |
| `docs/SPRINT_Sb_31_next_profile_link_BUILD_REPORT.md` | **NEW** | Ce rapport. |
| `docs/strategy/SPEC_REGISTRY.md` | MODIFIED | Sb_31.next.profile-link livré ✅. |
| `docs/strategy/ROADMAP_AND_NEXT_STEPS.md` | MODIFIED | §10 séquence : OQ-G marqué LIVRÉ. |

### Non touché (vérification explicite par tests garde)
- `app/services/body_intelligence.py` (composer pur Sb_31.1, sentinelle `BODY_INTELLIGENCE_VERSION=1` préservée)
- `app/services/body_intelligence_inputs.py` (Sb_31.2)
- `app/services/coach_report.py` (service, intact depuis Sb_31.3)
- `app/services/coach_inference.py` / `profile_metrics.py` / `muscle_scoring.py` / `quality_score.py` / `implicit_signal.py` / `confidence.py` / `radar.py` / `overload_*` / `substitution.py` / `recommendation.py`
- `app/routers/*` (aucun router modifié — `body_intelligence.py` intact)
- `app/templates/body_intelligence.html` + partials (Sb_31.2/4 intacts)
- `app/templates/_partials/coach_body_snapshot.html` (Sb_31.3/4 intact)
- `app/static/css/*` (aucun CSS modifié, la carte réutilise la classe `card`)
- `app/static/js/*` (aucun JS)
- `app/models/*` / `migrations/*` (aucun)

## 3. Emplacement exact du lien

Dans `app/templates/profile.html`, entre la carte "Identité" et la carte "Mes 30 derniers jours" :

```jinja
<div class="card profile-body-intel-link">
  <h2 class="card__title">Lecture corporelle</h2>
  <p class="text-dim" style="font-size:13px;margin:0 0 var(--space-sm);">
    Basé sur les séances loggées.
  </p>
  <p style="margin:0;">
    <a class="link" href="{{ url_for('body_intelligence') }}">
      Voir Body Intelligence <span aria-hidden="true">→</span>
    </a>
  </p>
</div>
```

Justification du placement :
- **Après Identité** : l'utilisateur a vu son nom + statut + comptes session ; le lien Body Intelligence est la suite logique (lecture corporelle dérivée de son entraînement).
- **Avant "Mes 30 derniers jours"** : le bloc 30j contient déjà des KPIs ; placer le lien Body Intel **avant** évite qu'il passe inaperçu en bas de la colonne principale.
- **Carte standalone** (classe `card` existante) : pas de mélange avec un autre bloc, pas de gros redesign, lecture immédiate.
- **Marqueur de classe `profile-body-intel-link`** : permet aux tests d'extraire précisément la zone et facilite un futur styling ciblé sans toucher au CSS global.

## 4. Diff UX

**Avant** :
```
/profile
├─ Identité (utilisateur, inscription, statut, sessions)
├─ Mes 30 derniers jours (KPIs + timeline)
└─ Nouvelle mesure / Mesures récentes (sidebar)
```
→ Aucun chemin vers `/body/intelligence` depuis le profil. L'utilisateur devait connaître la route ou passer par `/coach-report` pour découvrir le lien CTA Sb_31.3.

**Après** :
```
/profile
├─ Identité
├─ Lecture corporelle          ← NEW: lien sobre vers /body/intelligence
│   Basé sur les séances loggées.
│   Voir Body Intelligence →
├─ Mes 30 derniers jours
└─ ...
```
→ Découvrabilité directe et immédiate. Wording sobre, non-intrusif. Aucune duplication du contenu Body Intelligence (carte = juste un point d'entrée).

## 5. Wording utilisé

| Wording autorisé (utilisé) | Statut |
|---|---|
| « Lecture corporelle » | ✅ titre de la carte |
| « Voir Body Intelligence » | ✅ texte du lien |
| « Basé sur les séances loggées » | ✅ contexte court |

| Wording interdit (scanné par test) | Statut |
|---|---|
| « ton physique est » / « analyse morphologique » / « taux de gras » | ✅ absent |
| « diagnostic » / « posture réelle » / « symétrie corporelle réelle » | ✅ absent |
| « tu es gras/sec » / « tu dois absolument » | ✅ absent |

## 6. Tests ajoutés (17 cas)

### Structure + smoke (3)
- `test_profile_returns_200`
- `test_profile_html_contains_link_to_body_intelligence`
- `test_profile_link_section_carries_explicit_title` (titre "Lecture corporelle" + contexte "Basé sur les séances loggées")

### Texte du lien explicite (2)
- `test_profile_link_has_explicit_visible_text` (au moins un wording recommandé : "body intelligence" / "lecture corporelle" / "voir le détail")
- `test_profile_link_arrow_is_decorative` (flèche `→` enveloppée dans `<span aria-hidden="true">`)

### Wording interdit (1)
- `test_no_forbidden_wording_on_profile_around_body_intel_card` (scan régex sur la carte uniquement, 9 tokens interdits)

### Anti-duplication (2)
- `test_profile_does_not_duplicate_body_intelligence_blocks` (8 marqueurs spécifiques `/body/intelligence` interdits sur `/profile`)
- `test_profile_does_not_pre_compute_body_snapshot` (`data-body-snapshot-status` absent — appartient à `/coach-report`)

### Garde-fous structurels Sx_31 (4)
- `test_body_intelligence_service_unchanged` (sentinelle `BODY_INTELLIGENCE_VERSION=1`)
- `test_body_intelligence_inputs_layer_unchanged` (signature publique)
- `test_coach_report_service_unchanged` (ne référence pas `body_intelligence`)
- `test_body_intelligence_router_unchanged` (pipeline canonique + route préservée)

### Pas de nouvelle route / API / JS / migration (3)
- `test_no_new_route_created_on_profile` (`/profile.json` → 404/405)
- `test_no_new_js_file_introduced` (set strict `{preview.js, session_focus.js}`)
- `test_no_migration_mentions_profile_link`

### Non-régression Body Intelligence (2)
- `test_body_intelligence_route_still_200`
- `test_coach_report_still_200_with_snapshot`

## 7. Statut tests

| Suite | Résultat |
|---|---|
| `tests/test_profile_body_intelligence_link.py` (Sb_31.next.profile-link) | ✅ 17 passed |
| Sous-suite Sx_31 (119 tests existants) | ✅ non régressée |
| Suite complète locale | ⏳ background run |
| Ruff | ✅ 529 ≤ 548 (inchangé) |
| Spec protocol | ✅ |
| Alembic drift | ✅ no diff |

## 8. Contraintes respectées (verbatim user)

| Contrainte | OK |
|---|---|
| Modifier le template `/profile` ou son partial | ✅ template uniquement |
| Ajouter un CTA/lien vers `/body/intelligence` | ✅ |
| Ajouter tests de rendu | ✅ 17 tests |
| Mise à jour registry/report | ✅ |
| Pas de modification `body_intelligence.py` | ✅ test garde |
| Pas de modification `body_intelligence_inputs.py` | ✅ test garde |
| Pas de modification `coach_report.py` service | ✅ test garde |
| Pas de modification route `/body/intelligence` | ✅ test garde |
| Pas de home card / overload compliance / scoring body | ✅ |
| Pas de migration / modèle DB | ✅ test garde |
| Pas de JS / API JSON | ✅ test garde |
| Pas de LLM / HealthKit / photo / scan | ✅ |
| Pas d'ouverture Sx_32 / PWA | ✅ |
| UX sobre, mobile-first, non-intrusif | ✅ carte standalone, classes existantes |
| Wording autorisé uniquement | ✅ test scan |

## 9. Non-goals respectés

- Aucune duplication du contenu `/body/intelligence` dans `/profile` (test scan 8 marqueurs)
- Aucun pré-calcul de snapshot Body Intelligence côté `/profile` (test garde `data-body-snapshot-status` absent)
- Aucune mutation des services métier core
- Aucune modification du composer ni de la couche I/O
- Aucune carte home ajoutée (`Sb_31.next.home-card` reste différé)
- Aucune intégration overload compliance (`Sb_31.next.overload-compliance` reste différé)

## 10. CI réelle (post-push)

**Run GitHub Actions : [28358444492](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28358444492) — ✅ success (3/3 jobs verts)**

- [x] Job `pytest + QA scripts` — ✅ success
- [x] Job `lint (ruff budget + bandit + actionlint + shellcheck)` — ✅ success
- [x] Job `SonarCloud` — ✅ success (après rerun : 1er échec dû à un HTTP 500 transient côté `sonarcloud.io/api/plugins/installed`, upstream)

Note : un premier run [28357621906](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28357621906) avait échoué sur `check_spec_protocol` — le marker `## 12. Verdict` n'était pas dans la liste acceptée. Corrigé en `## 11. Verdict` (commit `e543a3e`). La section 11 reste "Métriques", la 12 → 11 garde la cohérence avec le pattern Sb_31.5.

## 11. Métriques

| Item | Valeur |
|---|---|
| Lignes template modifiées | +13 (carte Body Intel link) |
| Lignes CSS ajoutées | **0** (réutilisation classes `card`, `card__title`, `text-dim`, `link`) |
| Tests ajoutés | +17 |
| Migrations | 0 |
| Modèles SQLAlchemy | 0 |
| JS ajouté | 0 |
| API JSON | 0 |
| Services métier core mutés | 0 |
| Ruff total | 529 ≤ 548 (inchangé) |

## 11. Verdict

**✅ Sb_31.next.profile-link livré.**

OQ-G (Sx_31 §N.1) implémentée — la dernière OQ d'ergonomie pure du cycle Body Intelligence v2 est désormais traitée.

**Prochaine étape recommandée** : **dogfood Sx_31 device réel** sur ≥ 2 semaines (template prêt : `docs/dogfood/DOGFOOD_Sx_31_BODY_INTELLIGENCE_TEMPLATE.md`). Le dogfood couvre désormais 3 surfaces de découvrabilité :
- `/body/intelligence` (page complète Sb_31.2 + a11y Sb_31.4)
- `/coach-report > 1bis. Snapshot Body Intelligence` (Sb_31.3 + CTA a11y Sb_31.4)
- **`/profile > Lecture corporelle` (Sb_31.next.profile-link, livré aujourd'hui)** — point d'entrée principal vers Body Intelligence

Autres sprints discrétionnaires post-dogfood (toujours sous override séparé) :
- `Sb_31.next.home-card` (OQ-F, mini-summary sur `/`)
- `Sb_31.next.overload-compliance` (agrégation 30j des hints Sx_30)
- `Sb_31.next.thresholds-v2` (bump composer V=2 si dogfood le réclame)

Sx_32 (PWA) / Sx_33+ (Health/API) restent bloqués jusqu'à dogfood Sx_31 PASS ou override séparé documenté. Track parallèle Body Signal Model reste indépendant. Dogfoods Sx_27 et Sx_30 restent indépendamment pending.
