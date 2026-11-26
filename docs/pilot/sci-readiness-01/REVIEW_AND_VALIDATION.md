# SCI-READINESS-01 BUILD-01 — revue et vérification

25 novembre 2026. Revue indépendante fraîche du diff complet non committé, parent `1f0122bf`, en lecture seule ; aucun second avis indépendant des correctifs finaux n’est prétendu.

## Brainstorming / Options / Risques / Choix retenu

Le plan approuvé sépare capture SQLite cohérente, provenance, projection pure et worker Linux jetable. Un reader ORM eager réutilisé ou l’exécution du bundle historique coûterait une autorité/borne non prouvée. Choix : adaptateur de données strict, aucun import de code historique, garde SCI limitée au seul projection.py, refus conservateur des ressources/sources manquantes et défaut désactivé. Coût assumé : une entrée canonique hors plafond maintient HOLD.

## Findings Important et corrections

- Vecteur zéro sans contribution : evidence reste NULL pour une zone sans ligne applicable. Test de non-contribution RED→GREEN.
- Quantité EXACT malgré appartenance inconnue/statut malformé : borne MINIMUM pour la part certaine, UNKNOWN si aucune ; dates indéterminées ne comptent pas. Tests mêlant dates et statuts RED→GREEN.
- Exclusions hors fenêtre et compteurs : motifs effectivement inspectés décomptés ; frontières non explorées restent NULL. Test OUTSIDE_WINDOW RED→GREEN.
- Profil scientifique inconnu reclassé Legacy : marqueurs réservés et présence de binding vérifiés ; aucun fallback statique. Trois contre-exemples RED→GREEN.
- Reçus V3 non recoupés : digest factuel vérifié lorsque le matériau conservé permet la parité ; pré-normalisation non reconstructible = UNKNOWN, pas corruption affirmée. Poids canonique recoupé au réglage effectif TOTAL_EXTERNAL, machine/PER_IMPLEMENT non convertis. Tests digest/masse RED→GREEN ; le port positif n’emploie plus un digest inventé.
- Date courante hors fenêtre sautant l’épisode V3 : chaîne examinée avant exclusion ; contradiction conservée en UNKNOWN. Test RED→GREEN.
- Lecture/parsing de source dans le parent HTTP : déplacés sous les limites enfant et délai parent ; entrées non régulières refusées, bytecode enfant désactivé. Test de frontière parent + pipe/timeout/cleanup.
- Budgets de sources séparés et pins écrasés : budget commun local/historique et namespaces distincts ; setup SQLite compté. Tests budget partagé/setup RED→GREEN.
- Adapter inventory2 manquant : vérification data-only des racines, sources, parent V3 et digest d’extension, parité avec la référence courante attestée ; aucun rôle d’extension substitué aux rôles historiques. Test de mauvais parent.
- HTTP seulement mocké : ajout du vrai consommateur HTTP+SQLite/projection sur DB synthétique canonique, deux propriétaires et empreinte complète inchangée. Le port de transport Linux et l’omission éditoriale synthétique restent identifiés.
- Tous rôles UNKNOWN/incertains : aucune quantité certaine ni état PARTIAL implicite ; lecture des scalaires SQLite typée avant matérialisation.
- Artefact P07 : mapping admis réellement consommé/contrôlé, posterior sans crédit scalaire ; contre-exemple RED→GREEN.

Aucun Critical signalé. Aucun Minor explicitement reporté par le reviewer. « Declined to judge » : qualification Linux et image réelle, traitées comme HOLD jusqu’aux preuves concernées. L’auteur conserve ce verdict, sans le convertir en PASS.

## Rulings conservés

1. Numérotation Task1→Task 1 adaptée aux scripts de suivi, sans changement du plan ; risque limité à la lisibilité du suivi.
2. Checks locaux selon check_scope, environnement Python existant et broad ciblé, pas de sweep complet systématique ; filet global : CI réelle, sans réduction.
3. Catalogue4302>4096 : refus conservé. Les ports synthétiques ne qualifient pas la source réelle ; coût : indisponibilité jusqu’à amendement/qualification.
4. Le contrat SCI historique est byte-pinné par les loaders v2 : son addendum ne peut y être ajouté sans casser la validation. Octets historiques conservés ; acte/addendum descriptif dans ADMISSION et registre de dépendances. Coût : consulter la nouvelle admission pour la dérogation, aucun hash historique réécrit.

Les logs RED/GREEN intégraux et la première revue sont conservés dans le dossier de preuves de ce seul build, sans DB personnelle ni identifiant réel. Les résultats finaux et liens CI sont dans le reçu de livraison ; une suite du reader n’est pas une acceptation native ou physique.

## Amendement accepté et relu — 26 novembre 2026

Acte `SCI-BUILD01-SCOPE-AMENDMENT-2026-11-26` : deux seuls fingerprints historiques de SOURCE_PINS au commit dc6b79f, puis normalisation des 112 pins en objets source_ref/sha256. Les 112 empreintes sont recalculées sur les octets Git de 1f0122bf, sans divergence. Scan de tout le range pertinent : zéro résultat après ces deux exceptions. Aucune règle désactivée.

Revue indépendante fraîche de ce seul delta : aucun Critical, Important ou Minor. Hors avis : revue globale des correctifs backend, qualification opérationnelle et CI du futur HEAD. La revue ne remplace pas ces preuves.

CI initiale 45704937761 : cinq shards backend et agrégat QA verts, 1 610 mobiles + TypeScript et 77 visuels verts ; lint rouge sur ces deux seuls résultats Gitleaks, Sonar skipped. Le shard Linux 4 exécute les témoins worker sans test ignoré ; il ne qualifie pas l’image/source Python cible. Les deux HOLD opérationnels restent distincts.

Vérification locale après amendement : 122 PASS/2 témoins Linux ignorés sur Darwin ; Ruff neuf, budget260≤548, protocole et OpenSpec32/32 verts. Premier appel au budget sans Ruff dans PATH échoué ; relancé avec le binaire existant et vert, sans changement de dépendance.

Avant archive : le test de parité documentaire cherchait uniquement le dossier actif. Contre-exemple sur archive datée : zéro fichier trouvé (RED). Recherche active OU archive datée, unicité et égalité exacte conservées : GREEN ; 66 tests de contrat/consommateurs verts. Aucun code produit changé.
