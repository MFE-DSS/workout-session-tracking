# Sx_27 — Dogfood Status : DEFERRED

**Auteur :** opérateur SPIGNOS + Claude Code (Opus 4.7).
**Date de la position :** 2026-06-15.
**Cycle parent :** `docs/strategy/Sx_27_COACHING_LOOP_AND_PRODUCT_ACTIVATION_SPEC.md`.
**Closure technique :** `docs/strategy/Sx_27_CLOSURE_REPORT.md`.

---

## 1. Position formelle

**🟡 DOGFOOD REAL USAGE = DEFERRED**
**🟡 PRODUCT VALIDATION = PENDING DOGFOOD**

À la clôture technique de Sx_27 (2026-06-15), **aucune session d'usage réelle utilisateur** n'a été exécutée sur les surfaces livrées (`/`, `/sessions/{id}/done`, `/progress` enrichis). Le code est mergé, les tests passent, les gates CI sont vertes, mais la boucle de coaching n'a pas été vécue par un utilisateur réel.

Ce document marque explicitement cette position pour ne pas brouiller la distinction entre :
- **Technical closure** : code livré et vérifié par CI (✅ atteint)
- **Product validation** : usage réel qui valide ou invalide la valeur produit (⏳ en attente)

## 2. Ce que ce document N'EST PAS

- ❌ **Pas une simulation de retour utilisateur.** Aucune phrase de ce document n'invente ce qu'un utilisateur aurait ressenti ou pensé.
- ❌ **Pas un dogfood report.** Le vrai dogfood report (quand il sera produit) suivra `docs/templates/DOGFOOD_REPORT_TEMPLATE.md`.
- ❌ **Pas une justification a posteriori.** Le dogfood reste à faire ; ce document n'est qu'une mise au point sur l'état.

## 3. Protocole de dogfood futur

Quand le dogfood sera exécuté, il suivra strictement `docs/templates/DOGFOOD_REPORT_TEMPLATE.md`. Le protocole proposé :

### 3.1 Préparation

- VPS en état nominal (`/healthz/strict` → 200, deploy_state récent)
- Backup récent < 24h
- Session client : navigateur mobile (viewport 360×640 minimum, conformément à OQ-5)
- Auth : utilisateur réel (opérateur) avec historique de séances existant

### 3.2 Parcours à exercer (5-7 sessions sur 10-14 jours)

| # | Action | Surface ciblée | Hypothèse à valider |
|---|---|---|---|
| 1 | Ouvrir `/` en début de journée | Home | "En 5 secondes je sais quoi faire" |
| 2 | Lancer la séance recommandée | `/launcher` → `/sessions/{id}` | Le CTA est-il fluide ? La reco est-elle pertinente ? |
| 3 | Terminer la séance | `/sessions/{id}/done` | Session Review V1 résonne-t-il avec le ressenti ? |
| 4 | Revenir sur `/` | Home | La tuile Last session reflète-t-elle la séance vécue ? |
| 5 | Aller sur `/progress` | Weekly loop | Le compteur, le hint et l'anomalie éventuelle sont-ils utiles ? |
| 6 | Cas particulier : session "skip" / partielle | toutes | Les fallbacks "Non déductible" se déclenchent-ils proprement ? |
| 7 | Cas particulier : utilisateur en cold start | Home + reco | "Première séance — données encore limitées" est-il lisible ? |

### 3.3 Critères de succès produit

- L'utilisateur répond OUI aux 5 questions §1 du spec : *Quoi faire ? Pourquoi ? Que signifie ma dernière ? Comment ajuster ? Je progresse ?*
- Aucune phrase de la narrative ne sonne fausse ou robotique au point d'irriter
- Aucune information manquante laisse l'utilisateur consulter une autre surface inutilement
- Le rythme d'utilisation (1 ouverture/jour minimum) tient sur les 10-14 jours

### 3.4 Critères d'échec (= trigger pour `Sb_27.next.<fix>`)

- Une phrase narrative invente une donnée (devrait être impossible vu les tests, mais à vérifier IRL)
- Un fallback "Non déductible" se déclenche sur un cas où la donnée existe
- L'utilisateur ne comprend pas une raison `recommendation_explainer`
- Le viewport mobile 360×640 casse (scroll horizontal, débordement)
- Une régression perf visible (latence > 2s sur `/` ou `/progress`)

### 3.5 Livrables attendus du dogfood

À l'issue du dogfood :
- `docs/dogfood/DOGFOOD_Sx_27_REPORT_<YYYY-MM-DD>.md` selon le template
- Mise à jour de `docs/strategy/Sx_27_CLOSURE_REPORT.md §11` :
  - retirer le marqueur ⏳
  - ajouter ✅ ou ❌ selon les critères §3.3-3.4
- Mise à jour de `docs/strategy/SPEC_REGISTRY.md §1bis` :
  - statut Sx_27 → ✅ confirmed by dogfood / ❌ blocker found

## 4. Position default si le dogfood ne se fait pas

Si **14 jours après la clôture technique** (cible : 2026-06-29) aucun dogfood n'a été exécuté :
- Marquer Sx_27 "**product validation indefinitely deferred**" dans le registry
- L'ouverture de Sx_28 reste **possible mais déconseillée** (cf. closure report §14.3)
- L'opérateur acte que les futures décisions s'appuient sur les hypothèses Sx_27 non vérifiées

Si **30 jours sans dogfood** (cible : 2026-07-15) :
- Considérer que Sx_27 a livré la **plomberie** mais pas la **validation produit**
- Un sprint dédié `Sb_27.dogfood-1` doit être ouvert AVANT tout cycle suivant

## 5. Pourquoi ce document existe

Verbatim spec Sx_27 §15 (DoD globale) : *"Le dogfood report Sb_27.7 valide ou invalide explicitement l'activation produit."*

Verbatim contrainte user Sb_27.7 :
> Le dogfood réel utilisateur n'a PAS encore été exécuté.
> Ne pas inventer de dogfood.
> Ne pas prétendre qu'une session réelle a été faite.

Plutôt que de produire un dogfood report fictif, Sb_27.7 fait deux choses :
1. acte la **clôture technique** dans `Sx_27_CLOSURE_REPORT.md`
2. acte le **deferral** dans ce document

Quand le dogfood réel aura lieu, le report viendra en plus, pas à la place.

## 6. Backlog

| Item | Statut |
|---|---|
| Exécuter le dogfood selon §3 | **À faire** |
| Produire `DOGFOOD_Sx_27_REPORT_<date>.md` | Bloqué par dogfood |
| Décider de Sx_28 ou `Sb_27.next.<fix>` | Bloqué par dogfood report |
