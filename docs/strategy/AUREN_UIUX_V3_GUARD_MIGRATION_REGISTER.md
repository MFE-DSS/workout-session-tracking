# AUREN UI/UX V3 — Guard Migration Register

**Statut : `APPROVED — OPERATOR`** (2026-08-18, avec les amendements A/B/C de `Sx_UIV3_04 §1bis`)
Taxonomie de référence : `AUREN_UIUX_V3_FOUNDATION_CONTRACT §11`.

**656 gardes UI, 39 modules.** Ce registre existe pour qu'aucun test
historique ne bloque une évolution de design décidée, **et** pour qu'aucun
redesign n'affaiblisse une garde qui protège une vérité.

---

## Tiers

| Tier | Nature | Règle |
|---|---|---|
| **T1** | business / data | jamais affaiblie |
| **T2** | accessibilité | jamais supprimée sans preuve ≥ |
| **T3** | contrat d'interaction | modifiable par spec explicite uniquement |
| **T4** | contrat visuel | évolutif avec décision versionnée + baseline |
| **T5** | implémentation héritée | supprimable quand la spec la remplace |

---

## Registre par module

### Surfaces Home

| Module | Tests | Tier dominant | Sort sous V3 |
|---|---:|---|---|
| `test_home_design_decisions` | 7 | **T1** | **intouchable** sur l'interdit IA · `test_the_record_states_it_is_not_built` devient **T5** dès que D1–D5 sont construites : à **retourner**, pas à supprimer |
| `test_home_reco_origin` | 15 | **T5** | pinne `<details class="reco-origin">`, que `Sx_UIV3_01` supprime. **Remplacé** par une garde « la cause est rendue sans interaction ». |
| `test_home_decision_hero` | 33 | mixte | `test_css_cta_meets_tap_target` → **T2**, renforcé à la mesure navigateur · `test_no_medical_score_claim` → **T1** · `TestAurenTerminal` (tokens, mono, pas de webfont) → **T4** · `test_no_decorative_box_shadow_on_hero` → **T5**, le hero encadré disparaît |
| `test_ui06_home_dedup` | 7 | **T4** | la cible de dédup change ; à réécrire avec la nouvelle structure |
| `test_ui06_dedup` | 15 | T4 | idem |
| `test_recommendation_surface` | 6 | **T1** | la reco affichée vient du moteur — invariant |
| `test_briefing_surface` | 10 | mixte | `has_prior` / cas vide → **T1** · classes de puce → T4 |

### Surfaces Session

| Module | Tests | Tier dominant | Sort sous V3 |
|---|---:|---|---|
| `test_uiv2_session_focus_contract` | 7 | **T3** | **conservé tel quel**. `test_cta_copy_does_not_claim_a_set_level_action` a déjà attrapé une rédaction fautive pendant le durcissement — c'est la garde modèle. |
| `test_session_set_action` | 16 | **T3** | `nav=stay` reste réel ; sous V3 il sert l'état `CORRECTION`. Libellés à mettre à jour **par la spec**, jamais par commodité. |
| `test_session_focus_sticky_cta` | 16 | **T5** | `Sx_UIV3_02 §7.9` supprime la barre collante. Supprimable **le jour où** la commande contextuelle existe, pas avant. |
| `test_session_instrument_rows` | 14 | **T4** | **conservés**. Ils pinnent des causes structurelles de débordement (piste non fixe, `flex-wrap`, pas d'`overflow:hidden` masquant) valides quelle que soit la console. |
| `test_session_focus_logging_console` | 32 | mixte | `console-badge` unique → T4 · dérivation serveur de `completed` → **T1** |
| `test_session_focus_accessibility` | 9 | **T2** | **jamais supprimés**, à étendre à la mesure de cible |
| `test_session_focus_rest_timer` | 20 | mixte | repli no-JS → **T2** · position et style → T4 |
| `test_session_focus_worked_area` | 30 | mixte | anti-médical, pas d'anatomie inventée → **T1** · rendu → T4 |
| `test_session_focus_layout` | 21 | **T4** | évolutif |
| `test_session_focus_cockpit` | 34 | T4 | évolutif |
| `test_session_focus_header_structure` | 13 | T4 | le titre passe à 3 lignes — décision versionnée présente |
| `test_session_focus_navigation` | 19 | **T3** | la jump bar reste ; son rôle change si D est retenu |
| `test_session_ux_prev_load` | 7 | **T2** | `aria-hidden` + source accessible ailleurs — invariant |
| `test_session_ux_console_priority` | 12 | T4 | la priorité change de mécanisme |
| `test_session_ux_cues_density` | 16 | T4 | cues passent en L3 |
| `test_session_ux_alternatives_order` | 17 | **T3** | l'ordre des alternatives est un contrat |
| `test_checkbox_deprecation` | 6 | **T1** | `completed` dérivé serveur — invariant |
| `test_overload_hint_render` / `test_overload_placeholder` | 29 | **T1** | aucune valeur inventée dans un champ — invariant, **renforcé** par `Sx_UIV3_02 §7.12` (AUREN ne pré-remplit pas) |
| `test_last_time` | 6 | **T1** | pas de fausse charge |

### Transverses

| Module | Tests | Tier | Sort |
|---|---:|---|---|
| `test_contrast_guard` | 8 | **T2** | **étendu** : mesurer sur le fond réel, pas sur une constante |
| `test_reduced_motion` | 10 | **T2** | conservé |
| `test_ui_interaction_primitives` | 27 | **T2/T3** | la cible 44 px devient mesurée au navigateur |
| `test_mobile_polish` | 16 | **T2** | conservé, seuils resserrés |
| `test_app_shell_*` | 99 | T3/T4 | hors périmètre V3 immédiat |
| `test_shell_terminal` / `test_session_focus_terminal` | 34 | **T4** | tokens et direction visuelle — évolutifs avec décision |
| `test_bodymap_*` / `test_atlas_*` / `test_worked_area_*` | ~100 | **T1** | géométrie et identité — jamais affaiblis par un redesign |

---

## Gardes à créer

Une garde supprimée sans remplacement est une perte nette. Les remplacements
exigés par les specs V3 :

| Nouvelle garde | Remplace | Tier |
|---|---|---|
| « la cause de la recommandation est rendue **sans interaction** » | `test_home_reco_origin` | **T2/T3** |
| « le bilan 11 zones totalise exactement 11 » | — (neuf) | **T1** |
| « aucun pourcentage de récupération n'est rendu » | — (neuf) | **T1** |
| « `unknown` n'est jamais rendu comme rempli ni comme disponible » | — (neuf) | **T1** |
| « une seule commande dominante par état » | `test_session_focus_sticky_cta` | **T3** |
| « la série courante est au-dessus de la ligne de flottaison » | — (neuf, mesurée) | **T2** |
| « 0 cible sous 44 px sur les surfaces V3 » | renforce `test_ui_interaction_primitives` | **T2** |
| « une série terminée porte une affordance de correction » | — (neuf) | **T2** |

---

## Règles d'application

1. **Tout test modifié pendant un build V3 déclare son tier dans le diff.**
2. Un test **T1** ou **T2** modifié sans justification explicite **bloque la
   tranche**.
3. Un test **T5** ne se supprime que dans la tranche qui livre son
   remplacement — jamais en avance, jamais « pour nettoyer ».
4. Un test **T4** se met à jour avec une baseline **et** une décision
   versionnée (`Sx_UIV3_03 §6`).
5. **Une docstring historique ne définit jamais le produit contre le runtime
   actuel.** Exemple constaté : un commentaire affirme qu'aucune action de
   série n'existe alors que `nav=stay` l'implémente. Ce commentaire est
   `STALE`, pas une spécification.
6. Une garde qui protège un choix **officiellement abandonné** n'est pas un
   argument contre le redesign : c'est un élément à migrer.
