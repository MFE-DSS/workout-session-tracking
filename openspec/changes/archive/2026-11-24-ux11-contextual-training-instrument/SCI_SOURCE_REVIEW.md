# UX11 — revue indépendante des contrats de source

23novembre2026, /root/ux11_source_comparability_review, lecture seule sur9dd90ac et sources UX10 préservées. Aucun test ou code exécuté par ce relecteur. Relecteur de contrat, pas propriétaire d’une nouvelle admission biologique.

Verdict : affichage brut positif défendable entre deux séries de la même occurrence V3 sous une nouvelle règle explicite bornée. LegacyAdduction inéligible ; NON_COMPARABLE des historiques inter-occurrences inchangé. ContextKey complet/connu/identique, propriétaire et binding identiques, sourcecompleted/révision effective, setting/unité typés, aucune priorité d’un fait local/outbox ou d’une prescription.

Limite temporelle importante reprise dans le design : dernière révision ≠ dernière performance chronologique ; completed_at peut rester à la première complétion, performed_at est déclaré/estimated et l’ajustement appartient au reçu. Choisir par ordre de série, pas par date supposée fiable ou délai d’entraînement.

Aucun avis biologique nouveau n’est requis pour seulement présenter ce fait dans ces bornes. Toute réutilisation comme réglage à réessayer, progression ou capacité réouvre la revue/admission applicable. La revue n’est ni le GO BUILD opérateur, ni le gate pixels.

Sources : app/services/training_history_reads.py:455,642 ; clients/mobile/src/api/trainingHistory.ts:103,132 ; domain/planV3Types.ts:3 ; app/services/plan_v3/execution.py:274 ; app/services/plan_v3/journal.py:85,116 ; tools/science_initial_policy/calibration_time_contracts.py:22 ; docs/science/sci-p02-initial-policy/stage2-v3/authority/ADMISSION.md et calibration-six-extensions/authority/ADMISSION.md.
