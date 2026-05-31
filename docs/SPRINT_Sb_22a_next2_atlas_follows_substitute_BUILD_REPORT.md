# Sprint Sb_22a.next2 Build Report — Atlas suit le réalisé

**Date :** 2026-05-31
**Type :** BUILD CORRECTIF FOCAL — ferme le bug N8 du dogfooding (conseils d'exécution figés sur le prescrit malgré le substitut choisi).
**Prérequis :** Sb_22a.next livré (`63f78e9`), Sb_23 livré (`e99f776`).
**Successeur :** Sx_24 (spec scoring implicite + dépréciation checkbox).

---

## 1. Objectif

Faire en sorte que **la guidance immédiate dans la carte d'exercice suive le réalisé** (= le substitut choisi par l'utilisateur), au lieu de rester figée sur le prescrit. Le prescrit reste visible comme **référence historique/template** via le badge "Substitué : X (prescrit : Y)" déjà en place.

## 2. Diff métier

Avant : quand l'utilisateur substitue "Chest Press machine" par "Développé couché haltères", le panel "**Comment bien exécuter Chest Press machine**" reste affiché avec les cues de la machine prescrite — incohérent avec ce que l'utilisateur va vraiment faire.

Après :
- Si le substitut est référencé dans `machine_atlas.json` (par `name` ou `aliases`), le panel affiche **"Comment bien exécuter Développé couché haltères (substitué)"** avec **ses propres** cues d'exécution + erreurs fréquentes.
- Le badge `(substitué)` en uppercase accent rend le changement visible (UX delta clair).
- Le badge `Substitué : X (prescrit : Y)` reste affiché — la traçabilité prévu/réalisé est préservée.
- Si le substitut n'est **pas** dans l'atlas (cas hors V1 du registre), fallback transparent sur le prescrit — pas de panel vide.

## 3. Surface impactée

| Élément | Avant Sb_22a.next2 | Après Sb_22a.next2 |
|---|---|---|
| Nom dans en-tête de carte | ✅ déjà dynamique (`substituted_name or snapshot`) | inchangé |
| Badge "Substitué : X (prescrit : Y)" | ✅ déjà affiché | inchangé |
| Panel "Comment bien exécuter X" — titre | ❌ nom prescrit | ✅ nom substitut + tag `(substitué)` |
| Panel — execution_cues | ❌ cues du prescrit | ✅ cues du substitut |
| Panel — common_mistakes | ❌ erreurs du prescrit | ✅ erreurs du substitut |
| Panel — load_semantics | ❌ du prescrit | ✅ du substitut |
| Peek cues (Sb_11a — preview prochain exo) | ❌ atlas du prescrit | ✅ atlas du substitut (via la même fonction) |
| Briefing chip (scheme + dernière fois) | ✅ déjà dynamique (le nom n'apparaît pas dans la chip) | inchangé |
| `template_exercise.notes` (notes catalogue prescrites) | non rendu V1 | inchangé (toujours non rendu) |

## 4. Fichiers modifiés

| Fichier | Type | Nature |
|---|---|---|
| `app/services/machine_atlas.py` | Modify | +`get_machine_by_name(name)` (lookup par name + aliases case-insensitive), +`get_for_session_exercise(se)` (priorité au substitut, fallback prescrit). `get_for_template_exercise` inchangé pour compat. |
| `app/routers/sessions.py` | Modify | 1 ligne : `atlas_data[se.id] = machine_atlas.get_for_session_exercise(se)` au lieu de `get_for_template_exercise(se.template_exercise)`. |
| `app/templates/session_detail.html` | Modify | Titre du panel cues affiche `(substitué)` si l'atlas a résolu le substitut. |
| `app/static/css/app.css` | Modify | +`.machine-panel__tag` (~10 lignes) — pastille accent pour le badge "substitué". |
| `tests/test_atlas_follows_substitute.py` | New | 8 tests : prescribed-only / substitute-resolves / case-insensitive / alias / unknown→fallback / None template safe. |
| `docs/SPRINT_Sb_22a_next2_atlas_follows_substitute_BUILD_REPORT.md` | New | Ce rapport. |

**0 modification BD · 0 migration · 0 modèle touché · 0 réécriture historique.**

## 5. Contrats respectés

| Contrat | Vérifié |
|---|---|
| Le prévu reste visible comme référence | Badge "Substitué : X (prescrit : Y)" inchangé ; titre panel affiche `(substitué)` explicite |
| Pas de recalcul historique | `get_for_session_exercise` est read-only, ne touche rien en BD |
| Fallback safe si substitut hors atlas | Test `test_get_for_session_exercise_substitute_not_in_atlas_falls_back` vérifie le fallback prescrit |
| Pas de régression atlas existant | `get_for_template_exercise` inchangé, tous les anciens appels marchent identiquement |
| Lookup case-insensitive + aliases | Tests dédiés (exact / case / alias / inconnu / None) |

## 6. État des tests

```
8 nouveaux tests dans test_atlas_follows_substitute.py — 8/8 verts
801 → 809 tests pass (+8, 0 régression)
catalog_pattern_qa : OK exit 0
```

## 7. Limites assumées

1. **Périmètre atlas V1** — seuls les exos avec entrée dans `data/machine_atlas.json` (~29 machines × 8 familles) ont leurs cues résolues via le substitut. Les substituts hors atlas tombent sur le prescrit (acceptable — c'est ce qu'il y a de mieux).
2. **Alias** — seuls les aliases déjà saisis dans le JSON sont matchés. Pas de fuzzy matching, pas d'analyse lexicale (ex : "Développé couché barre" ne matchera pas si seul "Bench press barre" est listé). À étendre selon retour user.
3. **Pas de migration historique** — les sessions passées sans substitut affichent toujours le prescrit (inchangé). Les sessions avec substitut affichent désormais le substitut pour les cues — c'est une amélioration rétroactive bénigne (pas de réécriture data, juste un autre calcul à la volée au prochain affichage).

## 8. Vérification dogfood ciblée à faire en salle

1. Lance une séance Push A → carte "Incline Smith Press"
2. Drawer Substituer → choisis "Développé incliné haltères 30°"
3. Vérifie que **le panel "Comment bien exécuter X" change pour les haltères** + badge `(substitué)` visible
4. Si choisi un sub hors atlas (genre "Exercice maison"), le panel **garde les cues prescrits** (pas de panel vide)

## 9. Recommandation prochain sprint

**Sx_24 — Spec système** combinant N9 (dépréciation checkbox `fait`) et N10 (scoring implicite via drop-off charge/reps + fatigue inter-exo). Distinction explicite **signal saisi / dérivé / implicite**, pas de recalcul rétroactif, nouvelles saisies seulement.

Puis Sx_25 — Spec Coach Report v2 LLM narratif encadré (toujours sur la page SSR imprimable, pas de PDF natif V1).
