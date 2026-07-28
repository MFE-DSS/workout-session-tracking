# AUREN — Muscle Focus P0 Regional Review Protocol (`Sb_ASSET_03B.2`)

**Type** : protocole de revue humaine — **DOCS-ONLY**. Prépare la revue produit/anatomique des 3 Regional
Plates P0 **après** production géométrique (toolchain opérateur) et intake technique. `ASSET INTEGRATION GATE:
BLOCKED`.
**Amont** : [`../../strategy/Sb_ASSET_03B_2_P0_REGIONAL_PLATE_PRODUCTION_SPEC.md`](../../strategy/Sb_ASSET_03B_2_P0_REGIONAL_PLATE_PRODUCTION_SPEC.md).

> Ce protocole **ne préjuge d'aucun verdict**. La revue est humaine (Martin) ; l'assistant ne remplit pas les
> décisions. **`PROFESSIONAL ANATOMICAL REVIEW: NOT CLAIMED`** même après acceptation produit.

---

## 1. Objet de la revue

La revue statue, **plaque par plaque**, sur les 3 géométries candidates produites par le toolchain opérateur et
passées à l'intake technique. Elle **précède** toute intégration ; elle **ne franchit pas** l'ASSET INTEGRATION
GATE.

## 2. Décision par plaque (indépendante)

```
CHEST      : ACCEPTED | REVISION REQUIRED | REJECTED
SHOULDERS  : ACCEPTED | REVISION REQUIRED | REJECTED
POSTERIOR  : ACCEPTED | REVISION REQUIRED | REJECTED
```

**Règle de verdict global** : `GLOBAL: ACCEPTED` **uniquement si les 3 plaques sont ACCEPTED individuellement**.
Sinon `GLOBAL: REVISION REQUIRED` (au moins une REVISION, aucune REJECTED) ou `GLOBAL: REJECTED` (au moins une
REJECTED).

## 3. Axes de revue (chaque plaque)

1. **Exactitude générale** — la forme correspond au muscle réel, sans erreur grossière.
2. **Absence de forme trompeuse** — pas de « pectoraux = poumons », pas de faisceaux flottants, pas de masse
   indistincte.
3. **Compréhension immédiate** — lisible sans légende par un utilisateur non expert.
4. **Qualité du crop** — cadrage local pertinent (pas de corps entier, pas de hors-sujet).
5. **Distinction héros / contexte** — muscle cible vs os/voisin clairement séparés (remplissage/opacité/trait).
6. **Fidélité aux ancrages** — os de repère et insertions cohérents (clavicule/acromion/épine ; sternum/humérus ;
   bassin/ischion).
7. **Lisibilité mobile 360 px** — formes réductibles, contraste suffisant, pas de perte à petite taille.
8. **Cohérence Auren Terminal** — graphite/ambre, ≤ 3 teintes, 0 gradient/ombre, couleur via tokens.
9. **Qualité des captions** — FR, exactes, non médicales, non mesurées ; miroir textuel de ce qui est montré.
10. **Attribution visible** — Servier / OpenStax 1ʳᵉ éd. créditées sur la surface de revue.

## 4. Cas d'exigence spécifiques (rappel, contrainte de forme)

- **Chest** : éventail claviculaire + sterno-costal **convergeant** vers **une** insertion humérale ; **rejet**
  si deux ovales miroir / aspect poumons / plastron.
- **Shoulders** : 3 faisceaux **ancrés** (clavicule/acromion/épine), même deltoïde sous 2 vues ; **rejet** si 3
  muscles indépendants / faisceaux sans os / postérieur fondu dans le dos.
- **Posterior** : crop bassin→cuisse, fessier vs ischios distincts, **grouped-honest** ; **rejet** si corps
  entier / « bas du corps générique » / fusion / localisation par faisceau prétendue.

## 5. Surface de revue

Ouvrir localement `design/auren/previews/muscle-focus/auren-muscle-focus-p0-regional-v0.1.0.html` (produite à
l'intake) : desktop + cadres 360 px, front/back pour shoulders, fond graphite, héros ambre, captions FR,
attribution, fallback no-JS. **Aucune** dépendance réseau ; **aucune** prétention d'écran produit final.

## 6. Ce que la revue NE conclut PAS

Même `GLOBAL: ACCEPTED` :

```
PROFESSIONAL ANATOMICAL REVIEW : NOT CLAIMED
PROFESSIONAL LEGAL CLEARANCE   : NOT CLAIMED
RUNTIME INTEGRATION            : NOT STARTED
ASSET INTEGRATION GATE         : BLOCKED
```

L'acceptation produit **autorise** la suite gatée (revue anatomique professionnelle, puis — séparément — travaux
d'intégration), elle ne la **remplace pas**.

## 7. Suite selon verdict

- **3× ACCEPTED** → `GO` séparé pour la revue anatomique professionnelle, puis planification N3 (`Sb_ASSET_03B.3`)
  — **hors périmètre 03B.2**.
- **REVISION REQUIRED** → la/les plaque(s) concernée(s) repassent au toolchain opérateur ; ré-intake ; ré-revue.
- **REJECTED** → cause documentée ; nouvelle production ; les artefacts rejetés sont **conservés comme preuve**
  historique (jamais réécrits).

---

## Verdict

**Verdict :** 🟢 **`P0 REGIONAL REVIEW PROTOCOL: DEFINED`.** Décision **par plaque** (chest/shoulders/posterior),
10 axes de revue, cas d'exigence de forme, règle « global ACCEPTED ⇔ 3/3 », et bornes explicites (aucune
revendication anatomique/juridique, gate BLOCKED même après acceptation). **Aucune revue exécutée, aucun verdict
prérempli.** `ASSET INTEGRATION GATE: BLOCKED`.
