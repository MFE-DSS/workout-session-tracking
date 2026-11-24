# UX11 — une information, une source

| Élément | Source existante | Ce qu’il ne prouve pas |
| --- | --- | --- |
| Exercice/série | ExecutionV3 session/binding/mapping/cursor, workPositionV3 | Aucun programme actif inventé |
| Prescription | exercise.prescription.dose, affichage canonique conservé | Le fait précédent ne prescrit rien |
| Référence17,5/9 | détail propriétaire SCI validé, sets[40].observation.setting/reps, revision1 | Pas réglage conseillé ni capacité |
| Appareil/unité/côté | ContextKey exact et Setting.kind/unit ; strict même contexte enregistré | Kg affichés ≠ masse totale |
| Source/version | session/se/set, binding, revision, server_now du détail ; read_id/rows_read_at séparés pour l’index ; date/estimated explicites | Pas d’op_id ni flag adjusted inventés |
| Brouillon courant | state local React déjà utilisé pour l’édition V3 ; vide au changement de série | Aucun fait tant que non enregistré |
| Validation | callback canonique recordFact + eventTime | Pas de nouvelle autorité de temps |
| Local/pending/refus/ACK | local_facts et localOperations canoniques ; pending/unknown réseau regroupés « Envoi à vérifier » ; aucune priorité locale dans la référence | ACK ≠ fait courant relu |
| Fait actuel relu | GET propriétaire validé pour le set soumis et sa révision | Pas de lecture construite depuis le draft |
| Repos/setup/prochaine action | workPermissionV3 et contrôleur existants | La référence n’autorise aucune suite |

Un seul porteur primaire par valeur. Les identités détaillées sont consultables, sans double numérique dans le header. La référence n’apparaît pas si une des conditions manque.
