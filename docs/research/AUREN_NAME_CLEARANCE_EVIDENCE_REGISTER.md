# AUREN — Name Clearance — Evidence Register

**Type** : registre de preuves — recherche préliminaire, **PAS un avis juridique**
**Date de collecte** : 2026-07-15 (UTC ~19:24Z)
**Environnement** : session automatisée sans navigateur ; accès réseau limité (RDAP domaines
fonctionnel ; APIs marques officielles **non exploitables** en JSON → `MANUAL CHECK REQUIRED`).
**Méthode** : requêtes RDAP directes aux registres officiels (IANA bootstrap). Aucun agrégateur
non vérifié utilisé en substitution d'une source officielle. Aucune donnée personnelle privée
committée (registrant redacted = laissé redacted).

---

## A. Domaines — RDAP (données officielles vérifiables)

Chaque ligne = réponse RDAP réelle du registre faisant autorité pour le TLD, horodatée
2026-07-15T19:24Z. `cree`/`expire` = eventDate RDAP (registration/expiration).

| # | Domaine | Source RDAP (registre) | Résultat | Registrar | Créé | Expire | Confiance |
|---|---|---|---|---|---|---|---|
| D1 | auren.com | rdap.verisign.com/com | **ENREGISTRÉ** | OVH sas | 1998-04-27 | 2027-04-26 | haute |
| D2 | auren.net | rdap.verisign.com/net | **ENREGISTRÉ** | OVH sas | 2001-11-23 | 2026-11-23 | haute |
| D3 | auren.org | rdap.publicinterestregistry.org | **ENREGISTRÉ** | OVH sas | 2001-11-23 | 2026-11-23 | haute |
| D4 | auren.fr | rdap.nic.fr | **ENREGISTRÉ** | OVH | 2011-09-26 | 2026-09-26 | haute |
| D5 | auren.ch | rdap.nic.ch | **ENREGISTRÉ** | (registrar n/c) | 2015-01-21 | n/c | moyenne |
| D6 | auren.eu | rdap.eurid.eu | **MANUAL CHECK REQUIRED** (RDAP non-JSON/bloqué) | — | — | — | — |
| D7 | auren.io | rdap.identitydigital / Cloudflare | **ENREGISTRÉ** | Cloudflare, Inc. | 2025-01-16 | 2027-01-16 | haute |
| D8 | auren.app | pubapi.registry.google/rdap | **ENREGISTRÉ** | Namecheap Inc. | 2024-11-28 | 2026-11-28 | haute |
| D9 | auren.fit | rdap.nic.fit | **ENREGISTRÉ** | Name.com, Inc. | 2026-02-20 | 2027-02-20 | haute |
| D10 | auren.health | rdap.nic.health | **ENREGISTRÉ** | GoDaddy.com, LLC | 2025-05-30 | 2027-05-30 | haute |

### Fallbacks

| # | Domaine | Source | Résultat | Registrar | Créé | Confiance |
|---|---|---|---|---|---|---|
| F1 | getauren.com | rdap.verisign.com/com | **ENREGISTRÉ** | NameCheap, Inc. | 2026-06-23 | haute |
| F2 | useauren.com | rdap.verisign.com/com | **ENREGISTRÉ** | Name.com, Inc. | 2026-05-12 | haute |
| F3 | aurenapp.com | rdap.verisign.com/com | **ENREGISTRÉ** | GoDaddy.com, LLC | 2025-10-03 | haute |
| F4 | aurenfitness.com | rdap.verisign.com/com | **ENREGISTRÉ** | Tucows Domains Inc. | 2026-04-07 | haute |
| F5 | aurenperformance.* | — | **NON TESTÉ** (à vérifier) | — | — | — |

**Observations factuelles** :
- Le cluster `.com/.net/.org/.fr` partage le registrar **OVH** avec des créations anciennes
  (1998–2011) → titulaire unique établi de longue date, probablement une entité européenne.
- Registrant `auren.com` = **redacted** (privacy/RGPD) ; nameservers = Cloudflare. Identité du
  titulaire **non confirmée par RDAP** → `MANUAL CHECK REQUIRED` pour l'identité exacte.
- Les fallbacks « défensifs » (`getauren`, `useauren`, `aurenapp`, `aurenfitness`) sont **tous
  déjà enregistrés** et **très récents (2025–2026)** → soit squatting/anticipation, soit acteurs
  tiers actifs sur le terme « Auren » dans un contexte app. À investiguer.

## B. Marques — MANUAL CHECK REQUIRED (accès API non disponible)

Les bases marques officielles n'ont **pas** pu être interrogées de façon structurée dans cet
environnement (pas de navigateur JS ; TMview API a renvoyé HTTP 000 ; WIPO BrandDB / EUIPO eSearch
sont des SPA nécessitant un rendu). **Aucune recherche marque n'a été substituée par un agrégateur.**

| Base officielle | Territoire | Requête à exécuter | Statut |
|---|---|---|---|
| EUIPO eSearch Plus | UE | « AUREN » verbal + fuzzy, cl. 9/41/42/44 | **MANUAL CHECK REQUIRED** |
| INPI (data.inpi.fr) | France | « AUREN » + variantes | **MANUAL CHECK REQUIRED** (HTTP 403 direct) |
| WIPO Global Brand DB / Madrid | International | « AUREN » désignant FR/EU/CH | **MANUAL CHECK REQUIRED** |
| Swissreg | Suisse | « AUREN » | **MANUAL CHECK REQUIRED** |
| TMview | multi-office | « AUREN » exact + similarité | **MANUAL CHECK REQUIRED** (API 000) |
| UKIPO / USPTO / CIPO | UK/US/CA (priorité 2) | « AUREN » | **MANUAL CHECK REQUIRED** |

## C. Sociétés / usages commerciaux — observation non vérifiée

**Signal connu (à confirmer par source officielle, NON committé comme fait juridique)** : « Auren »
est le nom d'un **réseau international d'audit / conseil / expertise-comptable** (activité
professionnelle B2B), présent notamment en Europe (Espagne, France…). Ceci expliquerait le cluster
domaine OVH ancien. **Classe d'activité probable = conseil/audit (Nice 35/36), distincte du
logiciel fitness (9/42/44)** → proximité produit *a priori* faible, mais la notoriété d'un signe
peut élargir la protection. **À vérifier via registres officiels (INPI/Zefix/EUIPO) — MANUAL CHECK.**

| Entité | Pays | Activité | Usage d'Auren | Source | Statut |
|---|---|---|---|---|---|
| « Auren » (réseau audit/conseil) | ES/FR/EU (à confirmer) | audit/conseil B2B | raison sociale + marque probable | observation publique | **MANUAL CHECK REQUIRED** |

## D. App stores / handles — MANUAL CHECK REQUIRED
App Store / Google Play / GitHub / LinkedIn / Instagram / X / YouTube / TikTok : **non interrogés**
(pas d'accès applicatif fiable). À exécuter manuellement pour collision app fitness/santé.

---

*Fin du registre de preuves. Toute case `MANUAL CHECK REQUIRED` doit être complétée par un humain
ou un CPI avant toute décision de dépôt. Les données domaine (section A) sont des réponses RDAP
officielles horodatées et réutilisables.*
