# NUT-01 — vecteurs de contrat avant build

12novembre2026. Calcul des octets/hash avec les bibliothèques standards Python et JavaScript, pas test du futur produit NUT. Représentation millientière, protocole nutrition-canonical/1.0.0. Le préfixe est `NUT-CMD-1` suivi d’un seul LF avant le JSON ; pas de LF terminal. Les quatre vecteurs donnent les mêmes bytes/hash dans les deux outils.

## zero

```json
{"body":{"confirm_complete":null,"contract_version":"nutrition-command/1.0.0","expected_head_token":"0000000000000000000000000000000000000000000000000000000000000000","operation":"SET_FIELDS","request_id":"nut-contract-vector-1","target_ref":null,"timezone":"Europe/Paris","values":{"kcal_milli":0}},"method":"POST","namespace":"DAY","path":"/me/nutrition/days/2026-11-12/revisions"}
```

SHA256 préfixe+JSON : `81624acf1a2f7f57d63510c7d4a43e7b407963d473f88d72558ad55e4961cf5e`.

## limit

```json
{"body":{"confirm_complete":null,"contract_version":"nutrition-command/1.0.0","expected_head_token":"0000000000000000000000000000000000000000000000000000000000000000","operation":"SET_FIELDS","request_id":"nut-contract-vector-1","target_ref":null,"timezone":"Europe/Paris","values":{"protein_milli":999999999}},"method":"POST","namespace":"DAY","path":"/me/nutrition/days/2026-11-12/revisions"}
```

SHA256 préfixe+JSON : `eef88ddb5e52fc13a37788ed2c366d309128949b3c297c565f1a9be568b72c9a`.

## null-and-number

```json
{"body":{"confirm_complete":null,"contract_version":"nutrition-command/1.0.0","expected_head_token":"0000000000000000000000000000000000000000000000000000000000000000","operation":"SET_FIELDS","request_id":"nut-contract-vector-1","target_ref":null,"timezone":"Europe/Paris","values":{"fat_milli":1250,"kcal_milli":null}},"method":"POST","namespace":"DAY","path":"/me/nutrition/days/2026-11-12/revisions"}
```

SHA256 préfixe+JSON : `72544e11bedd46d138a75b59c69527768e6dd7283e99ab348fef0c2018164c6e`.

## absence-vs-null

```json
{"body":{"confirm_complete":null,"contract_version":"nutrition-command/1.0.0","expected_head_token":"0000000000000000000000000000000000000000000000000000000000000000","operation":"SET_FIELDS","request_id":"nut-contract-vector-1","target_ref":null,"timezone":"Europe/Paris","values":{"fat_milli":1250}},"method":"POST","namespace":"DAY","path":"/me/nutrition/days/2026-11-12/revisions"}
```

SHA256 préfixe+JSON : `e6e273f9c70a1bc8b998bc26f62ac0107126e3999a2f3e3b5d48cf321b480736`.

À reproduire dans les tests de production après GO : ordre des clés permuté donne le même canon ; absence et null ci-dessus ont des hash différents ; formatsfloat/exposant/bool/champs inconnus/doublons sont refusés avant canonicalisation, jamais convertis en commandes valides. Ces vecteurs ne valident pas leur futur transport, leur signature CAS ou leurs règles métier.
