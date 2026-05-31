# SPIGNOS — Coach Report v2 — LLM Narrative Encadré (Sx_25)

**Date :** 2026-05-31
**Type :** SPEC ONLY — extension de Sb_23 (Coach Report v1) avec une couche narrative encadrée par LLM.
**Prérequis :** Sb_23 livré (`e99f776`), Sx_24 spec livrée (couplage signaux implicites).
**Successeur build :** Sb_25 (lotté).
**Version :** v2 (v1 = Sb_23 Coach Report SSR + print A4, livré).

---

## A. Pourquoi cette spec

Sb_23 Coach Report v1 livre une synthèse 10 blocs lisible en 2 min, avec tags `Mesuré` / `Inféré` / `Non déductible`. Retour dogfooding N7 : **manque une couche narrative qualitative** qu'un coach humain produirait naturellement (résumé textuel des progrès, mise en relation des indicateurs, axes prioritaires synthétisés).

L'utilisateur a demandé qu'un LLM joue ce rôle. **Risque immédiat** : un LLM "qui joue le coach" peut franchir les 4 interdits stricts Sx_23 §B.bis (esthétique / pronostic morphologique / verdict performance max / comparaison inter-users) sans s'en rendre compte.

Sx_25 répond en posant un **contrat structurel** sur ce que le LLM peut produire (et **uniquement** ça), et un **fallback sans LLM** pour que la feature reste utilisable hors-ligne ou si l'API tombe.

## B. Périmètre fonctionnel

| Élément | V1 (Sb_23) | V2 (Sb_25) |
|---|---|---|
| Page `/coach-report` SSR | ✅ | ✅ inchangé |
| 10 blocs structurés | ✅ | ✅ inchangé |
| Tags `Mesuré`/`Inféré`/`Non déductible` | ✅ | ✅ inchangé |
| Bouton "Imprimer" (navigateur → PDF) | ✅ | ✅ inchangé |
| CSS print A4 | ✅ | ✅ inchangé |
| **Couche narrative LLM** | ❌ | ✅ **NEW** — encadré (§D) |
| **PDF natif server-side** | ❌ | ❌ **toujours hors V2** |
| **Comparaison vs autre user** | ❌ | ❌ **toujours interdit** |
| **Partage URL signée** | ❌ | ❌ hors V2 (V3 si besoin) |

**Décision verrouillée** : pas de génération PDF côté serveur (weasyprint, ReportLab, etc.). Le support principal reste **SSR + Imprimer navigateur**. Argument : le navigateur produit déjà un PDF correct via "Imprimer en PDF", et garder le rendu côté client réduit la surface de complexité (pas de dépendance OS, pas de gestion de polices, pas de cache PDF à gérer).

## C. Contrat dur — ce que le LLM peut et ne peut PAS faire

### C.1 — Garde-fous hérités de Sx_23 §B.bis (rappel verrouillé)

Le LLM **ne doit jamais** produire :

1. **Jugement esthétique** : "bel équilibre", "physique harmonieux", "silhouette équilibrée", etc.
2. **Pronostic morphologique** : "vous prenez de la masse", "vous perdez du gras", "votre composition corporelle évolue vers…"
3. **Verdict de performance maximale** : "vous êtes fort en X", "votre niveau de Y est faible", "votre 1RM estimé est…"
4. **Comparaison inter-users** : "top 20 %", "supérieur à la moyenne SPIGNOS", "comparé aux autres utilisateurs…"

Ces 4 classes sont **enforcées par 3 mécanismes complémentaires** (§D.3).

### C.2 — Ce que le LLM peut faire

| Type d'énoncé | Autorisé ? | Exemple OK |
|---|---|---|
| Reformuler un fait Mesuré | ✅ | "Vous avez complété 12 séances sur les 30 derniers jours" |
| Mettre en relation 2 Mesurés | ✅ | "Cette régularité (3 séances/sem moyenne) coexiste avec une streak de 5j actuelle" |
| Souligner un Inféré (toujours conditionnel) | ✅ | "Les données suggèrent une concentration sur le push horizontal (35 % des sets)" |
| Reformuler une lacune (Non déductible) | ✅ | "L'absence de mesure de masse maigre limite ce que ce rapport peut conclure sur la composition corporelle" |
| Suggérer un axe d'entraînement structuré | ✅ conditionnel | "Vous pourriez explorer 2 séances Legs/sem sur 4 semaines pour rééquilibrer" |
| Donner un avis nutrition / supplément | ❌ | hors périmètre santé |
| Donner un diagnostic médical | ❌ | hors compétence et illégal |
| Affirmer un état émotionnel | ❌ | "vous semblez démotivé" ; basé sur quoi ? |

### C.3 — Vocabulaire imposé

Le LLM **doit** utiliser systématiquement les marqueurs de conditionnel suivants :

- "suggèrent", "indiquent", "pourraient", "semblent"
- "selon les données saisies"
- "sous réserve de vérification par un coach humain"
- "ce rapport ne remplace pas un avis médical"

Le LLM **ne doit pas** utiliser :

- "Tu es / vous êtes" + verdict (fort, faible, en forme, fatigué…)
- "Tu vas / vous allez" + pronostic
- "Mieux que / moins bien que" + comparatif inter-personnes
- "Manifestement", "clairement", "évidemment"

## D. Architecture de l'encadrement

### D.1 — Format de sortie LLM = JSON structuré (pas freeform)

Plutôt que de demander au LLM "écris un paragraphe", on l'appelle avec une **demande de sortie JSON structurée**. Chaque champ a une **longueur maximale** et une **règle sémantique** documentée.

```json
{
  "one_line_summary": "string, max 200 chars",
  "block_narrations": {
    "volume": "string, max 250 chars",
    "ratio": "string, max 250 chars",
    "zones": "string, max 250 chars",
    "patterns": "string, max 250 chars",
    "discipline": "string, max 250 chars"
  },
  "key_insight": "string, max 300 chars — UNE observation qui met en relation 2+ blocs",
  "suggested_focus_next_period": "string, max 250 chars — UN axe principal pour les 30 prochains jours",
  "limitations": "string, max 250 chars — rappel de ce que le rapport NE peut PAS conclure"
}
```

Avantages :
- Validation triviale côté serveur (longueur, présence des champs)
- Pas de pseudo-paragraphes incontrôlés
- Chaque champ est rendu dans un emplacement dédié de la page (pas de free-floating texte)
- Le `limitations` field est **obligatoire** — force le LLM à acknowledger ses limites à chaque génération

### D.2 — Prompt système verrouillé

Le system prompt envoyé au LLM est **constant**, versionné dans `data/coach_llm_system_prompt.txt` (modifiable hors code), et contient :

1. Rôle : "Tu es un assistant d'analyse pour SPIGNOS. Tu n'es PAS un coach."
2. Contrat de sortie : JSON conforme au schéma §D.1
3. Liste explicite des 4 interdits §C.1
4. Liste du vocabulaire imposé / interdit §C.3
5. Note : "Si la donnée d'entrée est trop pauvre pour conclure, écris-le dans `limitations` au lieu de combler avec de l'interprétation"
6. Few-shot examples : 2-3 cas typiques avec sortie attendue

### D.3 — Triple mécanisme d'enforcement

| Mécanisme | Couche | Cas couverts |
|---|---|---|
| **1. Structured output (JSON schema)** | Pré-génération (côté API) | Champs manquants, types invalides, longueurs hors limites |
| **2. Keyword blacklist post-génération** | Server-side après réponse LLM | Détecte les mots/expressions interdits (§C.1, §C.3). Si match → rejet de la sortie, fallback §D.4 |
| **3. Tests unitaires sur prompt + parsing** | CI | Battery de réponses LLM mockées vérifie que la validation fonctionne |

Si la sortie LLM est rejetée par (2), on **n'affiche pas une sortie partielle** — on bascule sur le fallback §D.4. Aucune réécriture, aucune correction silencieuse.

### D.4 — Fallback sans LLM (mode dégradé robuste)

Le Coach Report doit **rester fonctionnel** quand :
- L'utilisateur opt-out (préférence de compte)
- La clé API n'est pas configurée (déploiement self-hosted simple)
- L'API Anthropic est down ou rate-limited
- La validation §D.3 rejette la sortie

Fallback : **rendre le rapport v1 (Sb_23) à l'identique**, plus un message neutre en haut :

```
ⓘ Synthèse narrative indisponible — affichage des données brutes ci-dessous.
```

Aucune dégradation silencieuse du contenu. Le rapport reste utile dans son format Sb_23.

## E. Tags Mesuré / Inféré / Non déductible — comment la narration s'aligne

Le LLM produit du texte, qui par nature relève toujours de **l'inférence**. Donc **toutes les sorties LLM sont taggées `Inféré`** dans l'UI, sans exception.

| Bloc UI | Tag | Source |
|---|---|---|
| Section "Synthèse narrative" en tête | `Inféré` | LLM (ou fallback) |
| 10 blocs v1 du Coach Report | inchangés (chacun avec son tag d'origine) | services existants |
| Block narrations §D.1 (un mini-paragraphe par bloc) | `Inféré` | LLM |
| `limitations` field | (visuellement séparé, encadré gris) "Limites de ce rapport" | LLM mais sourcing explicite |

**Tag `Mesuré`** : aucune sortie LLM ne porte ce tag. Réservé aux chiffres bruts (sessions/30j, sets/sem, etc.).

**Tag `Non déductible`** : reste utilisé pour les champs absents (âge, VO2max, etc.) — le LLM peut **mentionner** ces limites dans son `limitations` field mais ne change pas le tag du champ.

## F. Données envoyées au LLM (privacy)

### F.1 — Ce qui est envoyé

Uniquement les **agrégats déjà calculés par `services/coach_report.py`** (Sb_23) + les **signaux Implicites Sx_24** (post-Sb_24) :

```python
{
  "username_anonymized": "user_<hash8>",     # pas le vrai username
  "identity": {
    "height_cm": 178, "weight_kg": 78.5,
    "weight_trend_kg_90d": -1.2,
    # waist_cm, resting_hr, bp_* OK
    # year_of_birth → null (V1)
  },
  "volume_30d": {sessions: 12, streak: 5, cardio_min_per_week: 60, ...},
  "ratio": {strength_pct: 70, cardio_pct: 30},
  "zones": {top: [...], neglected: [...]},
  "patterns": {dominant: ("push_horizontal", 35), distribution: {...}},
  "discipline": {completion_rate: 90, with_note_rate: 70, ...},
  "implicit_30d": {                            # NEW post-Sb_24
    "reserve_probable_pct": 18,
    "trajectoire_coherente_pct": 55,
    "pyramidal_ascendant_pct": 12,
    ...
  },
  "last_session_meta": {template: "Push A", days_ago: 2, score: 72}
}
```

### F.2 — Ce qui n'est PAS envoyé

- ❌ `username` réel (pseudo-anonymisation via hash 8 chars)
- ❌ Notes libres (`free_note`)
- ❌ Détails set par set (poids, reps individuels)
- ❌ Données médicales hors les champs déjà saisis par l'user
- ❌ Email, mot de passe, hash de mot de passe
- ❌ Historique de connexion / IP / device

### F.3 — Opt-in

Le LLM **ne tourne pas par défaut**. L'utilisateur active la feature dans `/profile` :

```
[ ] Activer la synthèse narrative LLM dans mon Coach Report

   En activant cette option :
   - Les agrégats anonymisés de votre rapport seront envoyés à
     l'API du fournisseur LLM configuré (par défaut Anthropic).
   - Aucune donnée brute par séance, aucune note, aucun nom
     d'utilisateur réel n'est transmis.
   - Vous pouvez désactiver à tout moment ; les rapports passés
     ne sont pas réécrits.
```

Stockage : `users.coach_llm_enabled BOOLEAN DEFAULT FALSE`. Migration Sb_25.1.

### F.4 — Fournisseur LLM

V1 : **Anthropic Claude** via API HTTP officielle.
- Modèle : `claude-haiku-4-5-20251001` par défaut (rapide, peu coûteux, suffisant pour la tâche)
- Configurable via env `SPIGNOS_LLM_MODEL` pour passer à Sonnet/Opus si besoin
- Clé API : env `ANTHROPIC_API_KEY`, jamais commité, jamais loggé

Coût attendu (estimation ordre de grandeur) :
- Input : ~2 ko de prompt système + ~3 ko de data utilisateur = ~5 ko ≈ ~1500 tokens
- Output : ~1-2 ko de JSON ≈ ~500 tokens
- Total ≈ 2000 tokens/call
- Tarif Haiku ≈ $0.001/1k input + $0.005/1k output → **~$0.005 par rapport généré**
- Avec 100 users actifs qui consultent leur rapport 1×/sem → ~$2/mois

Acceptable V1. Si Sonnet/Opus utilisé, le coût peut x10 ou x50 — donc gardé en option configurable.

### F.5 — Cache

Pour limiter le coût et la latence, **cache la sortie LLM 24h** par couple `(user_id, hash_of_report_payload)`. Si l'utilisateur recharge la page sans nouvelle séance entre temps, on ressert la même réponse.

Implémentation : table `coach_llm_cache` (user_id, payload_hash, response_json, created_at) avec TTL 24h.

## G. UI — où la narration s'insère

```
┌────────────────────────────────────────────────┐
│ Coach Report — @username                       │
│ Généré le 2026-05-31                           │
├────────────────────────────────────────────────┤
│ ┌──────────────────────────────────────────┐   │
│ │ ⌨ Synthèse narrative      [Inféré]       │   │
│ │                                          │   │
│ │ {{ one_line_summary }}                   │   │ ← LLM
│ │                                          │   │
│ │ Insight clé : {{ key_insight }}          │   │ ← LLM
│ │ Focus suggéré 30j : {{ focus }}          │   │ ← LLM
│ │                                          │   │
│ │ Limites : {{ limitations }}              │   │ ← LLM
│ │                                          │   │
│ │ [Régénérer]   [Désactiver dans /profile] │   │
│ └──────────────────────────────────────────┘   │
├────────────────────────────────────────────────┤
│ 1. Identité physique          [Mesuré]         │
│    178 cm · 78,5 kg (−1,2 kg /90j)             │
│    {{ block_narrations.identity }}             │ ← LLM mini (250 chars)
├────────────────────────────────────────────────┤
│ 2. Volume et fréquence        [Mesuré]         │
│    ...                                         │
│    {{ block_narrations.volume }}               │ ← LLM mini
├────────────────────────────────────────────────┤
│ ... blocs 3-10 inchangés Sb_23 ...             │
└────────────────────────────────────────────────┘
```

Si LLM désactivé (opt-out) ou fallback : le bloc en haut est masqué, et les mini-narrations par bloc disparaissent. Le rapport reste fonctionnel.

## H. Sécurité et données sensibles

| Menace | Mitigation |
|---|---|
| Prompt injection via free_note saisie utilisateur | ❌ `free_note` n'est pas envoyé au LLM (§F.2). Aucune entrée user libre ne traverse vers l'API |
| Fuite de PII via username | Hash 8 chars (§F.1) — pas réversible côté LLM |
| Exfiltration des données via le LLM (logging côté Anthropic) | Anthropic ne stocke pas les inputs API par défaut. Documenté §H.4 |
| Régression du contrat narratif (mise à jour du modèle) | Tests CI sur outputs mockés (§D.3 mécanisme 3) |
| LLM hallucine un chiffre | Les chiffres bruts viennent des blocs v1 (services Sb_23) — pas régénérés par le LLM. La narration LLM ne **redit pas** les chiffres, elle les **commente** |
| Coût LLM explose | Cache 24h §F.5 + opt-in par user §F.3 + modèle Haiku par défaut |
| LLM bloqué / down | Fallback §D.4 transparent |

### H.4 — Politique Anthropic

À documenter dans la page `/profile` au-dessus de l'opt-in :
- Anthropic Anti-Misuse policy
- Anthropic Privacy Policy
- Lien vers la doc "Trust Center" Anthropic
- Mention claire : aucune donnée n'est utilisée pour l'entraînement (politique Anthropic API standard)

## I. Fallback détaillé

Le fallback (§D.4) doit être :

1. **Transparent** — l'utilisateur sait qu'il y a une dégradation (bannière info)
2. **Sans bug** — toutes les autres surfaces du Coach Report restent fonctionnelles
3. **Logged** — chaque fallback augmente un compteur `coach_llm_fallback_total{reason}` qu'on peut consulter en debug
4. **Cause discriminée** — 4 causes possibles, journalisées séparément :
   - `opt_out` : l'utilisateur a désactivé
   - `not_configured` : pas de clé API en env
   - `api_error` : appel raté (timeout, 4xx, 5xx)
   - `output_rejected` : la sortie a été rejetée par la blacklist §D.3 mécanisme 2

Un usage sain devrait avoir `output_rejected = 0` à long terme — si ce compteur monte, il faut affiner le prompt §D.2.

## J. Tests requis

| Test | Surface |
|---|---|
| Mock LLM happy path | Sortie JSON conforme → 200 avec section narrative |
| Mock LLM réponse non-JSON | → fallback `api_error` |
| Mock LLM avec mot interdit ("vous êtes fort") | → fallback `output_rejected` (mécanisme 2) |
| Mock LLM avec longueur dépassant max | → fallback `output_rejected` |
| User opt-out | → fallback `opt_out` (LLM jamais appelé) |
| Pas de clé API en env | → fallback `not_configured` |
| Cache hit | 2 appels successifs avec data identique → 1 seul appel API |
| Cache miss après nouvelle session | hash du payload change → re-call LLM |
| Privacy : free_note exclu du payload | Inspection du body construit avant call |
| Privacy : username hashé | Inspection du body |
| Tags `Mesuré`/`Inféré`/`Non déductible` préservés sur les blocs v1 | Test de régression Sb_23 |
| Print A4 : section narrative reste lisible imprimée | Test visuel CSS print |

## K. Limites assumées

1. **Pas de PDF natif serveur V2** — décision verrouillée. Si un coach veut un PDF, il imprime le SSR via son navigateur en "Imprimer en PDF".
2. **Anthropic uniquement V1** — pas de support multi-providers V2. Si on veut OpenAI / Gemini, ce sera Sb_25.next.
3. **Pas de génération en arrière-plan** — la narration est calculée à la consultation de la page (~2-5s d'attente avec Haiku). Pas de job cron qui pré-génère. Choix produit : la page reste cohérente avec les données du moment.
4. **Cache 24h figé** — si l'utilisateur fait une séance et veut voir le rapport mis à jour le jour même, il doit cliquer "Régénérer". Acceptable V1.
5. **Pas de mémoire conversationnelle** — chaque appel est indépendant, pas de fil de discussion. Le LLM ne "se souvient" pas du rapport de la semaine dernière.
6. **Modèle peut changer sans préavis (côté Anthropic)** — un futur Haiku 4.6 pourrait subtilement changer le ton de la narration. Tests CI §J détectent les régressions sur la liste d'interdits, pas les variations stylistiques fines.
7. **Pas de feedback utilisateur sur la qualité de la narration** — V1 n'a pas de bouton "👍/👎" ni de signalement de violation des garde-fous. À ajouter en Sb_25.next si besoin.
8. **Pas de garantie 100 % anti-jailbreak** — le triple mécanisme couvre la majorité, mais un attaquant déterminé pourrait trouver une formulation qui passe. Le risque réel = un utilisateur fait son propre rapport, donc il peut "casser" son propre encadrement. Pas un risque de société.

## L. Lotissement build (Sb_25)

| Lot | Sujet | Effort estimé | Dépendance |
|---|---|---|---|
| **Sb_25.1** | Migration BD : `users.coach_llm_enabled` (default FALSE) + table `coach_llm_cache` | 2 h | — |
| **Sb_25.2** | Service `services/coach_llm.py` : construit le payload anonymisé §F.1, fait l'appel API Anthropic, parse la réponse JSON | 3 h | Sb_25.1 |
| **Sb_25.3** | Validation post-génération : keyword blacklist §C, vérification longueur, fallback structuré | 2 h | Sb_25.2 |
| **Sb_25.4** | System prompt versionné dans `data/coach_llm_system_prompt.txt` + few-shots | 2 h | — |
| **Sb_25.5** | Cache 24h via la nouvelle table + invalidation sur nouvelle session | 2 h | Sb_25.1, Sb_25.2 |
| **Sb_25.6** | Opt-in UI `/profile` (checkbox + texte d'explication + lien Trust Center Anthropic) | 2 h | Sb_25.1 |
| **Sb_25.7** | Template `coach_report.html` : section "Synthèse narrative" + mini-narrations par bloc + bannière fallback | 3 h | Sb_25.2, Sb_25.3 |
| **Sb_25.8** | Tests E2E §J : happy path, opt-out, not_configured, api_error, output_rejected, cache, privacy | 3 h | tous |
| **Sb_25.9** | Sprint report + audit empirique sur 5-10 rapports générés (ton, respect des contrats) | 1 h | tous |

**Effort total Sb_25 : ~20 h** sur 1-2 semaines.

### L backlog post-Sb_25

- **Sb_25.next1** — Multi-provider (OpenAI, Gemini) si une dépendance unique à Anthropic devient problématique
- **Sb_25.next2** — Bouton 👍/👎 sur la narration + signalement de violation
- **Sb_25.next3** — Génération en arrière-plan (cron post-séance) si la latence consultation devient frustrante
- **Sb_25.next4** — Memoire conversationnelle ("la semaine dernière, vous aviez tel pattern…") — V3, risque sur la cohérence et le coût

## M. Risques

| Risque | Mitigation |
|---|---|
| LLM produit une narration qui franchit les 4 interdits | Triple mécanisme §D.3 + tests CI + monitoring `output_rejected` |
| Coût LLM dérive | Modèle Haiku par défaut + cache 24h + opt-in user |
| Utilisateur s'attache à la narration et finit par la prendre pour parole d'évangile | Le tag `Inféré` partout + le `limitations` field obligatoire à chaque génération |
| Anthropic change ses tarifs ou retire Haiku | Spec déjà multi-providers en backlog (Sb_25.next1) |
| Privacy plainte de l'utilisateur | Opt-in explicite avec texte détaillé §F.3 + politique Anthropic documentée |
| Un coach externe critique la qualité de la narration ("ce n'est pas ce que je dirais") | Le LLM n'est PAS un coach — message §C.1 "tu n'es PAS un coach" + fallback v1 toujours accessible |
| Le SSR + narration LLM dépasse la latence acceptable (>5s) | Haiku attendu ~2-3s. Si Sonnet/Opus utilisé, peut monter à 10s. Cache 24h limite l'exposition |

## N. Acceptance criteria Sx_25

- [x] Spec couplée à Sx_24 (consommation des signaux Implicites — §F.1)
- [x] Format de sortie LLM structuré (JSON schema documenté §D.1)
- [x] System prompt versionné hors code (§D.2)
- [x] Triple mécanisme d'enforcement (§D.3)
- [x] Fallback complet documenté (§D.4 + §I) avec 4 causes discriminées
- [x] Opt-in par défaut, jamais opt-out (§F.3)
- [x] Privacy : aucune donnée brute par séance, aucune note, username hashé (§F.1, §F.2)
- [x] Tags `Mesuré`/`Inféré`/`Non déductible` préservés et étendus (§E)
- [x] PDF natif serveur **explicitement hors V2** (§B)
- [x] Lotissement Sb_25 chiffré (§L)
- [x] Tests requis listés (§J)
- [x] Limites assumées (§K) + risques (§M)

## O. Verdict

**Sx_25 prête.** Spec couplée à Sx_24 (les signaux Implicites alimentent la narration). Les contrats durs §C + §E + §F.3 garantissent que la feature, même si activée, ne peut pas franchir les 4 interdits hérités de Sx_23.

**Recommandation après validation humaine** :
1. Ouvrir **Sb_24.1** (migration BD du scoring V2 + label Implicite) — fondations pour Sb_25
2. Enchaîner sur Sb_24.2 (`services/implicit_signal.py`)
3. Une fois Sb_24 livré, ouvrir Sb_25.1 — la narration LLM consommera naturellement les signaux Implicites

Le triptyque de specs Sx_24 + Sx_25 (couplé) est cohérent : V2 du Coach Report fait sens **après** que le V2 du scoring soit en place.
