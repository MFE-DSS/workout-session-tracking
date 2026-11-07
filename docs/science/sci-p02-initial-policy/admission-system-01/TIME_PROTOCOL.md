# SCI-P02-INITIAL-POLICY-ADMISSION — C6 protocole de collecte

**initial-positive-time-evidence/1.0.0-proposed ; sortie C ; aucun participant ni résultat collecté ici.** Ce protocole n'admet pas Duration et ne fixe aucune seconde de travail/setup, durée moyenne de machine, multiplicateur de transition ou nombre universel d'essais.

## Question et périmètre

Pour une personne adulte déclarée non clinique sans limitation prise en charge, une configuration exacte du bundle initial, son état de familiarisation/calibration et un budget déclaré : dispose-t-on d'une borne temporelle applicable couvrant réellement **la première exécution**, ou seulement d'un temps passé/arithmétique conditionnelle ? Départ sans charge connue et retour avec réglage comparable sont deux domaines distincts, jamais fusionnés pour fabriquer une borne du novice.

Les sept réalisations bilatérales du plan qualifié de REPORT bornent la première collecte. Pas d'élargissement aux autres pulls, appairages unilatéraux ou supersets. Deux et trois séances changent les répétitions hebdomadaires et l'état de familiarisation : enregistrer l'ordre réel des séances, ne pas prétendre qu'une troisième répétition est une nouvelle première séance. La sélection reste contextuelle, sans inventaire obligatoire.

## Trois issues et règles d'autorité

- **A — modèle positif** : protocole applicable, données réelles, préenregistrement et validation de prédiction indépendants. Une moyenne ou le min/max de l'échantillon ne suffit pas.
- **B — convention produit bornée** : hypothèses exactes, auteur humain, domaine, source, limites et retrait explicitement acceptés ; aucun label « validé scientifiquement » ni probabilité personnelle. Le nouveau contrat doit exprimer cette nature avant tout READY. Aucun chiffre candidat n'est proposé depuis des fixtures.
- **C — preuve insuffisante** : issue actuelle. Collecter/analyser selon ce protocole ou conserver blocage précis si moyens/autorisation manquent. Un GO de collecte/build n'est pas une preuve positive.

## Avant collecte : dossier préenregistré requis

Responsable scientifique + exploitation identifiés ; population, critères inclusion/exclusion, cadre supervisé/autonome et limites du futur usage, lieu/appareils réels, matériel effectivement disponible, protocole bootstrap relu C3, droit de retrait/traitement des observations et autorisation de l'environnement. Les consentements et durées de conservation ne sont pas déduits d'un script ; DATA fournit la politique applicable. Aucun usage de production/destruction de preuves QA.

Le responsable scientifique/statistique fixe **avant de consulter les résultats de validation** : cible de couverture de borne, tolérance de dépassement, niveau d'incertitude, traitement du risque d'arrêt, plan d'échantillonnage et calcul de taille justifié, séparation apprentissage/validation par sujet et par contexte, stratification nécessaire, règles de données manquantes et critères de retrait. Ces paramètres sont **OPEN, non inventés par l'architecte**. Tant qu'ils manquent, collecte pilote descriptive possible seulement si autorisée, mais promotion prédictive interdite. Aucun « n séances suffisent » universel.

## Enregistrement exact par décision/séance

1. Identifiant pseudonyme de sujet et références d'autorisation/consentement, horodatage, sujet/contexte/appareil/réalisation/côté, engine/policy/curation/pull/bundle/effective-science digests, request/evaluation fingerprints, prescription et budget. Ne pas collecter taille/poids si inutiles.
2. Familiarité déclarée, début/état de calibration, provenance/ledger complet ; réglage observé et unité, technique/gêne/succès/completed, RIR facultatif, acceptation/réessai/refus. Chaque essai préparatoire est explicitement distinct du travail prescrit : ne pas le compter deux fois en séries de travail.
3. Horloge monotone de séance et mapping UTC sourcé. Mesurer début/fin de session/prep, slot/prep, chaque tentative de calibration, chaque série de travail, repos interséries, installation/réglage/transition/attente et saisie/interaction nécessaire. Conserver horloge/événement/source, précision de mesure et éventuelle incertitude ; pas de décomposition depuis les seuls completed_at.
4. Pour chaque intervalle : kind, couverture, début/fin, chevauchements explicites et contexte de prescription. Même clock pour union ; horloges non comparables → composante incertaine. Une période sans événement n'est pas zéro ; un trou d'horloge est nommé/inconnu. La préparation générale et les opérations entre slots ne doivent pas disparaître de la couverture.
5. Temps réellement écoulé jusqu'au terme du protocole, état achevé/arrêté/abandonné/interrompu, cause si disponible et non forcée. Attente de matériel, instructions, familiarisation, retries et repos réellement plus longs restent des observations du contexte ; aucune suppression opportuniste des séances trop longues. Conserver les arrêts comme données censurées/échecs opérationnels selon règle préenregistrée.
6. Séparer interruption extérieure exceptionnelle et activité nécessaire sans retrancher silencieusement leur temps ; présenter les deux analyses si le protocole le prévoit et rendre explicite laquelle définit le domaine servi.

Chaque séance doit pouvoir être rejouée pour vérifier couverture et absence de double comptage. L'addition des composantes doit se confronter à l'écoulé total ; union des intervalles quand setup a lieu pendant repos. Aucun setup positif n'est inventé pour combler un gap, aucun zéro par défaut pour le masquer.

## Analyse et validation

Geler avant apprentissage les règles d'applicabilité (réalisation/appareil, calibration/familiarité, structure séquentielle, disponibilité, contexte supervisé/autonome). Décrire distributions, coverage manquante, dépassements et abandons par strate ; aucune moyenne ne devient une borne personnelle. Si l'on construit un modèle, publier variables réellement consommées, entraînement, version, domaine et règle de borne ; séparer sujets de validation pour éviter qu'une même personne prouve son propre modèle par ses répétitions.

Sur validation tenue à part, mesurer : couverture empirique de la borne haute et incertitude, fréquence/amplitude des dépassements de budget, erreur/dispersion pertinentes, complétude de préparation/bootstrap, performance par strate et échecs/arrêts. Comparer aux seuils préenregistrés ; refus/coverage insuffisante/strate absente → modèle non admis pour cette strate. Pas de refit sur les échecs puis réemploi du même lot comme preuve indépendante.

Le modèle ne peut ignorer les inconnus indispensables. Changer appareil, réalisation, prescription, durée réelle des repos, contexte de préparation, état de calibration ou population invalide son applicabilité sauf extension revue. Les conventions C2 ne sont pas comprimées pour rentrer dans le budget. Une réfutation ne porte que sur la configuration étudiée, pas sur toutes les alternatives.

## Pièces fermant C6

Protocole/analyses préenregistrés signés + dataset réel sourcé et politique de données applicable + journal des exclusions/arrêts + code/version d'analyse + validation tenue à part et ses résultats/limites + reviewer scientifique indépendant + modèle/convention versionné et digest immuable + règle d'applicabilité/invalidation. Ensuite seulement : binding admis et test par vrai producteur/validateur. Si B est choisi, remplacer les revendications prédictives par les hypothèses produit bornées effectivement acceptées, jamais renommer un min/max « modèle validé ».

**Blocker actuel exact : aucune telle base positive applicable n'est admise.** Les fonctions savent calculer et préserver provenance ; elles ne fournissent pas cette preuve à elles seules. La décision de route, les paramètres statistiques et moyens de collecte doivent venir des responsables compétents ; le système reste honnêtement indisponible pendant ce travail.
