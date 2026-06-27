# SPIGNOS — Sb Body 01 Manual Body Profile (Build Spec)

**Spec amont :** `Sx Body 01` (`SPIGNOS_BODY_SIGNAL_MODEL_SPEC.md` + `SPIGNOS_BODY_PRIVACY_AND_CONSENT_SPEC.md`)
**Sprint de build cible :** `Sb Body 01 — Manual Body Profile`
**Branche de build future :** `sb-body-01-manual-profile`
**Type de CE document :** SPEC-ONLY (préparation de build). **0 runtime, 0 migration, 0 dépendance ici.**

> Ce document **prépare** le build. Il n'autorise pas encore à coder. Le build `Sb Body 01` ne s'ouvre qu'**après** verrouillage de `Sx Body 01` (mesures MVP, tables futures, consentement, suppression, feature flags, règles de recommandation, versionnement moteur, tests d'acceptance).

---

## 0. Contrat spec-driven (gabarit réutilisable pour tous les `Sb Body *`)

| # | Champ | Valeur pour `Sb Body 01` |
|---|---|---|
| 1 | **Context** | Premier build du module : profil corporel **manuel**, sous feature flag, sans photo/AI/provider. |
| 2 | **Existing repo constraints** | FastAPI SSR/Jinja2/SQLite/Alembic ; **ADD COLUMN ONLY** + snapshot + drift guard + roundtrip ; ownership (`user_id` CASCADE) ; ruff budget verrouillé ; deploy manuel + smoke. `body_measurements` & `users.height_cm` existent ; route `/physique` & `app/services/measurements.py` existent ; export existant. |
| 3 | **Branch name** | `sb-body-01-manual-profile` |
| 4 | **Strict scope** | Mesures manuelles MVP, consentement `consent_body_measurements`, suppression + export, ratios MVP **lecture seule** (affichage), feature flag. **Pas** de reco engine complet (différé `Sb Body 04`), **pas** de photo/provider. |
| 5 | **Files allowed** | `app/body_assessment/**`, `app/templates/body_assessment/**`, additions ciblées dans `app/models/measurement.py` (colonnes additives), `app/routers/` (nouveau router body) ou extension `pages.py`, `app/config.py` (flag), `migrations/versions/*` (1 migration additive), `tests/**`. |
| 6 | **Files forbidden** | toute intégration provider, MediaPipe, Bodygram ; `requirements.txt`/`pyproject.toml` ; `.env*` versionné ; modification du **mode séance** (`session_detail`, `session_focus`, overload). |
| 7 | **Required inspection** | `app/models/measurement.py`, `app/models/user.py`, `app/routers/pages.py` (`/physique`), `app/services/measurements.py`, `app/routers/export.py`, `physique.html`, migrations récentes (pattern snapshot/roundtrip). |
| 8 | **Deliverables** | cf. §1–§6 ci-dessous + sprint report `SPRINT_Sb_Body_01_*_REPORT.md`. |
| 9 | **Data model impact** | cf. §1 (tables/colonnes probables — additif). |
| 10 | **Privacy impact** | cf. `PRIVACY_AND_CONSENT_SPEC` §11 (surface MVP : consentement mesures + suppression + export + minimisation). |
| 11 | **Tests / checks** | cf. §4 + CI 3/3 (ruff/bandit, tests, migration roundtrip). |
| 12 | **Acceptance criteria** | cf. §7. |
| 13 | **Rejection criteria** | cf. §8. |
| 14 | **Handoff report** | sprint report + mise à jour `SPEC_REGISTRY.md`. |

---

## 1. Tables / colonnes probables

> **ADD COLUMN ONLY.** Réutiliser au maximum, ajouter en additif. Une seule migration en vol.

**Réutilisé (aucune nouvelle table) :**
- `body_measurements` (existe) — mesures confirmées.
- `users.height_cm` (existe) — taille.

**Colonnes additives sur `body_measurements` (Float nullable) :**
| Colonne | Raison |
|---|---|
| `shoulder_width_cm` | input MVP V-taper (manquant) |
| `calf_cm_left` | latéralisation mollet (existant `calf_cm` = single, conservé back-compat) |
| `calf_cm_right` | idem |

**Nouvelles tables probables (additif, à confimer en build) :**
| Table | Rôle | États de signal |
|---|---|---|
| `body_consents` | consentements granulaires (type, version texte, accordé/retiré, horodatage) | métadonnée légale |
| `body_recommendations` *(optionnel MVP, sinon `Sb Body 04`)* | recos générées + version + rationale + accepted/ignored | `generated/accepted/ignored_recommendation` |

> **Décision MVP recommandée :** `Sb Body 01` crée `body_consents` + colonnes additives. **`body_recommendations` est différé à `Sb Body 04`** (le MVP affiche des ratios, pas encore des recos persistées) — sauf décision opérateur contraire. Les ratios (`derived_ratio`) sont **calculés à la volée** (non matérialisés) au MVP.

---

## 2. Routes probables

> Décision UX (OQ-8) : **page dédiée `/body`** plutôt que surcharger `/physique` / `/dashboard` (isole la surface, réduit le risque de conflit). À confirmer en build.

| Route | Méthode | Rôle | Garde |
|---|---|---|---|
| `/body` | GET | synthèse profil corporel (dernières mesures + ratios calculés + état confiance) | flag + auth + ownership |
| `/body/measurements/new` | GET/POST | formulaire de saisie mesure manuelle (MVP) | flag + auth + bornes plausibilité |
| `/body/measurements/{id}/edit` | GET/POST | correction d'une mesure | flag + auth + ownership |
| `/body/measurements/{id}/delete` | POST | suppression d'une mesure | flag + auth + ownership |
| `/body/consent` | GET/POST | gestion `consent_body_measurements` (accord/retrait) | flag + auth |
| `/body/export` | GET | export données corporelles (extension export existant) | flag + auth |

> Réutiliser autant que possible `/physique` + `app/services/measurements.py` si l'opérateur préfère ne pas créer `/body` ; tranché en build.

---

## 3. Templates probables

`app/templates/body_assessment/` :
- `body_overview.html` — synthèse (mesures récentes, ratios, badges de confiance, disclaimers non médicaux).
- `measurement_form.html` — saisie/correction (mobile-first, champs optionnels, bornes).
- `consent.html` — consentement explicite (case non pré-cochée, finalité claire).
- partials : `_ratio_card.html`, `_confidence_badge.html`, `_proxy_flag.html`.

**Contraintes UX :** mobile-first, SSR, **hors mode séance**, aucun score humiliant, ratios drillables (formule + inputs visibles).

---

## 4. Tests probables

| Catégorie | Cas |
|---|---|
| Modèle/migration | migration additive applicable + **roundtrip** (snapshot) ; colonnes nullable ; pas de breaking change. |
| Bornes de plausibilité | rejet/clamp des valeurs hors min/max (§ signal spec §2). |
| Ratios (purs) | formules correctes ; **fallback** si input manquant ; `is_proxy` correct ; pas de calcul sous le seuil de confiance. |
| Confidence policy | pas de tendance < 3 points ; ratio non affiché si input requis absent. |
| Consentement | saisie bloquée si `consent_body_measurements` absent ; retrait stoppe + propose suppression. |
| Ownership | un user ne lit/édite/supprime que ses mesures ; 404/403 sinon. |
| Suppression | hard delete ; cohérence ratios dérivés. |
| Export | contient mesures + consentement, pas d'autre user. |
| Feature flag | flag OFF ⇒ routes inactives / 404 ; aucun impact sur le reste de l'app. |
| Wording | absence de termes médicaux interdits (test de garde linguistique). |
| Mode séance intact | `session_detail` / `session_focus` non modifiés (test de non-régression). |

Cible CI : **3/3 jobs verts** (ruff/bandit + tests + migration check), conforme à la discipline `Sb_*`.

---

## 5. Migrations probables

- **Une** migration additive : `ADD COLUMN shoulder_width_cm, calf_cm_left, calf_cm_right` sur `body_measurements` + `CREATE TABLE body_consents`.
- Snapshot + linter + roundtrip (contrat SPIGNOS).
- **Sérialisation** : ne pas ouvrir cette migration pendant une autre migration en vol (ex. cycle `Sx_30`). Rebaser sur HEAD à jour avant build.

## 6. Feature flags probables

```text
BODY_ASSESSMENT_ENABLED=false   # gate global du module ; OFF par défaut
```
- Convention `app/config.py` : `body_assessment_enabled: bool = Field(default=False)`.
- `BODY_PHOTO_CAPTURE_ENABLED` / `BODY_PROVIDER_BODYGRAM_ENABLED` **non** créés en `Sb Body 01` (lots ultérieurs).
- Flag OFF ⇒ 0 route exposée, 0 impact prod.

---

## 6bis. Non-goals du build `Sb Body 01`

- ❌ photo / image analysis / MediaPipe.
- ❌ provider externe / Bodygram.
- ❌ moteur de recommandation complet (différé `Sb Body 04`) — au MVP : ratios + (optionnel) reco statique non persistée.
- ❌ modification automatique du programme.
- ❌ liaison graphe de substitution (différé `Sb Body 05`).
- ❌ modification du mode séance.
- ❌ diagnostic médical / % body fat / score humiliant / caractéristique protégée.

---

## 7. Acceptance criteria (`Sb Body 01`)
- [ ] Mesures MVP saisissables/corrigibles/supprimables, sous flag, mobile-first.
- [ ] Colonnes additives + `body_consents` via **une** migration additive avec roundtrip vert.
- [ ] `consent_body_measurements` requis avant saisie ; retrait + suppression fonctionnels.
- [ ] Export des données corporelles disponible (ownership respecté).
- [ ] Ratios MVP affichés avec confiance + fallback + `is_proxy`, sans wording médical.
- [ ] Flag OFF ⇒ aucun impact ; mode séance intact (non-régression).
- [ ] CI 3/3 verte ; `SPEC_REGISTRY.md` mis à jour.

## 8. Rejection criteria (`Sb Body 01`)
- [ ] Photo/provider/dépendance ajoutés.
- [ ] Migration non additive / renommage / drop destructif.
- [ ] Saisie possible sans consentement.
- [ ] Suppression ou export absents/cassés.
- [ ] Wording médical / caractéristique protégée / score humiliant.
- [ ] Mode séance modifié.

## 9. Handoff report (de CE document)
- **Statut :** préparation de build `Sb Body 01` — **build non ouvert**.
- **Pré-requis de passage `Sx Body 01 → Sb Body 01` :** mesures MVP ✅, tables futures ✅, consentement ✅, suppression ✅, feature flags ✅, règles de recommandation ✅ (différé partiel), versionnement moteur ✅, tests d'acceptance ✅ — tous spécifiés ici/spec jumelle. Verrouillage opérateur requis.
- **Runtime :** 0. **Migration :** 0. **Dépendance :** 0 (dans ce sprint spec).
