# MOB-03 — déclarations d'entraînement, adaptateur mobile v1

Statut : implémenté localement, non déployé. Adaptateur du service canonique existant, pas nouvelle doctrine scientifique ni contrat complet BodyTrainingBlueprint.

## Ressource

`GET /api/mobile/v1/me/training-preferences/declarations` lit les faits du propriétaire Bearer. `PUT` remplace les trois déclarations héritées dans leur ensemble. Le cookie web seul ne donne aucun accès. Aucun user_id accepté dans le corps. La lecture minimale `/me/training-preferences` du bilan MOB-02 reste inchangée.

```json
{
  "sessions_per_week": null,
  "focus_priorities": null,
  "available_equipment": null
}
```

Les trois clés sont obligatoires au PUT, nullable, sans champ supplémentaire. Aucun booléen, flottant ou entier sous forme de chaîne à la place de la fréquence. Les validations, bornes structurelles, normalisation et libellés viennent uniquement de `app/services/training_preferences.py`.

- `null` = non déclaré ; `[]` = liste explicitement vide. Aucun défaut inventé.
- `focus_priorities` : ordre déclaré conservé, axes canoniques, doublons refusés. Aucun objectif de labo.
- `available_equipment` : familles, ensemble normalisé par le service. Ne décrit pas des objets concrets et ne permet pas d'inférer un banc, une salle complète ou une substitution.
- `available_equipment_items` : writer séparé existant, jamais modifié par ce PUT.

Réponse 200 : `contract_version: 1`, `declarations` (trois champs), `options` (bornes de fréquence et listes `{value,label}` canoniques pour priorités/familles). Aucune recommandation, mesure, confiance ou effet scientifique ajouté. Réponses de données `Cache-Control: no-store`. Une répétition séquentielle du même PUT retrouve une seule ligne, sans append d'événement. Les écritures concurrentes suivent le service existant ; aucun verrouillage optimiste multiclient revendiqué.

Refus métier : 400 `invalid_training_preferences`, sans valeur soumise dans le message. Schéma incomplet/invalide : 422 sanitisé, sans `input` ou `ctx`. Sans Bearer valide : 401. Les en-têtes no-store des erreurs génériques 400/401 restent une limite héritée distincte des réponses de données ; constat mineur de revue consigné.

## Consommateur TypeScript préparé

`TrainingPreferencesClient.read/save` retourne `confirmed(value)`, `rejected(code)`, `unknown` ou `cancelled`. Le client ne possède ni cache ni outbox. Une version non reconnue ou un payload illisible ne devient pas une confirmation. Les résultats d'une identité quittée sont annulés. Les éditions du brouillon après soumission ne changent pas le payload capturé. Une seconde écriture pendant la première est refusée avec `request_in_flight`.

Authentification renouvelable avant envoi ; **aucun replay du PUT** après 401 ou réponse incertaine. Après timeout/5xx, état inconnu ; une lecture explicite permet de comparer les faits actuels, sans affirmer qu'elle prouve l'origine d'une écriture. Aucun retry automatique ne remplace les déclarations d'un autre appareil.

Cet adaptateur n'est pas encore raccordé au formulaire Blueprint réel. Durée, expérience, taille, poids daté/consentement et limitations ne sont pas introduits par cette ressource. SCI-P01/P02 et la politique d'effacement restent ouverts.
