# Sb_BI_01.activation — Readiness Plan (Controlled Body Intelligence Flag Activation)

**Type** : ACTIVATION READINESS / PLAN — docs-only, **aucun code, aucune activation**.
**Date** : 2026-07-11
**Statut** : 🟢 PLAN LIVRÉ — activation **deferred until after dogfood + explicit GO**.
**Rapport** : [`../SPRINT_Sb_BI_01_ACTIVATION_READINESS_REPORT.md`](../SPRINT_Sb_BI_01_ACTIVATION_READINESS_REPORT.md)

> **Objet** : décrire **comment** activer `body_intelligence_enabled` en prod de
> façon contrôlée, **sans l'activer** dans ce sprint. Ce plan est une **procédure
> future** ; rien n'est exécuté ici.

---

## 0. Étape 0 — Brainstorming / Options / Risques / Choix retenu

### Options

| Option | Description | Verdict |
|---|---|---|
| **A** | Readiness docs-only maintenant, activation après dogfood | ✅ **RETENU** |
| B | Activation immédiate sans dogfood | ❌ trop tôt |
| C | Activation + deploy + smokes maintenant | ❌ GO deploy explicite requis + dogfood demain |
| D | Attendre sans préparer | ❌ moins efficace |

### 15 sujets clivants tranchés

1. **Activer ou préparer ?** → **préparer seulement** (Option A). Rien activé.
2. **Flag config / env / settings ?** → **variable d'env** dans le `.env` prod (`BODY_INTELLIGENCE_ENABLED=1`) — pydantic `BaseSettings` la lit ; pas de changement de code.
3. **Déployer avant ou après dogfood ?** → **après** dogfooding terrain (validation des surfaces d'abord).
4. **Smoke public ou auth aussi ?** → **les deux** : public (404→existence) + auth-redirect (303). Jamais de session prod personnelle.
5. **Tester sans compte prod ?** → **oui** : `/body/intelligence` flag ON → **303** (redirect login) pour anonyme = suffisant pour prouver « surface existe, plus 404 ». Pas besoin de se connecter.
6. **Utilisateur de test dédié ?** → **non requis** pour le smoke (le 303 suffit) ; si une vérif authentifiée est voulue plus tard, créer un **compte de test dédié**, jamais un compte prod réel.
7. **Si `/body/intelligence` marche mais `/physique` crée encore une double lecture ?** → `/physique` est **déjà encadré** (Sb_BI_01.3) + lien conditionnel s'affiche (flag ON) → une seule surface **principale** signalée. Si double lecture persiste → NO-GO, revoir microcopy avant ré-activation.
8. **Si le lien depuis `/physique` apparaît mal ?** → NO-GO ; corriger le rendu (build ciblé) avant activation ; rollback flag entre-temps.
9. **Quels endpoints vérifier ?** → §5 (public + auth).
10. **Quels fichiers/config exacts changer ?** → **UNIQUEMENT** le `.env` prod (`BODY_INTELLIGENCE_ENABLED=1`) — voir §3. Aucun fichier repo.
11. **Commande deploy ?** → `deploy-production.yml` (workflow_dispatch), `ref = <SHA ou branche réelle>` — **jamais `main`** (défaut invalide, cf. Sx_32) ; `skip_smoke=false`.
12. **Rollback exact ?** → §6 (remettre `BODY_INTELLIGENCE_ENABLED=0` / retirer la ligne + restart systemd ; ou re-deploy du SHA précédent).
13. **Tag release ?** → **aucun tag** pour l'activation d'un flag (pas un changement de version applicative). Release tag reste deferred.
14. **Logs à surveiller ?** → §7.
15. **Critère GO/NO-GO ?** → §8.

### Risques / parades

| Risque | Parade |
|---|---|
| Double lecture corporelle (BI + score `/physique`) | `/physique` déjà encadré (Sb_BI_01.3) ; NO-GO si microcopy insuffisante |
| Surface BI cassée en prod | smoke 303 ; rollback flag immédiat |
| Deploy sur `ref=main` invalide | passer le **SHA/branche réel** (jamais `main`) |
| Smoke sur compte prod personnel | **interdit** — smoke public + 303 uniquement |
| Activation avant dogfood | **interdit** — dogfood d'abord |

---

## 1. Préconditions obligatoires (avant activation)

1. `Sx_BI_01`, `Sb_BI_01.1`, `Sb_BI_01.2`, `Sb_BI_01.next`, `Sb_BI_01.3` **ACCEPTED** ✅ (toutes satisfaites).
2. `/physique` **encadré** (Sb_BI_01.3) ✅.
3. **Dogfooding terrain Sx_DOGFOOD_01** effectué et concluant (⏳ prévu demain).
4. **GO explicite** de l'opérateur pour l'activation **et** le deploy.
5. CI verte sur le SHA à déployer.
6. Backup prod récent vérifié (`/healthz/strict` → backup OK).

**Si une précondition manque → NO-GO.**

---

## 2. Activation target

- **Surface** : `GET /body/intelligence` (Zone Cards + Drill), aujourd'hui **404** en prod (flag OFF).
- **Effet de l'activation** : la route devient accessible (303 pour anonyme, 200 pour authentifié) ; le lien « Voir la lecture par zones » apparaît sur `/physique`.
- **Aucune autre surface** activée (le flag ne gouverne que `/body/intelligence`).

---

## 3. Config / flag à changer (au moment de l'activation, PAS ce sprint)

| Élément | Valeur |
|---|---|
| Fichier | `/opt/workout-session-tracking/.env` (VPS prod) |
| Ligne à ajouter/modifier | `BODY_INTELLIGENCE_ENABLED=1` |
| Mécanisme | pydantic `Settings` (`BaseSettings`) lit le `.env` ; `body_intelligence_enabled` passe à `True` |
| Redémarrage | `sudo systemctl restart <service>` (ou via le pipeline deploy) |
| Fichier repo modifié | **AUCUN** (le défaut `Field(default=False)` reste dans `config.py` ; on ne change **pas** le code) |

> **Important** : l'activation est un **changement d'environnement prod**, pas un
> commit. Le défaut du repo reste `False` (sécurité : toute nouvelle install/CI est
> OFF par défaut).

---

## 4. Procédure deploy future (au GO)

1. Choisir le **SHA** à déployer (dernier commit CI-vert du cycle BI, ex. `fa7d63e` ou plus récent).
2. Poser `BODY_INTELLIGENCE_ENABLED=1` dans le `.env` prod (§3) — via la procédure ops sécurisée (pas dans le repo).
3. Lancer `deploy-production.yml` (workflow_dispatch) : `ref=<SHA réel>` (**jamais `main`**), `skip_smoke=false`.
4. Le workflow déploie + exécute `smoke_deploy.sh` automatiquement.
5. Vérifier la smoke checklist (§5) + monitoring (§7).
6. Décision GO/NO-GO (§8).

---

## 5. Smoke checklist

### 5.1 Public (sans compte)
- [ ] `GET /healthz` → 200
- [ ] `GET /healthz/strict` → 200 (db.ok, backup OK, deploy.sha = SHA attendu)
- [ ] `GET /welcome` / `/login` / `/register` → 200 (surfaces publiques intactes)
- [ ] **`GET /body/intelligence` → 303** (flag ON : redirect login pour anonyme — **plus 404**). C'est la preuve que la surface est activée, **sans se connecter**.
- [ ] `GET /physique` → 303 (auth requise, inchangé)

> **Nouveau check à ajouter au smoke lors du build d'activation** : le
> `smoke_deploy.sh` actuel **ne teste pas** `/body/intelligence`. Le build
> d'activation devra ajouter un `check_auth_redirect "GET /body/intelligence" "/body/intelligence"`
> (attendu 303 flag ON). **Non fait ici** (docs-only).

### 5.2 Authentifié (sans compte prod personnel)
- [ ] Si une vérif authentifiée est requise : utiliser un **compte de test dédié** créé pour l'occasion (jamais un compte prod réel), vérifier `/body/intelligence` → 200 + Zone Cards + Drill + microcopy non médicale.
- [ ] Vérifier `/physique` → lien « Voir la lecture par zones » présent et pointant vers `/body/intelligence`.
- [ ] **Interdit** : se connecter avec un compte utilisateur réel de production.

---

## 6. Rollback exact

En cas de NO-GO après activation :
1. **Rollback flag (rapide)** : remettre `BODY_INTELLIGENCE_ENABLED=0` (ou retirer la ligne) dans le `.env` prod + `sudo systemctl restart <service>` → `/body/intelligence` redevient 404. **Aucun re-deploy nécessaire** (le code est inchangé).
2. **Rollback complet (si nécessaire)** : re-déployer le SHA précédent via `deploy-production.yml` (`ref=<SHA-précédent>`).
3. Vérifier le retour à l'état attendu (smoke §5.1, `/body/intelligence` → 404).

> Le rollback flag est **le plus sûr** : c'est un simple toggle d'env, réversible en
> secondes, sans toucher le code déployé.

---

## 7. Monitoring / logs

- **`/healthz/strict`** : db.ok, backup présent + intègre, deploy.sha correct.
- **Logs applicatifs** (systemd journal) : erreurs 500 sur `/body/intelligence`, exceptions dans `compute_physique_dashboard` (réutilisé par les Zone Cards).
- **Codes HTTP** : `/body/intelligence` doit passer de 404 → 303/200 ; surveiller un pic de 500.
- **Leaderboard / user_profile** : vérifier qu'ils rendent toujours (consommateurs partagés de `compute_physique_dashboard`).

---

## 8. Critères GO / NO-GO (après dogfood + smoke)

**GO si TOUS** :
- dogfooding terrain concluant (surfaces lisibles, non médicales, pas de « charge faussement intelligente ») ;
- smoke public vert (`/body/intelligence` → 303, healthz OK) ;
- pas de double lecture corporelle perçue (`/physique` encadré suffit) ;
- lien `/physique` → BI correct ;
- pas de régression leaderboard/user_profile ;
- backup prod OK.

**NO-GO si UN SEUL** :
- surface BI en erreur (500) ;
- double lecture confuse ;
- lien cassé/mal placé ;
- régression consommateur partagé ;
- dogfood négatif.

→ NO-GO = **rollback flag** (§6) + build correctif ciblé avant nouvelle tentative.

---

## 9. Non-goals (ce sprint)

Pas de code · pas de test · pas de config prod · **pas de modification du flag** · pas
de deploy · pas de release tag · **pas de smoke prod réel** · **pas de compte prod
personnel** · pas de modification `/physique` · pas de modification `/body/intelligence`.

---

## 10. Décision

**Activation `deferred until after dogfood + explicit GO`.** Ce plan est prêt ; il
sera exécuté par un **futur build/ops `Sb_BI_01.activation`** (qui ajoutera le check
smoke `/body/intelligence` + posera le flag prod), **uniquement** après dogfooding
terrain concluant et GO explicite de l'opérateur.

---

## 11. Verdict

**Verdict :** 🟢 **Sb_BI_01.activation-readiness — PLAN LIVRÉ, activation deferred.**

La procédure d'activation contrôlée de `body_intelligence_enabled` est **entièrement
cadrée** : préconditions (dont dogfood + GO explicite), activation par **variable
d'env prod** (`BODY_INTELLIGENCE_ENABLED=1`, aucun fichier repo modifié, défaut reste
`False`), deploy via `deploy-production.yml` (`ref=<SHA réel>`, jamais `main`),
**smoke sans compte prod** (`/body/intelligence` → 303 prouve l'activation),
**rollback flag** en secondes, monitoring `/healthz/strict` + consommateurs partagés,
critères GO/NO-GO explicites. **Rien n'est activé, déployé ni modifié dans ce sprint.**
Activation **deferred until after dogfood + explicit GO**.
