## ADDED Requirements

### Requirement: Qualified selective catalogue admission

Le lecteur SHALL admettre une vue sélective d'un catalogue intégralement attesté uniquement après vérification complète de sa forme et des plafonds inchangés, selon l'exception éditoriale explicite proposée. Le GO BUILD exact du26novembre2026 autorise ce correctif sans activation ; la qualification et l'activation gardent leurs preuves propres.

#### Scenario: Canonical editorial note exceeds generic string ceiling
- **WHEN** le catalogue attesté contient sa note de4302octets au chemin de curation admis
- **THEN** la future vue spécialisée SHALL conserver identités, rôles, exécutions et digests, sans tronquer le JSON ni relever la borne générique4096

#### Scenario: Scientific or retained string exceeds its ceiling
- **WHEN** un champ hors de la seule exception dépasse son plafond
- **THEN** le lecteur SHALL refuser l'admission sans fabriquer un résultat EXACT

### Requirement: Runtime qualification remains profile-specific

La qualification SHALL porter sur l'image, le profil de sources et les limites Linux réellement exécutés ; une preuve sur Mac, un autre Python ou un profil superposé SHALL rester distincte du runtime QA inchangé.

#### Scenario: Faithful disposable runtime unavailable
- **WHEN** le moteur de conteneurs ne répond pas ou la cible exacte ne peut pas être reproduite
- **THEN** le reçu SHALL conserver RUNTIME HOLD avec les écarts et les mesures non exécutées

#### Scenario: Limits or trust prerequisites fail
- **WHEN** un plafond, l'isolation propriétaire, le snapshot ou la confiance des chemins n'est pas démontré
- **THEN** le lecteur SHALL rester NOT_QUALIFIED et désactivé, sans élargissement de budget ou activation implicite
