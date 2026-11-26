# AUREN — SCI BUILD-01 : amendement minimal du scope sécurité CI

25 novembre 2026 — Europe/Paris. **Proposition du25novembre conservée ; ACCEPTÉE par acte opérateur du26novembre2026 et appliquée dans sa seule portée.**

PR : https://github.com/MFE-DSS/workout-session-tracking/pull/446
HEAD : `dc6b79f8f3e3aa43a27323d8e1aa7441710a13e5` ; parent `1f0122bf4f2d30f7c95d4975b5994d1453363bc5`.
Run : https://github.com/MFE-DSS/workout-session-tracking/actions/runs/45704937761
Job lint :139524393824, step « gitleaks scan (required — Sb_26.4) » : **FAIL**, generic-api-key, deux résultats, SOURCE_PINS.json lignes9 et10. Les autres contrôles de ce job déjà exécutés (Ruff/budget/Bandit/actionlint/shellcheck/pip-audit) ont réussi.

## Diagnostic vérifié

Les deux valeurs sont exactement les SHA256 des fichiers canoniques `app/routers/mobile_api.py` et `app/services/device_auth.py` au parent1f0122bf. Leur égalité aux octets Git a été recalculée. Ce ne sont pas des clés API. Le scanner réagit aux mots api/auth dans les clés JSON immédiatement suivis des empreintes.

Le scan local initial par stdin n’avait pas révélé ces occurrences. Le scan local **du même historique Git que la CI** les reproduit. Une copie de la liste d’exceptions existante, enrichie uniquement des deux fingerprints ci-dessous, passe ce même scan (0finding). La vraie `.gitleaksignore` reste inchangée.

## Amendement demandé

Autoriser l’ajout à `.gitleaksignore` de **ces deux occurrences historiques exactes uniquement**, avec la justification source-SHA256. Aucun ignore de fichier, aucune règle désactivée, aucun seuil changé. Les autres findings restent bloquants. Ce fichier n’appartient pas à la liste de fichiers du BUILD_SCOPE initial ; l’instruction opérateur exige donc un amendement avant apply.

Pour éviter de recréer le même faux positif dans les futurs reçus, la présentation documentaire de SOURCE_PINS pourra passer de clés chemin→hash à des lignes source_ref/sha256, en conservant les112empreintes et leur portée historique. Aucun contrat runtime ni code produit n’est modifié par ce format.

```diff
diff --git a/.gitleaksignore b/.gitleaksignore
--- a/.gitleaksignore
+++ b/.gitleaksignore
@@ -1,3 +1,7 @@
 # Reviewed Git revision in the product brief, not a credential.
 # Exact historical occurrence only; scanner rules and other findings remain active.
 640e5bafdf63ac051e1ecf6cd757ff4071d76732:docs/MOBILE_UIUX_PO_DESIGNER_BRIEF_2026_11_05.md:generic-api-key:8
+
+# Reviewed public source-file SHA256 values, not credentials. Exact historical occurrences only.
+dc6b79f8f3e3aa43a27323d8e1aa7441710a13e5:openspec/changes/sci-readiness-01-build-01/SOURCE_PINS.json:generic-api-key:9
+dc6b79f8f3e3aa43a27323d8e1aa7441710a13e5:openspec/changes/sci-readiness-01-build-01/SOURCE_PINS.json:generic-api-key:10
```

## Après accord

Appliquer le patch exact, relancer le scan historique, vérifier les contrôles sur le nouveau HEAD et ne merger qu’après CI protégée complète. Aucun bypass, force-push, nouvelle baseline ou activation.

Le lecteur reste **désactivé / qualification opérationnelle HOLD** pour la raison séparée4302octets >4096 dans le catalogue réel et l’absence de profil d’image qualifié. Aucun VPS, donnée personnelle, APK ou OTA concerné.

Décision bornée proposée : **« Autoriser les deux exceptions historiques SHA256 et le format documentaire SOURCE_PINS »**.


## Acte reçu le26novembre2026

Référence `SCI-BUILD01-SCOPE-AMENDMENT-2026-11-26` : « J’autorise les deux exceptions historiques exactes proposées […] ainsi que la normalisation documentaire de SOURCE_PINS.json en conservant les112empreintes. » Les112SHA256 ont été recalculés sur les octets Git du parent1f0122bf avant apply ; aucune différence. Deux fingerprints, aucun wildcard, aucune règle désactivée. Les deux blocages opérationnels restent distincts ; le lecteur demeure désactivé. La suite historique ci-dessus décrit la proposition et son essai avant accord, sans réécriture de la chronologie.
