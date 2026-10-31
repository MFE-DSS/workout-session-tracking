# Sb_MISSION_SESSION_ZONES — la séance proposée porte son BodyMap

**Date :** 2026-10-31
**Branche :** `sb/mission-session-zones` (base canonique `cfc1dd5`, après DA-05.1)
**Verdict :** voir la fin du rapport.

## 0. Commande et décisions de l'opérateur

- « continue sur le chemin critique […] dans le sens que tu viens de donner » : gate DA-01, puis le BodyMap de séance
  sur MISSION.
- Gate DA-01 final (planche des cinq questions, réserve sur la question 3) : « oui à tout ».
- Planche MISSION : « go ».

## 1. Brainstorming · Options · Risques · Choix retenu (`CLAUDE.md §3`)

| Option | Pour | Contre |
|---|---|---|
| A — l'app déduit les zones du plan de séance | rien côté serveur | la mission n'a pas de plan : il faudrait démarrer la séance pour la voir |
| B — **le serveur ajoute les zones à la mission** (`session_zones`, résolveur canonique) | même autorité que le plan et le relevé ; l'app ne choisit rien | toucher un module partagé (tier `shared_code`) |
| C — le panneau en plus de tout le texte | aucun retrait | « Démarrer » sort de l'écran (80 à 195 px de trop) |

**Choix : B**, et le panneau **remplace** le texte qui disait la même chose (sous-titre, « On commence par », nom
répété dans l'action). **Risques** : régénérer la fixture du labo et bouger des baselines verrouillées (→ 71 / 71
inchangées au pixel) ; un panneau écrasé (→ non dessiné sous 96 par ligne) ; une action hors écran (→ banc, 4 / 4).

## 2. Pré-vol

| # | Point | Valeur |
|---|---|---|
| 1 | baselines qui font foi | les 71 du contrat |
| 2 | fichiers LOCKED impliqués | `BODYMAP-ZONES-V1` (panneau réutilisé tel quel), `EXECUTION-SCREEN-V1` (même fixture de labo) |
| 3 | invariants | zones dérivées, jamais composées ; fait absent non dessiné ; « Démarrer » à l'écran |
| 4 | delta permis | la mission (champ `zones`), l'écran MISSION, le générateur du labo |
| 5 | fichiers prévus | §4 |

## Croquis validé

```
 AUREN · AUJOURD'HUI                 •••
            Samedi 31 octobre
              Push A
 │ Pectoraux, Deltoïdes latéraux : le moins servi…
 │ MESURÉ · 14 DERNIERS JOURS
 ┌ PECTORAUX ─────┬ DELTOÏDES LATÉRAUX ┐
 ├ DELTOÏDES POST.┼ TRICEPS ───────────┤   ← zones de la séance, dérivées par le serveur
 └────────────────┴────────────────────┘
        7 EXERCICES      21 SÉRIES
 [            Démarrer             ]
```

## Inventaire — une information, une seule fois

| Élément | Information | Source (contrat de données) | Doublon ? |
|---|---|---|---|
| titre | la séance | `mission.template.name` | non : retiré de « Démarrer » |
| raison | pourquoi elle | `mission.reason` (mots du moteur) | non |
| panneau BodyMap | où elle travaille | `mission.zones` (serveur) | non : le sous-titre qui le disait s'efface |
| chiffres | combien d'exercices / de séries | `mission.scope` | non |
| « On commence par » | le premier exercice | `mission.scope.first_exercise` | **retiré** avec le panneau : affiché dès « Démarrer » |

## Comparaison avec la référence validée

| Référence validée | Tranche / date | Ce qui doit survivre | Survit ? |
|---|---|---|---|
| `BODYMAP-ZONES-V1` | DA-04.2 | panneau dérivé, fenêtres égales, trois par ligne | **oui** |
| `EXECUTION-SCREEN-V1` | DA-05.1 | les 6 écrans | **oui**, identiques au pixel malgré la fixture régénérée |
| MISSION (vNext C2) | — | une question, une action, la raison du moteur | **oui** |

## Changement unique de l'itération

- Changement : **la séance proposée montre où elle travaille.**
- Rien d'autre : la recommandation n'est pas touchée ; la mission gagne un champ.

## 3. Relecture du relevé de décisions (`CLAUDE.md §5.2`)

| Décision | Verdict |
|---|---|
| opérateur 2026-10-29 — image → zone, exercice → zones, programme → exercices (agnostique) | **respectée** (`session_zones`) |
| opérateur 2026-10-31 — moins de texte | **respectée** (sous-titre, « On commence par », nom répété) |
| §21 — panneau dérivé, jamais composé ; zone non devinée | **respectée** |
| gate DA-01 — « oui à tout », réserve question 3 | **consignée** (backbone §8.4) |
| `CLAUDE.md §5.3` — jamais une soustraction seule | **respectée** : le texte retiré part avec le panneau qui le remplace ; sans zone, l'écran d'avant reste |
| `CLAUDE.md §5.4` — couleur = token | **respectée** (aucune couleur neuve) |
| aucun doublon verbal-visuel | **respectée** (inventaire) |

## 4. Réalisation

| Fichier | Rôle |
|---|---|
| `app/services/mobile_read_models.py` | `session_zones` ; la mission porte `zones` |
| `clients/mobile/scripts/generate_fixtures.py` | mission avec `zones` ; zones des exercices par le résolveur canonique (plus l'ancien classifieur) |
| `clients/mobile/src/fixtures/lab_fixture.json` | régénérée : `zones`, `secondary_zones`, 3 zones corrigées, horodatages |
| `clients/mobile/src/domain/types.ts` | `Mission.zones` (optionnel) |
| `clients/mobile/src/ui/MissionScreen.tsx` | panneau dérivé, texte en double retiré, jour injectable (banc) |
| `clients/mobile/src/ui/contract/MissionScreenFixture.tsx`, `fixtures.ts`, `ContractFixture.tsx`, `candidates.ts` | écran gouverné |
| `clients/mobile/visual-contract/review.spec.ts` | contrôle d'écran entier étendu à MISSION |
| `clients/mobile/visual-contract/baselines/` + manifeste | 4 baselines |
| `tests/test_mobile_zones_canonical.py` | dérivation, mission, générateur sans ancien classifieur |
| `tests/test_visual_contract_governance.py` | `MISSION-SCREEN-V1` |
| contrat (registre, §25), backbone (gate DA-01, MISSION), registre des specs | suivi |

## 5. Post-vol

- 71 baselines inchangées au pixel ; 4 neuves, identiques à l'octet aux captures revues.
- Balayage ciblé (`shared_code`) : 338 tests verts sur les consommateurs du module et de la fixture.
- Constat corrigé au passage : le générateur du labo gardait l'ancien classifieur (la moitié restante de la
  correction #322) ; la garde de module le couvre désormais.

**Verdict :** `MISSION-SCREEN-V1` **LOCKED** et gate `DA-01` **passé** — la séance proposée porte son BodyMap,
dérivé par le serveur ; la direction artistique initiale est close.
