# SCI-SNAPSHOT-READS-01 — lectures répétées bornées

## Why
Le paquet exact 1f81d5b8 refuse la fixture structurelle100 V3 au budget SQL4096 après67 graphes. Le catalogue n'est parsé qu'une fois ; les mêmes évaluations et autorité sont relues. Les refus historiques sont conservés.

## What Changes
Réutiliser les présences de tables internes, évaluations par identité et autorité runtime dans une seule capture read-only. Valeurs indépendantes, stockage borné, aucun partage entre captures ou propriétaires, fin de capture libérant les valeurs. Aucun changement de comportement SCI ou DTO ; skip_specs est réservé à cette optimisation interne sans nouvelle politique.

## Non-goals
Aucun writer, SCI, TIME-01, DTO, plafond, mobile, déploiement ou nouvelle image. Pas de promesse de lecture complète pour toute forme d'historique100.
