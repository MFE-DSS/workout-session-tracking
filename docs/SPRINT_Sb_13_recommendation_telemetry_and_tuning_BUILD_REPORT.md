# Sprint Sb_13 Build Report — Recommendation Telemetry & Tuning

**Date :** 2026-04-21
**Type :** Build chirurgical — implémente §M de `SPIGNOS_RECOMMENDATION_CALIBRATION_SPEC_v1.md`
**Prérequis :** Sx_13 validée, Sb_12 livré (moteur en place), micro-dogfooding Sb_12 OK
**Successeur :** passe dogfooding 7 jours (§E de la spec Sx_13) puis arbitrage Sx_11b / Sx_13.1

---

## 1. Objectif

Ajouter l'instrumentation minimale qui permettra de calibrer le moteur de recommandation à partir d'un usage réel. Une seule nouvelle donnée (`creation_source`), un script CLI d'observation, aucun changement du moteur lui-même. Pas de bouton utilisateur, pas de dashboard admin, pas de JavaScript.

---

## 2. Fichiers modifiés

| Fichier | Type | Nature |
|---------|------|--------|
| `migrations/versions/20260421_add_creation_source.py` | **New** | Migration additive nullable sur `workout_sessions` |
| `app/models/session.py` | Modify | Ajout du champ `creation_source: Optional[str]` (String 16) |
| `app/routers/sessions.py` | Modify | `create_session` accepte et persiste `creation_source` via whitelist, silencieux si invalide |
| `app/templates/_partials/next_session_reco.html` | Modify | Hidden `reco_top` sur CTA principal ; alternatives deviennent des mini-forms POST porteurs de `reco_alt` |
| `app/templates/launcher.html` | Modify | Hidden `launcher` dans le form de démarrage step 3 |
| `app/templates/library.html` | Modify | Hidden `library` dans le form de démarrage |
| `app/static/css/app.css` | Modify | `.reco-next__alt-form` + reset bouton pour conserver l'apparence de lien |
| `scripts/reco_calibration_report.py` | **New** | CLI — 4 métriques + top phrases sur fenêtre configurable |
| `tests/test_recommendation_telemetry.py` | **New** | 10 tests (persistance + whitelist + rendu hidden inputs) |
| `tests/test_reco_calibration_report.py` | **New** | 3 tests (empty run, comptage sources, section phrases) |
| `docs/SPRINT_Sb_13_recommendation_telemetry_and_tuning_BUILD_REPORT.md` | **New** | Ce rapport |

**Zéro JS. Zéro moteur modifié. Zéro nouvelle route. Migration strictement additive (nullable).**

---

## 3. Décisions d'implémentation

### D1 — Whitelist centralisée dans le router

La validation de `creation_source` vit dans `sessions.py` (`_CREATION_SOURCE_ALLOWED`), pas dans le modèle. Une valeur invalide est **silencieusement** écrasée en `NULL`. Jamais de 400/422 pour un champ analytique — le POST principal (`template_slug`) doit toujours réussir.

### D2 — Alternatives deviennent des mini-forms POST

L'ancien lien `<a href="/launcher?preselect=...">` devenait inutile : impossible de tagger le démarrage comme `reco_alt` sans rebondir sur le launcher. J'ai remplacé par un **petit `<form>` POST direct** par alternative, avec boutons stylés comme des liens (reset `<button>` + `text-align:left`). L'utilisateur voit exactement la même chose, le backend reçoit directement `creation_source=reco_alt`.

Bénéfice : un clic = une session créée avec la bonne provenance, pas de redirection intermédiaire à instrumenter.

### D3 — Script CLI, pas page admin

Aligné avec `catalog_qa.py` et `machine_atlas_qa.py`. Un simple `python scripts/reco_calibration_report.py --days 7` sort un rapport texte. Pas de nouveau endpoint, pas de sécurité admin à ajouter, pas de pollution du cockpit utilisateur.

### D4 — Phrases recalculées, pas persistées

La spec §J.4 assumait explicitement la possibilité d'un léger écart entre la phrase affichée et celle recalculée. J'ai tenu cette position : pour chaque session créée en `reco_top`, le script réappelle `recommend_next_session` à l'horodatage `started_at` et lit la phrase. Zéro nouveau champ DB, zéro surface d'écriture supplémentaire.

### D5 — Migration nullable

La colonne `creation_source` est nullable. Les séances pré-Sb_13 restent `NULL` et sont comptées comme « unknown source » dans le rapport. Pas de backfill, pas de guess. Le signal de la calibration s'accumule à partir de la date de déploiement.

### D6 — Tests du script via subprocess

`test_reco_calibration_report.py` lance le script comme un process séparé (comme l'aurait fait un CI), avec `DATABASE_URL` héritée du fixture. Cela garantit que le script est fonctionnel tel qu'un humain l'exécuterait, pas uniquement via import pytest-monkeypatché.

---

## 4. Comment le champ `creation_source` est peuplé

### 4.1 Sources

| Valeur | Surface d'origine | Template |
|--------|-------------------|----------|
| `reco_top` | Bloc « Prochaine séance suggérée », CTA principal | `_partials/next_session_reco.html` |
| `reco_alt` | Bloc « Prochaine séance suggérée », lien alternatif (form POST maintenant) | `_partials/next_session_reco.html` |
| `launcher` | Picker 3-étapes step 3, bouton « Démarrer » | `launcher.html` |
| `library` | Page `/library`, bouton « Démarrer » par template card | `library.html` |
| `replay` | Réservée, non utilisée V1 (démarrage automatique depuis un rapport `/done` futur) | — |
| `NULL` | Avant Sb_13, ou valeur invalide soumise (silenciée) | — |

### 4.2 Flux POST

```
<form method="post" action="/sessions">
  <input type="hidden" name="template_slug"     value="push-a">
  <input type="hidden" name="creation_source"   value="reco_top">
  <button type="submit">Démarrer Push A →</button>
</form>
```

Router :

```python
if creation_source in _CREATION_SOURCE_ALLOWED:
    session.creation_source = creation_source
# sinon : session.creation_source reste NULL (défaut ORM)
```

---

## 5. Comment le rapport est produit

`python scripts/reco_calibration_report.py [--days N] [--user-id X] [--phrase-top K]`

Sections rendues :

1. **Header** — fenêtre, total sessions, known/unknown source count.
2. **Breakdown par source** — compte + pourcentage relatif au total known.
3. **Indicateurs clés** — `reco_acceptance_rate`, `alt_click_rate`, `bypass_rate` avec cibles.
4. **Top phrases** (uniquement si `--user-id` fourni) — échantillon des K dernières sessions `reco_top` ; pour chacune, réappel du moteur à l'horodatage de la séance pour reconstruire la phrase ; agrégation et flag ⚠ sur toute phrase apparaissant ≥ 3 fois.

Exemple de sortie sur une DB vide :

```
SPIGNOS — Reco calibration report
================================================
Window                : 7 day(s)
Sessions (window)     : 0
  with known source   : 0
  with unknown source : 0  (pre-Sb_13 or invalid)

Creation source breakdown
------------------------------------------------
  reco_top  :    0  (n/a of known)
  reco_alt  :    0  (n/a of known)
  launcher  :    0  (n/a of known)
  library   :    0  (n/a of known)

Key indicators (vs known-source sessions)
------------------------------------------------
  reco_acceptance_rate : n/a  (target > 40%)
  alt_click_rate       : n/a  (target 10-25%)
  bypass_rate          : n/a  (target < 30%)

Top phrases sampling skipped (requires --user-id to be meaningful)
```

Exit code : toujours 0. Script observationnel, pas un pass/fail.

---

## 6. Tests ajoutés

### 6.1 Telemetry — `tests/test_recommendation_telemetry.py` (10)

- `test_creation_source_reco_top_persists` — enum valide persisté.
- `test_creation_source_reco_alt_persists`
- `test_creation_source_launcher_persists`
- `test_creation_source_library_persists`
- `test_invalid_creation_source_stored_as_null` — chaîne hors whitelist → NULL, pas de 400.
- `test_absent_creation_source_is_null` — backward-compat pour callers anciens.
- `test_home_partial_has_reco_top_hidden_input` — rendu du hidden input dans le CTA principal.
- `test_home_partial_alternatives_carry_reco_alt` — présence du `reco_alt` dès que les alternatives s'affichent.
- `test_launcher_step3_form_carries_launcher_source` — hidden `launcher` bien injecté step 3.
- `test_library_form_carries_library_source`

### 6.2 Script CLI — `tests/test_reco_calibration_report.py` (3)

- `test_script_runs_on_empty_db` — exit 0, sections attendues.
- `test_script_counts_creation_sources` — 4 sessions seedées avec sources mixtes → comptes corrects dans la sortie.
- `test_script_with_user_filter_mentions_phrases_section` — `--user-id` active la section top phrases.

### 6.3 Régression

- Full suite : **696 passed** (vs 683 avant Sb_13, +13).
- Aucune régression observée.
- Tests surface Sb_12 encore verts malgré le refacto lien → form POST pour les alternatives.
- `catalog_qa` PASS, `machine_atlas_qa` PASS.

---

## 7. État final de la suite

```
tests : 696 passed en 3m35s
catalog_qa.py : PASS (16 templates, 98 exercises)
machine_atlas_qa.py : PASS (8 familles, 29 machines)
alembic : head = c3d5f1e82a04 (nouvelle migration appliquée localement)
```

---

## 8. Comment lancer la passe de calibration

Rappel §J.5 de la spec Sx_13 — séquence après déploiement Sb_13 :

1. **J+0** — déployer Sb_13 (migration alembic appliquée, scripts à jour).
2. **J+0 → J+7** — usage normal, une note rapide chaque jour dans `docs/DOGFOOD_SB_12_NOTES.md` (crée-le).
3. **J+7** — exécuter le rapport :
   ```bash
   python scripts/reco_calibration_report.py --days 7 --user-id <YOUR_USER_ID>
   ```
4. Lire les 4 indicateurs + les phrases répétées.
5. Décider **au plus 2 modifications** de constantes dans `app/services/recommendation.py` (priorité P0/P1 §4 du rapport Sx_13).
6. Commiter les nouvelles valeurs, relancer la suite (elle doit rester verte), re-déployer.
7. **J+14** — nouveau rapport pour vérifier l'effet des ajustements.

**Règle stricte :** si la calibration produit 2 passes consécutives sans modification de constante nécessaire, la reco est considérée **stable**. On peut alors ouvrir un chantier produit extension (Sx_11b programme-builder prioritairement).

---

## 9. Limites assumées

1. **Volume utilisateur V1 = 1** — les pourcentages sont qualitatifs, pas statistiquement significatifs. Traiter les seuils (> 40 %, < 30 %) comme des garde-fous, pas comme des KPIs rigoureux.
2. **Phrase recalculée post-hoc peut diverger** de la phrase affichée si l'historique a bougé entre le rendu et le POST. Acceptable pour calibration qualitative, réversible V2 via persistance d'un champ dédié.
3. **Pas de tracking JS** — donc pas de mesure du taux d'ouverture du `<details>` alternatives. On se repose sur `alt_click_rate` (clic effectif qui démarre une séance).
4. **Pas de bouton « pas cette suggestion »** V1.5 — si le bypass ne suffit pas à diagnostiquer après 2 passes dogfooding, ajouter H2 de la spec.
5. **Script CLI ne sait que lire** — pas de mutation, pas d'ajustement automatique. Toute décision de tuning reste humaine, documentée par commit.
6. **L'agrégation `phrase_repetition_rate`** dépend de la stabilité du moteur entre déploiements — si les constantes changent pendant la fenêtre observée, l'agrégation mélange deux versions. Éviter de tuner en pleine passe.
7. **Pas de séparation par type de template** — le bypass_rate mélange les bypass « je veux Push » et « je veux cardio ». Suffisant V1, affinable V2 en segmentant par `session_kind`.
8. **Les sessions pré-Sb_13** resteront indéfiniment `NULL` — pas de backfill. C'est volontaire (rien à deviner sur leur provenance réelle).

---

## 10. Recommandation du prochain sprint de spec

**Attendre la passe de dogfooding 7j avant d'ouvrir un nouveau sprint de spec.**

Trois chemins possibles après la passe :

- **Chemin A (reco stable, calibration OK)** → **Sx_11b — Programme-builder utilisateur** (15–20h build). C'était le candidat primaire de Sx_12 §8. Les signaux analytiques (zones, kinds, atlas) s'appliquent désormais au catalogue mais devront continuer à fonctionner si l'utilisateur ajoute ses propres templates.
- **Chemin B (reco encore bruyante)** → **Sx_13.1 — Cycle calibration 2** (~2h spec + 2h build tuning). Un deuxième passage léger sur les constantes, éventuellement avec introduction de H2 (bouton « pas cette suggestion ») si le signal passif n'a pas suffi.
- **Chemin C (reco excellente, appétit pour autre sujet)** → **Sx_11c — Squad / social v2** (4h spec, 8–12h build). Moins urgent mais cohérent si la trajectoire produit bascule vers l'engagement/retention.

**Recommandation par défaut :** Chemin A après passe dogfooding positive. Programme-builder est le prochain saut de valeur utilisateur logique maintenant que la couche reco est à la fois buildée et instrumentée.

---

## 11. Synthèse exécutive

- 1 migration additive (`creation_source String(16) NULL`), 1 champ modèle, whitelist de 5 valeurs côté router avec silent drop des valeurs invalides.
- 3 templates enrichis de hidden inputs : CTA reco top (`reco_top`), alternatives passées en forms POST (`reco_alt`), picker launcher step 3 (`launcher`), library (`library`).
- Script CLI `scripts/reco_calibration_report.py` produit 4 métriques sur fenêtre configurable + top phrases (avec `--user-id`). Aligné sur `catalog_qa.py` / `machine_atlas_qa.py`.
- 13 nouveaux tests (10 telemetry + 3 script), full suite **696 passed** (+13).
- **Zéro JS, zéro refonte, zéro dashboard admin, zéro nouvelle route.**
- Prêt pour passe dogfooding 7j avant toute décision d'extension produit.
