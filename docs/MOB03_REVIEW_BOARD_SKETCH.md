# MOB-03 — croquis consolidé pour la planche de revue

Statut : **croquis validé par l'opérateur le 5 novembre 2026**, réponse « Valider ce croquis pour la planche ». Le manifeste est reçu dans strategy/AUREN_MANIFESTO_V1.md.
Le logo est le vrai AurenMark, les couleurs et contrôles sont ceux d'AUREN. Cette validation autorise la composition de la planche ; **aucun rendu ni baseline n'est accepté par cette seule réponse**.

```text
ENTRÉE                              INSCRIPTION
          [AurenMark]               [Retour]                  AUREN
             AUREN                 Créer ton compte
Ton entraînement,                  Identifiant
construit autour de toi.           Mot de passe · Confirmation
                                   Email (facultatif) · aide récupération
Ton espace d'entraînement          [Créer mon compte]
Identifiant · Mot de passe         Résultat/refus sous le formulaire
[Se connecter]                     Inconnu : vérifier par connexion
Créer mon compte
Récupération · Confidentialité

PREMIER USAGE — en-tête discret AUREN + Retour + Étape n/4
1 Ton point de départ              2 Ta disponibilité
Taille · Poids/date/unité           Séances/semaine · Durée · Environnement
Expérience                         Déclarations confirmées seulement
Usage expliqué ; omission visible
3 Ton physique                     4 Ton premier plan
Priorités · contraintes            Ce qui est connu / ce qui manque
Vocabulaire canonique              Proposition réelle si disponible
                                   [Voir ma séance] ou [Réessayer]
[Continuer] et [Passer pour l'instant] quand facultatif

PARAMÈTRES COMPTE                   REPRISE / PROPRIÉTAIRE INCERTAIN
Compte vérifié                     AUREN + message sobre
Changer le mot de passe            Données conservées, aucun détail étranger
Export web · Confidentialité       Vérification en cours / connexion nécessaire
Suppression : politique à définir  [Vérifier] · [Changer de compte]
Déconnexion                        Pas de confirmation ou purge inventée
```

Les champs sans contrat réel ne deviennent pas des contrôles enregistrables. La planche distingue candidat visuel et produit fonctionnel. La suppression ne porte pas un bouton actif de faux effacement. Chargement, hors ligne, refus, résultat inconnu, clavier, grandes tailles de texte et retour Android sont à décliner sur le banc puis à recetter.


## Itération V2 — demande précise de l'opérateur, 5 novembre

Source G1 : « le mettre en beaucoup plus gros […] en background centré […] l'identifiant et le mot de passe centré […] des keywords, des bullet points […] bodybuilding […] cockpit ». Cette demande vaut croquis pour ces changements précis selon le protocole d'itération ; les pixels restent candidats.

```text
                   A U R E N
         [très grand AurenMark en filigrane]
               Ton cockpit
               bodybuilding
         Intelligence d'entraînement
         Corps • Programme • Progression

                 IDENTIFIANT
              [saisie centrée]
                MOT DE PASSE
              [saisie centrée]
               [Se connecter]
              Créer mon compte
         Récupération • Confidentialité
```

Même axe central sur l'inscription et la confirmation de création ; l'introduction en phrases est remplacée par des repères courts. Le filigrane réutilise le composant de marque sans modifier sa géométrie. Aucun KPI, profil déjà connu, prescription personnalisée parfaite ou résultat d'IA n'est simulé pour habiller l'entrée. L'expression « intelligence d'entraînement » positionne le cockpit ; elle ne revendique ni diagnostic ni prescription générative.

Options considérées : emblème agrandi dans l'en-tête ; filigrane central derrière le formulaire. Choix de cette itération : filigrane central, selon l'exemple transmis. Plan borné : composition Entry/Signup/Created, aucun changement des contrats de compte ; vérification des interactions existantes, contraste du filigrane, petites largeurs, rendu avant/après sur la même planche locale.

### Précision opérateur — « tout en étant minimaliste »

La V2 est simplifiée : retirer la ligne « Intelligence d’entraînement ». Un seul titre « Cockpit bodybuilding », trois repères discrets Corps / Programme / Progression, deux champs, une action principale. La marque reste un seul grand dessin en fond ; aucune donnée décorative ajoutée. Les captures web de la V2 simplifiée remplacent les précédentes dans le comparatif ; pixels toujours candidats.


## Retour retenu — V1 ajustée, supersède V2

Décision opérateur : « je préfère […] la V1 […] juste retire ton espace entraînement […] identifiant mot de passe […] centré […] AUREN AI […] sur ce moment-là spécifiquement ». Cette demande précise vaut croquis pour l'ajustement, sans acceptation automatique de pixels.

```text
                  [AurenMark V1]
                     AUREN AI
        Ton entraînement, construit autour de toi.

                   IDENTIFIANT
                 [valeur centrée]
                  MOT DE PASSE
                 [valeur centrée]
                  [Se connecter]
                 Créer mon compte
          Récupération du compte · Confidentialité
```

Rétablir la composition V1 sur la planche, retirer le filigrane géant et les mots-clés V2. Sur l'entrée uniquement : supprimer le titre « Ton espace d'entraînement », centrer les libellés et valeurs des deux champs, présenter « AUREN AI » comme variante éditoriale demandée. L'accroche reste une seule fois. Pas de renommage global, de logo redessiné ou de nouvelle capacité IA introduite. Les comportements de compte restent inchangés.


## Extension ciblée — préférences réellement enregistrables, croquis à valider

Accès : Profil → ligne actuelle « Profil d'entraînement » remplacée par « Préférences d'entraînement », destination native. La création de compte continue d'ouvrir la MISSION existante ; ce parcours ne se présente pas comme le Blueprint complet. Aucun champ sans API collecté.

```text
DISPONIBILITÉ · 1/2                 PRIORITÉS · 2/2
Retour           AUREN            Retour           AUREN
Ta disponibilité                  Tes priorités
Séances par semaine               Zones dans ton ordre de priorité
[Non déclaré] [1]...[7]*           [Non déclaré] [Sans priorité]
Familles de matériel              [Zone canonique : rang si choisie]*
[Non déclaré] [Aucun matériel]     Une sélection ajoute en fin de liste ;
[Barre][Haltères][Poulie]...*       un second appui la retire.
                                  Les autres rangs se recalculent.
[Continuer]                       [Enregistrer]
```

`*` : valeurs/libellés/bornes fournis par la ressource serveur existante, pas une taxonomie locale. Même AccountFrame, mêmes primitives et tokens que le compte accepté. Aucune durée, taille, expérience, contrainte médicale ou promesse d'allocation affichée. « Familles » ne devient pas une salle concrète. Les deux pages partagent une saisie en mémoire et n'envoient qu'un remplacement complet, après lecture préalable.

États : chargement avec retour ; lecture impossible → Réessayer, sans formulaire rempli de valeurs par défaut ; sauvegarde → commandes verrouillées ; refus → saisie conservée ; réponse perdue → « Enregistrement à vérifier », pas de répétition, action « Relire sur AUREN » ; résultat confirmé → « Préférences enregistrées sur AUREN » et retour Profil. Une relecture vérifie les valeurs actuelles, jamais l'origine d'une écriture ; la saisie reste disponible si elle diffère. Connexion expirée → reconnecter sans purge du journal. Retour/Android avec modifications non enregistrées : confirmation native de sortie ; aucun faux brouillon persistant.

### Brainstorming / Options / Risques / Choix retenu

Une longue page unique réduirait le nombre d'étapes mais mélangerait rythme et ordre des priorités. Reprendre les quatre moments Blueprint forcerait des champs sans contrats. Proposition ciblée : deux pages de préférences canoniques, indépendantes du premier plan. Coût : Blueprint complet reste à raccorder après contrats scientifiques ; bénéfice immédiat : une vraie déclaration native et reprenable après confirmation. Le modèle de formulaire/réseau peut être préparé sans code de composition pendant la revue de ce croquis.


Acceptation du croquis ciblé le 5 novembre : « Valider ce parcours ciblé ». Autorise la composition des deux pages décrites et leurs états ; le rendu réel reste à exposer avant commit UI.


## Ajustement des priorités — demande opérateur et validation visuelle déléguée

L'opérateur accepte le rendu puis demande de remplacer la liste verticale de grandes lignes par de petits blocs : « Tu le fais sans me demander, tu le valides. » Cette instruction précise vaut croquis pour ce seul ajustement et délègue sa revue visuelle à l'agent. Elle ne constitue pas une dispense générale de validation des autres écrans.

```text
Tes priorités
Les zones que tu souhaites privilégier.
[Non déclaré] [Sans priorité]
[Pectoraux]      [Épaules]
[Dos largeur]    [Dos épaisseur]
[1 · Bras]       [Bas du corps]
Choix facultatifs ; second appui pour retirer.
[Enregistrer]
```

La grille lit toujours les valeurs/libellés canoniques et affiche le rang déclaré. L'ordre ne devient pas un diagnostic de points forts/faibles ni un coefficient scientifique. La place de cette préférence parmi les observations/historiques sera définie par les futurs contrats du moteur, sans changer ici les règles existantes.
