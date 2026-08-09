# Sb_CUSTOM_PROGRAM_PUBLICATION_04 — Cycle de republication sûr (SPEC)

**Cycle :** Custom Program · **Amont :** `Sx_CUSTOM_PROGRAM_04 §6-7` + `Sx_CUSTOM_PROGRAM_05` (publication/versioning) + PUBLICATION_01 (matérialisation N templates) + PUBLICATION_02 (nouveau cycle d'édition) + PUBLICATION_03 (accès/lancement)
**Tier :** ISOLATED (fichier de test neuf + docs ; **aucun changement de code app · aucune migration**) · **Statut :** ✅ MERGED (voir appendice closeout du rapport)

---

## 1. Objectif

Rendre **sûr et vérifié** le cycle complet de republication d'un `UserProgram` : publié `v{n}` → nouveau cycle d'édition (PUBLICATION_02, même row → `draft v{n+1}`, liens de séance effacés) → édition + validation → **republication `v{n+1}`**. Objectif produit : les nouvelles séances `v{n+1}` sont lançables (PUBLICATION_03), les anciennes `v{n}` sont **préservées, immuables, non lançables via le programme courant et jamais exposées** dans `/library`.

## 2. Préflight — décision de schéma (STOP + arbitrage opérateur, Option A)

Le préflight a répondu à la question imposée (« le schéma existant supporte-t-il l'archivage/remplacement sûr des anciens templates user ? ») et a **atteint des conditions d'arrêt de la mission** → **STOP + arbitrage**. Verdict opérateur : **Option A**.

### 2.1 Le cycle REQUIS est déjà exprimable — sans migration, sans nouveau champ
- `publish_user_program` (PUBLICATION_01) construit les slugs avec `current_version` : `up{uid}-{base}-v{n+1}-s{pos}`. Comme PUBLICATION_02 a **incrémenté** `current_version`, les slugs `v{n+1}` **diffèrent** des `v{n}` → **aucune collision**, N **nouveaux** `WorkoutTemplate` créés, séances re-liées.
- PUBLICATION_02 a **déjà effacé** `published_template_id`/`template_slug_snapshot` sur chaque séance ; la republication les repointe vers les templates `v{n+1}`.
- **Conséquence** : aucune séance ne pointe plus vers les `v{n}` → `resolve_owned_published_template` renvoie `v{n+1}`, `is_owned_published_template(v{n})` renvoie `False` → **`v{n}` non lançable** (ni par le programme, ni par slug via `create_session`). Les `v{n}` restent `catalog_section="user"` : **immuables, exclus de `/library` (listing + `/library/{slug}` → 404), protégés du wipe-guard reseed**.

Toute la section « Expected product behavior » est donc **déjà satisfaite** par les briques existantes.

### 2.2 L'archivage « préféré » N'est PAS exprimable sûrement (conditions d'arrêt)
`WorkoutTemplate` n'a **aucun champ d'archivage** (`archived_at`/`is_archived` absents). Le seul mécanisme est `catalog_section="archived"`, **inutilisable** ici :

| # | Effet du re-label `user`→`archived` | Condition d'arrêt |
|---|---|---|
| 1 | `/library/{slug}` (`pages.py`) ne 404 que sur `"user"` → un `"archived"` **rend sa page détail** = exposition globale par slug | *no global /library exposure* · *archived semantics conflict* |
| 2 | Wipe-guard seed supprime `catalog_section != "user"` → le template deviendrait **supprimable au reseed** | *no delete of old rows* |
| 3 | `"archived"` = retrait d'un template **système** ; le détourner change une sémantique catalogue partagée | *risk of breaking system templates* |

Un vrai champ d'archivage exigerait une **migration** — interdite car le lifecycle requis s'exprime **déjà** sans elle (§2.1).

### 2.3 Décision retenue (Option A)
**Aucune migration. Aucun nouveau champ/table. Aucun re-label.** Les anciens `v{n}` restent `catalog_section="user"` (privés, immuables, non lançables via liens effacés, exclus de `/library`). Ce sprint **prouve et verrouille** ces invariants par des tests de régression et **documente** la décision de schéma. **Zéro changement de code applicatif.**

## 3. Comportement (contrat verrouillé par tests)

| Invariant | Garde |
|---|---|
| Republier `v{n+1}` crée N **nouveaux** templates, slugs `…-v{n+1}-s{pos}` | slug versionné (PUBLICATION_01) |
| Anciens `v{n}` **jamais supprimés** | aucune suppression dans le cycle |
| Contenu `v{n}` **inchangé** (exercices/séries) | aucune mutation ; l'édition frappe le brouillon → `v{n+1}` |
| `v{n}` **non lançable** via le programme courant | liens effacés (PUBLICATION_02) + non repointés |
| Programme lié **uniquement** aux `v{n+1}` | republication repointe toutes les séances |
| `/library` exclut `catalog_section="user"` (listing + slug) | inchangé (`pages.py`) |
| Utilisateur étranger → **404** | owner-scope (PUBLICATION_03) |
| Templates **système** intacts | non touchés |
| Idempotence / collision de slug **sûre** | déjà-publié → existant, `created=False`, zéro duplicata |
| **Aucune** écriture de quality review hors freeze de publication | 1 par version ; nouveau cycle + édition = 0 |

## 4. Surface

- `tests/test_user_program_republication.py` **(neuf)** — 11 tests couvrant tout le §3.
- Docs : cette spec + rapport (avec §2 Brainstorming/Options/Risques) + SPEC_REGISTRY + ROADMAP.
- **Code applicatif : 0 fichier modifié.**

## 5. Périmètre interdit (non-goals, tous tenus)

Aucune suppression de `WorkoutTemplate` · aucune mutation d'exercices/séries d'anciens templates · aucune exposition `/library` (globale) · aucun partage · aucun navigateur d'historique de versions · **aucune nouvelle table** · **aucune migration** · aucun `WorkoutTemplate.user_id` · aucune réécriture de `session_builder` · aucun EKB/ASSET/BodyMap · aucune UI d'unpublish · aucun re-label `catalog_section`.

## 6. Limites assumées

- **Accumulation** : les anciens `v{n}` s'accumulent en base (privés, invisibles, non lançables). C'est le choix explicite « no delete » ; un archivage propre resterait une évolution **additive future** (nouveau champ `archived_at` + migration + garde `/library`), hors périmètre et sur GO migration dédié.
- **`/library/{slug}` sur `"archived"`** : le fait que la route détail ne 404 pas sur `"archived"` (templates système retirés) est un comportement **préexistant** hors périmètre ; il est précisément la raison pour laquelle le re-label des templates user est refusé ici.
