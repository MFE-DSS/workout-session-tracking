# Espace local — suppression bornée proposée, non exécutée

27 novembre 2026. Seuil opérateur :20Gio disponibles avant acquisition/transfert. Relevé frais :18,63Gio disponibles. Le VPS passe déjà ses bornes ; cette proposition concerne uniquement le Mac.

## Inventaire exact
28entrées recensées dans le fichier privé [DISK_CLEANUP_EXACT_INVENTORY.private.json](/Users/martinfeldmann/auren-review/sci-ops-qualify-01-evidence-20261127/execution-20261127/DISK_CLEANUP_EXACT_INVENTORY.private.json), avec chemin, propriétaire, inode/device, date et volume alloué. Total observé :1,914Gio alloués, sans garantie de récupération identique en présence de blocs partagés.

| Emplacement | Suppression proposée | Nature |
|---|---|---|
| `/Users/martinfeldmann/.npm/_npx` | Seulement les19sous-dossiers inventoriés | Copies téléchargées de CLI : eas-cli, expo, playwright, etc. Une prochaine invocation peut les retélécharger. |
| `/Users/martinfeldmann/.cache/uv` | Seulement les7sous-dossiers inventoriés | Cache de paquets Python ; environnements installés distincts conservés. |
| `/Users/martinfeldmann/Library/Caches/pip` | Le dossier inventorié | Cache de téléchargements Python, environ61Mio. |
| `/Users/martinfeldmann/.npm/_cacache` | Le dossier inventorié | Cache de téléchargements npm, environ71Mio. |

## Contrôle avant suppression, après accord uniquement
Recontrôler les IDs, chemins, propriétaires, liens et processus/cwd/fichiers ouverts. Ne jamais afficher les arguments ou environnements bruts des processus. Si une entrée est devenue utilisée ou a changé d'identité, la conserver et rapporter l'écart. Ne suivre aucun symlink hors de ces racines ; supprimer seulement les entrées listées, pas de glob ni prune. Mesurer le gain réel et réévaluer le seuil20Gio ; s'il reste insuffisant, conserver HOLD sans élargissement automatique.

Aucun worktree, node_modules partagé, preuve, archive d'image, base, secret, simulateur ou conteneur ne fait partie de cette proposition. Les trois node_modules BODY/NUT/MOB06 inspectés sont des liens partagés et sont exclus.

## Décision requise
Autoriser seulement les28entrées de cache inventoriées et les contrôles ci-dessus. Cet acte ne permet aucune suppression d'anciennes preuves ni d'autres fichiers. Aucune suppression n'a encore été effectuée.
