# Dogfooding Report — `<CYCLE_OR_FEATURE>` — `<YYYY-MM-DD>`

> Rapport produit après une session d'usage réelle, pas un test automatisé. Le but : capturer les frictions vécues, pas les bugs détectables par CI.

**Auteur :** `<utilisateur>`
**Surface dogfoodée :** `<feature(s) ou cycle Sx_NN>`
**Durée de la session :** `<heures, sessions, # interactions>`
**Contexte :** mobile / desktop / prod / staging / dev

---

## 1. Résumé en 3 lignes

Ce qui marche bien. Ce qui frustre. Ce qui surprend.

## 2. Frictions ressenties (ordonnées par fréquence)

| # | Friction | Surface | Fréquence | Impact | Reproductible ? |
|---|---|---|---|---|---|
| 1 | | | constant / fréquent / occasionnel | bloquant / agaçant / cosmétique | oui / non / partiel |

Format : verbatim de ce que l'utilisateur a vécu. Pas de réinterprétation.

## 3. Surprises positives

Choses qui ont mieux marché que prévu — signale que la spec a bien anticipé.

## 4. Surprises négatives

Choses qui n'ont pas marché comme prévu **et qui n'étaient pas couvertes par la spec**. C'est ici qu'on identifie les non-goals oubliés ou les hard contracts à ajouter.

## 5. Items à backloguer

| Item | Sprint cible suggéré | Sévérité |
|---|---|---|
| | Sb_NN.next.<topic> ou Sb_NN+1.0 | bloquant / important / cosmétique |

## 6. Items qui NE doivent PAS devenir un sprint

Frictions qu'on assume comme acceptables V1 (qualité produit > vitesse, ou debt technique connue). Documenter explicitement pour éviter qu'un futur sprint les ouvre par réflexe.

## 7. Signaux de drift / dette spec

Cas où la spec d'origine n'a pas anticipé un usage réel. Marqueurs pour le prochain Sx_NN+1.

## 8. Verdict

- Cycle `<Sx_NN>` : ✅ utilisable / ⚠️ utilisable avec frictions / ❌ pas utilisable
- Prochain sprint prioritaire : `<Sb_NN.next.<topic>>` ou aucun
