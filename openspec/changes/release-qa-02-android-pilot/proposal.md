# RELEASE-QA-02 — APK Android interne attesté

## Why

Le mandat du10novembre demande un vrai APK de la vraie application, avec ses modules natifs. ExpoGo58.0.5 ne contient pas ExpoTopicSubscriptionModule. Le package verrouillé expo-notifications58.1.6 contient pourtant son implémentation Android Kotlin et son consommateur JS ; ils ne seront pas supprimés. Base canonique b8f5ffc2d6671521cbc276ab87397540aed60bb7.

## What Changes

Profil EAS QA autonome/internal/APK distinct du profil pilot public. Identité Android QA distincte, HTTPS temporaire vers le seul banc synthétique (direction testeur distant reçue avec le GO), attestation des révisions/configurations et test de composition native. Backend neuf propriétaire loopback, passerelle API bornée, base synthétique migrée, vrais loaders SCI et flags contrôlés. Pas de dépendance USB/Metro dans l'APK distant. Recette physique à retourner par le bêta-testeur, aucun Android personnel disponible à l'opérateur. Produire APK/build ID/signature/empreintes, checklist courte et résultats séparés PASS/FAIL/UNAVAILABLE.

## Impact

GO du delta de configuration reçu le10novembre : « Autoriser ce build RELEASE-QA-02 contrôlé », avec précision de testeur distant. Pas de plugin cleartext dans le build effectif ; revue de la passerelle avant exposition API. Aucun nouveau GO routinier de merge. Aucune nouvelle composition visible : primitifs, pixels, SCI, contrats et baselines inchangés. Un correctif UI éventuel requerra son rendu/gate applicable.

Hors scope : mise à niveau SDK/RN, suppression de notifications, production ou backend partagé, Store/OTA, données personnelles, nouveaux produits MOB04/05/BODY/NUT, modifications de migrations ou de politique SCI. Absence d'Android physique ne sera pas remplacée par une capture émulateur.
