# Sprint report — DA-04.0b BodyMap Internal Authorization

**Date :** 2026-10-28
**Branche :** `sb/da-04-0b-bodymap-internal-authorization`
**Base :** canonique `a647fe4`
**Nature :** micro-tranche de gouvernance — aucune géométrie, aucun code runtime, aucune surface.

## 0. Commande

Réponse de l'opérateur au rapport DA-04.0 (2026-10-28) :

- « Je choisirais la voie (b), mais limitée à l'usage interne/prototype » → `ACCEPT_INTERNAL_P0_WITH_CONSTRAINTS`,
  « mais pas approved for public App Store release ». Contraintes : builds internes AUREN ; attribution visible dans
  À propos / Licences ; les deux sources + mention « adapted » ; « visualisation non médicale » ; « revue anatomique
  professionnelle non réalisée » ; aucune revendication d'activation, de recrutement musculaire ou de risque ;
  diffusion publique bloquée jusqu'à revue anatomique + revue juridique externe. « Ce n'est pas un avis juridique,
  mais c'est un compromis de gouvernance cohérent avec les licences publiées. »
- « Je valide aussi tes deux amendements de gouvernance » : `geometry_status` corrigé ; Muscle Focus — « Le registre
  doit refléter la réalité […] Ne garde pas NOT AUTHORIZED pour un asset réellement monté. »
- Rôle verrouillé : « BodyMap V1 = localisation fonctionnelle » ; illustration riche = Anatomy V2.
- « je lancerais déjà un backlog ANATOMY-V2. Pas dans le critical path immédiat. » ; « ne remplace pas maintenant
  le master par de l'IA ».
- Puis `DA-04.1` (triptyque Push A), dans une tranche séparée.

## 1. Brainstorming / Options / Risques / Choix retenu

**Options pour inscrire la décision**

| Option | Pour | Contre |
|---|---|---|
| A — passer `runtime_authorization` à `authorized` | simple | ment : la diffusion publique n'est pas autorisée ; le garde à deux états confondrait interne et public |
| B — troisième état `internal-builds-with-constraints` + `public_release_authorization: blocked`, contraintes et texte d'attribution dans le registre | dit exactement la décision ; la garde peut exiger décision, portée, contraintes, attribution | une valeur de plus à maintenir |
| C — laisser `blocked` et noter la décision en prose | aucun changement de garde | la prose et le registre se contrediraient de nouveau — le défaut que DA-04.0 venait de fermer |

**Choix : B.** La garde passe à trois états (bloqué / interne / autorisé) ; l'état interne exige la décision nommée,
sa date, sa portée, ses contraintes, le texte d'attribution, la mention non médicale, et la diffusion publique fermée.

**Risques**

- Lire « interne » trop large. Mitigation : la portée écrite exclut le runtime web et tout store public ; la garde
  existante `test_runtime_not_integrated` reste en place pour `app/static/`.
- Faire passer la décision du propriétaire pour une revue. Mitigation : `professional_anatomical_review: not-claimed`
  et `reviewer: NOT YET REVIEWED` inchangés ; la provenance le dit en toutes lettres.
- Muscle Focus : la consigne vaut « s'ils sont utilisés dans un environnement interne contrôlé ». **Constat** :
  `/science` exige une session, mais l'inscription web est ouverte (`app/routers/auth_routes.py`, `/register`).
  L'exposition est plus large qu'« interne ». Je n'ai pas touché au runtime (hors périmètre) : l'écart est
  consigné dans le registre (`runtime_exposure_open_point`), la provenance et ce rapport, pour décision.

## 2. Changements

| Fichier | Changement |
|---|---|
| `design/auren/source/bodymap/auren_bodymap_source.yaml` | `runtime_authorization: internal-builds-with-constraints` ; champs `owner_decision*`, `authorization_scope`, `public_release_authorization: blocked`, `bodymap_role`, `runtime_constraints`, `attribution_fr`, `non_medical_notice_fr`, `license_url`, `missing_for_public_release` ; `missing_for_runtime` réduit à la surface d'attribution. Faits DA-04.0 (`gate_resolution`) conservés |
| `design/auren/source/bodymap/README.md` | état actuel : décision, portée, cinq contraintes, rôle V1, ce qui est permis ; l'état DA-04.0 passe en historique |
| `design/auren/AUREN_ASSET_INTAKE_CHECKLIST.md` | section « Décision du propriétaire — BodyMap master (DA-04.0b) » |
| `design/auren/AUREN_ASSET_PROVENANCE.md` | ligne DA-04.0b (attribution exacte, chaque source marquée adaptée) ; Muscle Focus : `usage_nature` réconciliée, note de montage `/science` et écart d'inscription ouverte |
| `design/auren/source/bodymap/auren_bodymap_mapping.yaml` | `geometry_status: PRODUCED_AS_DESIGN_SOURCE`, `runtime_status`, `public_release_status`, `status_amended_by` ; `male_neutral_v1` disponible en builds internes |
| `design/auren/source/muscle-focus/auren_muscle_focus_registry.yaml` | `asset_integration_gate: INTERNAL_P0_WITH_CONSTRAINTS`, `public_release: NOT_AUTHORIZED`, `runtime_mount`, `runtime_exposure_open_point` |
| `design/auren/AUREN_BODY_ZONE_TAXONOMY.md`, `AUREN_VISUAL_ASSET_MANIFEST.md` | lignes « NOT YET PRODUCED » du master corrigées |
| `docs/strategy/AUREN_VISUAL_BACKBONE.md` §8.4 | ligne `DA-04.0b` ; `DA-04.1` débloqué et précisé ; ligne `ANATOMY-V2` (backlog hors chemin critique) |
| `docs/strategy/SPEC_REGISTRY.md` | ligne de la tranche |
| `tests/test_auren_bodymap_master.py` | garde à trois états + 3 cas négatifs |
| `tests/test_auren_body_zone_contract.py` | `test_exactly_three_body_variants_only_the_produced_one_internal` (remplace l'épingle `NOT YET PRODUCED`) |
| `tests/test_auren_muscle_focus_plates.py` | `test_registry_declares_internal_gate_and_review_not_claimed` |
| `tests/test_auren_asset_governance.py` | commentaires alignés |

Intouchés : `auren_bodymap_master.svg`, `auren_bodymap_compact.svg`, les trois planches, tout le runtime.

## 3. Gardes qui mordent

Mutations rejouées contre la garde neuve (section 5) :

- registre repassé à `blocked` alors que les documents disent « interne » → `readme-not-blocked` ;
- état interne sans contraintes et diffusion publique ouverte → `registry-runtime_constraints-missing`,
  `registry-public-release-open` ;
- README qui perd « PUBLIC RELEASE NOT AUTHORIZED » → `readme-not-internal`.

## 4. Anatomy V2 (backlog)

Même taxonomie, mêmes 11 IDs, géométrie nettement plus nette — pas forcément plus médicale. Hors chemin
critique ; alimenté par les zones que les recadrages DA-04.1 révéleront trop grossières. Jamais une
régénération IA du master.

## 5. Vérification

- `check_scope` : `ISOLATED` (15 fichiers).
- Tests ciblés : 198 / 198 (BodyMap, contrat de zones, planches, gouvernance, identité, atlas, taxonomie,
  protocole UI) ; balayage élargi des tests qui lisent ces documents : 197 / 197.
- `check_spec_protocol` OK ; ruff OK ; budget ruff 264 ≤ 548.

**Verdict :** décision du propriétaire inscrite — **AUTHORIZED FOR AUREN INTERNAL BUILDS WITH CONSTRAINTS /
PUBLIC RELEASE NOT AUTHORIZED** ; deux vérités de gouvernance corrigées ; écart d'exposition web consigné pour
l'opérateur. DA-04.1 peut commencer.

## Annexe de clôture (2026-10-28)

- **GO MERGE** de l'opérateur (« oui bien GO MERGE »). Gate vérifié juste avant : tête `711a58d`, 11 / 11 checks
  verts, Sonar PR `OK` (0 sur toutes les conditions), 0 fil de revue ouvert, `CLEAN`.
- PR #317 fusionnée en `--merge --match-head-commit` : **`64f1d6e`**.
- **CI canonique** sur le push : run `40706972496`, **verte**.
- Aucun incident. Reste ouvert, à décider par l'opérateur : l'exposition des planches Muscle Focus avec
  l'inscription web ouverte.
- DA-04.1 démarré dans la foulée : rendus de revue publiés, code non commité jusqu'au choix T1 / T2.
