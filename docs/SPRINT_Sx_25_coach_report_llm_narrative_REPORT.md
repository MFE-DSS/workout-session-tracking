# Sprint Sx_25 Spec Report — Coach Report v2 LLM Narrative Encadré

**Date :** 2026-05-31
**Type :** SPEC ONLY — extension Sb_23 Coach Report v1 avec couche narrative LLM strictement encadrée.
**Prérequis :** Sb_23 livré (`e99f776`), Sx_24 spec livrée (signaux implicites couplés).
**Successeur build :** Sb_25 (lotté, après Sb_24).

---

## 1. Résumé exécutif

Sx_25 ferme le triptyque de specs ouvert par Sx_21 méta-spec. Elle ajoute une **couche narrative LLM** au Coach Report v1 (Sb_23) tout en garantissant que **les 4 interdits stricts hérités de Sx_23 §B.bis ne peuvent pas être franchis** (jugement esthétique, pronostic morphologique, verdict performance max, comparaison inter-users).

**Verrous décidés (consignes user)** :
- ✅ SPEC ONLY
- ✅ Pas de PDF natif server-side V2 — SSR + Imprimer navigateur reste le support
- ✅ Tags `Mesuré`/`Inféré`/`Non déductible` préservés
- ✅ Fallback complet sans LLM
- ✅ Couplée avec Sx_24 (signaux Implicites consommés comme matière première de la narration)

## 2. Fichiers créés

| Fichier | Type | Lignes |
|---|---|---|
| `docs/strategy/SPIGNOS_COACH_REPORT_LLM_NARRATIVE_SPEC_v2.md` | New | Spec complète A→O |
| `docs/SPRINT_Sx_25_coach_report_llm_narrative_REPORT.md` | New | Ce rapport |

**0 ligne code applicatif touchée.** Implémentation = Sb_25 (9 lots, ~20 h).

## 3. Décisions clés livrées

### 3.1 — Format de sortie LLM : JSON structuré (pas freeform)

```json
{
  "one_line_summary": "string max 200",
  "block_narrations": { "volume": "...", "ratio": "...", ... },
  "key_insight": "string max 300",
  "suggested_focus_next_period": "string max 250",
  "limitations": "string max 250 — obligatoire"
}
```

Justification : valider la sortie devient trivial (longueurs, présence). Le LLM ne peut pas "déborder" en paragraphes incontrôlés. Chaque champ a son emplacement dédié dans la page.

### 3.2 — Triple mécanisme d'enforcement

| # | Mécanisme | Couche |
|---|---|---|
| 1 | Structured output (JSON schema) | Pré-génération |
| 2 | Keyword blacklist post-génération | Server-side |
| 3 | Tests CI sur outputs mockés | CI |

Si l'un échoue → fallback §3.4. Pas de réécriture silencieuse.

### 3.3 — Vocabulaire imposé / interdit (§C.3 de la spec)

**Imposé** : "suggèrent", "indiquent", "pourraient", "selon les données saisies", "sous réserve de vérification par un coach humain".

**Interdit** : "vous êtes" + verdict, "vous allez" + pronostic, "mieux que / moins bien que", "manifestement / clairement / évidemment".

### 3.4 — Fallback robuste (4 causes discriminées)

| Cause | Comportement |
|---|---|
| `opt_out` | User a désactivé → LLM jamais appelé |
| `not_configured` | Pas de clé API → bannière info, rapport v1 |
| `api_error` | Anthropic down / timeout → bannière info, rapport v1 |
| `output_rejected` | Sortie a franchi un mot interdit → bannière info, rapport v1 |

Compteurs par cause loggés pour debug. Aucune réécriture silencieuse de la sortie LLM rejetée.

### 3.5 — Opt-in par défaut (privacy)

`users.coach_llm_enabled BOOLEAN DEFAULT FALSE`. L'utilisateur active explicitement dans `/profile` avec texte d'explication (politique Anthropic + nature des données envoyées).

**Données envoyées** : agrégats anonymisés (Mesurés/Inférés) + signaux Implicites Sx_24.
**Données NON envoyées** : free_note, sets individuels, username réel (hashé en `user_<hash8>`), email, sessions logs.

### 3.6 — Fournisseur LLM V1

- **Anthropic Claude Haiku 4.5** par défaut (rapide, peu coûteux).
- ~$0.005 par rapport généré ; cache 24h ; ~$2/mois pour 100 users actifs.
- Configurable via `SPIGNOS_LLM_MODEL` pour Sonnet/Opus si besoin (coût x10-x50).
- Multi-providers en backlog Sb_25.next1 (OpenAI, Gemini).

### 3.7 — PDF — décision verrouillée

**Pas de génération PDF côté serveur V2.** Argument :
- Le navigateur produit déjà un PDF correct via "Imprimer en PDF"
- Pas de dépendance OS / polices / cache à gérer
- Stack reste simple (FastAPI + Jinja, pas de weasyprint/reportlab)

Si plus tard un coach externe exige un PDF "officiel", on ré-ouvrira.

## 4. Couplage avec Sx_24

Le LLM reçoit les **signaux Implicites Sx_24** comme matière première :

```json
"implicit_30d": {
  "reserve_probable_pct": 18,
  "trajectoire_coherente_pct": 55,
  "pyramidal_ascendant_pct": 12,
  ...
}
```

Conséquence : Sb_24 doit être livré **avant** Sb_25. La narration LLM consomme les labels Implicites et peut s'en servir pour expliquer l'effort réel sur 30j (avec garde-fous : toujours conditionnel "les données suggèrent…").

## 5. Lotissement build (Sb_25, ~20 h)

| Lot | h |
|---|---|
| Sb_25.1 — Migration BD (`users.coach_llm_enabled` + table cache) | 2 |
| Sb_25.2 — `services/coach_llm.py` (payload + appel API + parsing) | 3 |
| Sb_25.3 — Validation post-génération (blacklist + longueur) | 2 |
| Sb_25.4 — System prompt versionné + few-shots | 2 |
| Sb_25.5 — Cache 24h + invalidation | 2 |
| Sb_25.6 — Opt-in UI `/profile` | 2 |
| Sb_25.7 — Template `coach_report.html` étendu | 3 |
| Sb_25.8 — Tests E2E (12 cas listés §J) | 3 |
| Sb_25.9 — Sprint report + audit empirique 5-10 rapports | 1 |

## 6. Acceptance criteria Sx_25

- [x] Format JSON structuré (§D.1)
- [x] System prompt versionné hors code (§D.2)
- [x] Triple mécanisme d'enforcement (§D.3)
- [x] Fallback 4 causes discriminées (§D.4 + §I)
- [x] Privacy : pseudo-anonymisation + opt-in + pas de free_note transmis (§F)
- [x] Tags `Mesuré`/`Inféré`/`Non déductible` préservés (§E)
- [x] PDF natif explicitement hors V2 (§B)
- [x] Couplage Sx_24 documenté (§F.1 + §4 ici)
- [x] Lotissement Sb_25 chiffré (§L de la spec)
- [x] Tests listés (§J de la spec)
- [x] Risques + limites (§K, §M)

## 7. Verdict

**Sx_25 prête.** Triptyque Sx_24 + Sx_25 cohérent et couplé. Build doit s'ouvrir **Sb_24 puis Sb_25** (la narration consomme les signaux implicites — séquencement naturel).

## 8. Synthèse du triptyque livré

| Spec | Livrée | Couvre |
|---|---|---|
| Sx_24 | `0c77ea8` | N9 + N10 (checkbox + scoring implicite) |
| Sx_25 | (ce commit) | N7 (Coach Report narratif encadré) |
| Bug fix focal Sb_22a.next2 | `3092d00` | N8 (atlas suit le réalisé) — **déjà déployé prod** |

Les 4 retours dogfooding (N7, N8, N9, N10) sont **tous fermés au niveau spec** ou en prod. Le build Sb_24 + Sb_25 peut maintenant être exécuté en série.
