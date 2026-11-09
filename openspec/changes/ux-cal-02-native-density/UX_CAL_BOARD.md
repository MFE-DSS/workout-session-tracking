# UX-CAL-02 — composition G1 avant / après proposée

**G1_PENDING, aucun code produit nouveau.** Cette planche ASCII décrit le
changement de composition. Elle n'est ni un rendu natif après, ni la validation
des pixels à venir. Les références avant restent intactes :
[entrée388](../../../clients/mobile/visual-contract/review-receipts/plan-cal-01/native/ios-home.png),
[machine388](../../../clients/mobile/visual-contract/review-receipts/plan-cal-01/native/ios-final-machine.png),
[haltères388](../../../clients/mobile/visual-contract/review-receipts/plan-cal-01/native/ios-rdl-setting.png).

## Croquis validé

**En attente de décision opérateur.** Une composition commune appliquée aux sept
réalisations, mêmes primitives et valeurs réelles ; aucune illustration ajoutée.
Le dessin n'impose pas une hauteur fixe quand la fonte exige plus de place.

### Entrée : même fonctionnalité, priorité courante

```text
AVANT — référence388                  APRÈS — proposition390pt
┌──────────────────────────┐         ┌──────────────────────────┐
│ Retour       AUREN       │         │ Retour       AUREN       │
│ Ton premier              │         │ Ton calibrage            │
│ entraînement             │         │ Une rencontre à la fois. │
│                          │         │                          │
│ Paragraphe explicatif    │         │ Chest press              │
│ sur plusieurs lignes     │         │ Observation conservée    │
│                          │         │                          │
│ [Découvrir un appareil]  │68       │ [ Reprendre ]            │48+
│ Reprendre ma rencontre   │         │ Choisir un mouvement     │48+
│ Vérifier réglages · plan │         │                          │
│ Ajouter réglage observé  │         │ Aide       Détails       │48+
│ Disponibilités           │         └──────────────────────────┘
│ Relire / Préférences…    │         Sans rencontre : Commencer le
└──────────────────────────┘         calibrage, sans charge suggérée.
                                    Détails : mêmes destinations réelles,
                                    pending/alertes restent immédiats.
```

### Réglage : un instrument, machine / par haltère

```text
AVANT                                APRÈS — même contexte, même saisie
┌──────────────────────────┐         ┌──────────────────────────┐
│ Titre étape              │         │ Ton réglage       Aide   │
│ ┌ Frame C ─────────────┐ │         │ ┌ Frame C ─────────────┐ │
│ │ Nom exercice grand  │ │         │ │ Chest press           │ │
│ │ Statut              │ │         │ │ Machine A · lieu réel │ │
│ │ Définition calibrage│ │         │ │ ┌RecessedWindow─────┐ │ │
│ │ Historique détaillé │ │         │ │ │ Ton choix         │ │ │
│ │ Lien procédure     │ │         │ │ │ 17  kg affichés   │ │ │
│ │ ┌ Réglage ───────┐ │ │168      │ │ └───────────────────┘ │ │112+
│ │ │ Valeur         │ │ │         │ │ Tu choisis un réglage │ │
│ │ │ Unité          │ │ │         │ │ réellement disponible.│ │
│ │ └────────────────┘ │ │         │ │ [ Confirmer ]         │ │48+
│ │ Message explicatif │ │         │ │ Pause · Signaler      │ │48+
│ │ [Confirmer...]     │ │68       │ │ Historique · Détails  │ │48+
│ │ Pause/retrait/…    │ │         │ └───────────────────────┘ │
│ └─────────────────────┘ │         └──────────────────────────┘
└──────────────────────────┘         Exemple haltères : même module,
                                    8 kg par haltère, jamais16kg total.
```

17 et8 sont des saisies synthétiques nommées pour la comparaison, jamais des
valeurs proposées par AUREN. Champs vides au premier usage. Réglage utilisé
après essai = autre saisie ou confirmation humaine explicite, jamais copie.

### Déclinaisons communes des étapes

| Étape | Information principale | Action dominante | Accessible immédiatement / à la demande |
|---|---|---|---|
| Choix/reprise | Mouvement sélectionné, faits conservés | Reprendre ou Préparer | Aide avant ouverture ; autre mouvement |
| Contexte | Lieu, appareil, disponibilité/préoccupation déclarées | Confirmer | UNKNOWN explicite ; aide/retour |
| Préparation | Notice et setup réellement rapportés | Confirmer | Procédure de ce seul exercice ; pause |
| Réglage | Choix vide ou valeur/unité saisie | Confirmer | Stop/préoccupation et aide ; aucun incrément |
| Familiarisation | Même réglage et contexte | Confirmer contexte puis familiarisation, selon serveur | Changer réglage, aide, pause ; jamais deux dominants concurrents |
| Essai | Même réglage, repère8–12 avec réserve et arrêt libre | Commencer l'essai si permis | Stop/préoccupation ; limite subjective conservée |
| Observation1 | Réglage utilisé/reps/complétion/réussite | Continuer, local seulement | Aucune valeur par défaut ; fait passé possible |
| Observation2 | Qualité/gêne/motif/date | Enregistrer | Retour corrige1 ; passé/inconnu explicitement disponibles |
| Décision | Réglage réellement observé, provisoire | Accepter si permis, ou retry si permis | Résumé factuel compact ; détail/historique |
| QUALIFIED | Provisoire, jamais optimal | Revenir au choix/reprise | Détail des faits ; aucun travail créé par le calibrage |
| Préoccupation/retrait/inconnu | Motif et absence de nouvelle consigne | Relire si pertinent | Pause/sortie/faits passés, pas de retry interdit |
| Pending/erreur | Réponse à vérifier, faits préservés | Réconcilier même action | Pas de succès/refus inventé |

L'accord temporel exact et le handoff vers la séance restent ceux de388 : pas de
nouvelle composition ni de clic d'aide valant acquittement.

## Inventaire — une information, une seule fois

| Élément | Information | Source (contrat de données) | Doublon ? |
|---|---|---|---|
| Titre d'étape | Étape UI, pas permission physique | CalibrationDraft.stage / sous-écran local | non |
| Exercice | Identité sélectionnée | capacités supported_realizations recoupées au profile et progress.context | non |
| Contexte compact | Dispositif et lieu déclarés | progress.context.equipment_ref/context_ref ou formulaire de contexte avant ouverture | non |
| Réglage | Choix ou fait utilisé selon étape | form.load / observedLoad / dernier ATTEMPT_OBSERVED, jamais interchangeables | non |
| Unité | Affichage machine ou par haltère | profil négocié + load_semantics/context | non |
| Statut | Décision SCI actuelle et limite provisoire | result.state / authority / allowed_actions | non |
| Historique déplié | Faits anciens, pas permission | progress.observations et reported_stop_reasons | non |
| Choix factuels | Rapports distincts sans défaut | CalibrationDraft puis payload observation existant | non |
| Aide | Commun + réalisation + arrêt applicables | protocol_material source_ref/sha256/texte contrôlés | non |
| Commande dominante | Mutation permise ou navigation locale explicite | allowed_actions + gates existantes / action locale sans effet serveur | non |
| Reprise | Rencontre possédée et brouillon | source.encounter_ref, calibration_drafts, reçu exact | non |
| Incertitude / pending | État courant sans autorité inventée | result null / source.pending / outcome réel | non |

## Comparaison avec la référence validée

| Référence validée | Tranche / date | Ce qui doit survivre | Survit ? |
|---|---|---|---|
| Instrument partagé machine/haltères | PLAN-CAL-01 /9nov | Frame C, RecessedWindow, NumericReadout, unités et faits | exigé au build, pas encore rendu |
| Marque et tokens | AUREN Visual Contract | Géométrie, rôle et couleurs existants | read-only |
| MISSION/exécution/ack | Baselines acceptées | Aucun changement visuel dans ce scope | read-only |
| Saisie et pause/retrait | Receipt388 | Aucune acceptation implicite ; faits/histoire conservés | tests consommateurs requis |

## Changement unique de l’itération

Recomposition bornée soumise à G1 ; les demandes du mandat seront montrées
séparément dans le board final : densité/CTA, hiérarchie, aide, groupes factuels,
états de reprise. La partie décodage est une correction comportementale séparée
dans les tests et la revue, jamais cachée comme CSS.

Demandes citées : « One dominant action per stage », « Reduce visible density,
not factual accuracy », « Secondary explanations accessible on demand »,
« Never remove uncertainty or an explicit acknowledgment required by the
scientific contract ». Avant = receipt388 ; après = croquis présent, pixels
réels ultérieurs à accepter. Aucun après natif ou baseline nouvelle prétendu.
