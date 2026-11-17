# REL-03 OPS-02 — approbateur unique explicitement désigné

17 novembre 2026. Parent canonique `612617193e898c4cf90d2a93250d7567e02cf3ac`.

## Décision et portée

L'opérateur confirme : « je travail seul donc uniquement le mien, MFE-DSS », après avoir autorisé le paquet opérationnel et la désignation de l'approbateur. Le compte désigné est `MFE-DSS`, User/id156458952. Cette décision remplace la séparation entre deux humains proposée dans OPS-02 ; elle ne remplace pas l'approbation effective d'un run, ni n'autorise une release APK/OTA.

## Brainstorming / Options / Risques / Choix retenu

Exiger un second humain rendrait le paquet inexécutable pour cet opérateur seul. Un relais bot contournerait la séparation sans apporter de revue humaine. Choix : utiliser la politique d'auto-approbation explicite déjà supportée par la garde générale de publication, également pour la préparation d'image. `qa-release` aura MFE-DSS comme seul reviewer humain direct, `prevent_self_review=false`, bypass administrateur désactivé. Coût assumé : absence de séparation entre deux personnes ; la revue reste une action humaine distincte, traçable et liée au run/SHA exact.

La préparation d'image exige toujours une tentative1, le workflow manuel exact, le SHA exact, le run en cours, une seule approbation de l'environnement exact, un User explicitement reviewer et le commentaire `APPROVE_QA_IMAGE <SHA exact>`. L’auto-approbation d’image est bornée à MFE-DSS (id156458952), unique reviewer direct ; autre identité ou liste élargie User/Team refusée. Si la politique interdit l'auto-approbation, l'acteur ne peut toujours pas s'approuver. Une politique absente ou non booléenne est refusée. Aucun accord déduit d'un GO MERGE, aucun auto-approve de l'agent.

## Plan d'implémentation borné

**Architecture :** aligner `image_preparation_approval(env, get=None)` sur le réglage GitHub existant ; ne modifier ni workflow, ni interface produit, ni SCI, ni migrations, ni modules natifs. Les gardes existantes de publication restent intactes.

**Fichiers possédés :** `tools/qa_delivery/image_receipts.py`, `tests/test_qa_delivery_image_receipts.py`, cet amendement, le delta de spec QA release et les paragraphes opérationnels de `docs/release/rel-03/ops02/OPERATIONAL_DECISION.md` / `COMMANDS.md` / `OPS02_SCOPE_AND_LEDGER.md`.

- [x] RED : cas reviewer=acteur permis par false ; vérifier refus sous true, politique inconnue, approbation absente/étrangère/bot, mauvaise source, commentaire, environnement ou tentative.
- [x] GREEN : politique booléenne obligatoire ; comparaison reviewer/acteur conditionnelle seulement. Conserver les autres prédicats.
- [x] `check_scope`, checks locaux exigés et broad consommateurs QA ; aucune full sweep locale sans tier l'exigeant.
- [ ] Revue indépendante du delta complet ; correction en scope, PR et CI HEAD exact, merge gardé sous GOV-MERGE-01, CI canonique et reçus réels.
- [ ] Après livraison, configurer seulement l'environnement QA désigné, relire sa protection et les références autorisées. Les tokens dédiés manquants restent une dépendance, jamais un token large substitué.

## Review Focus

Le booléen false doit permettre l'opérateur solo sans permettre une approbation absente, par bot ou par non-reviewer. True doit toujours interdire l'auto-approbation. Les valeurs absentes/non booléennes ne deviennent pas false. Une approbation d'un autre run/environnement/SHA et une tentative relancée ne valent pas autorisation. Les secrets, calcul cloud, déploiement QA et distribution native restent des états distincts.

## Vérification et livraison

Cas de politique :2RED/1PASS avant correction →29PASS sur le fichier final. Revue indépendante :2Important (exception trop large et instructions opérationnelles périmées), corrigés en une passe. Les3 cas autre identité/extraUser/extraTeam ont réellement échoué avant la restriction, puis passent dans la suite finale. Broad consommateurs :375PASS,1warning de dépréciation Starlette/httpx existant. Ruff ciblé et budget259≤548, protocole, OpenSpec strict, diff check et Gitleaks tools passent. Bandit obligatoire -ll app et fichier modifié passent ; un scan additionnel sans seuil conserve3LOW historiques B404/B603 du fichier, sans les masquer ni modifier de seuil. Pas de full sweep locale au tierISOLATED. Les CI/HEAD/merge restent à acquérir.

Ruling : la désignation explicite de MFE-DSS seul autorise l'amendement de la séparation initiale, sans redemande d'un GO déjà donné. Coût : une seule personne peut déclencher puis approuver ; la vraie approbation GitHub liée à la source et les autres preuves restent indispensables. Aucun second avis des correctifs finaux prétendu.

Aucun nouvel environnement, build d'image ou déploiement n'est déclaré réalisé par cet amendement.
