# AUREN — réception de la révision et contenu Programmes directement transmissible

**13 novembre 2026. Exploration non approuvée.** Archive originale et19fichiers conservés ; huitSVG390×844 vérifiés. Les corrections P1/P2/P3/B1/B2/B3 sont présentes dans les textes des sources. Cela constate une révision sémantique, sans accepter la composition, les interactions ou une reconstruction.

## Contenu de conception : supprimer la dépendance aux chemins locaux

Le designer externe n’a pas accès au disque du poste. Les chemins locaux/ZIP mentionnés dans le chat ne garantissent pas que le contenu a été joint à son propre tour. Les éléments ci-dessous sont donc **copiables tels quels dans son message** ; `PROGRAMMES_CONTENU_COPIABLE.json` accompagne cette note. Il s’agit d’une projection synthétique de conception, pas d’un DTO à servir ni d’une fixture runtime.

| Objet lu par le vrai domaine dans le banc QA | Noms exacts de l’exemple | Prescription connue dans cet exemple |
|---|---|---|
| Programme personnel PUBLISHED | **Programme QA publié** ; **Séance QA 1**, **Séance QA 2** | Chaque séance : un « Exercice synthétique non cartographié », deux séries de travail de8–12répétitions. Total du programme :4séries. |
| Programme personnel VALIDATED | **Programme QA validé** ; **Séance QA 1**, **Séance QA 2** | Même structure de conception. Le statut VALIDATED n’autorise pas le départ natif ; aucun bouton de lancement. |
| Modèle de séance, section core | **Push A — Pecs épaisseur + Delts + Triceps** |7exercices,21séries prévues dans le snapshot du vrai routeur. Ce n’est pas un programme personnel, ni une recommandation actuelle. |
| Modèle de séance, section core | **Push B — Pecs largeur/stretch + Delts latéraux + Triceps** |7exercices,22séries prévues dans ce snapshot. Même distinction de source. |

Les deux programmes QA sont des exemples synthétiques, **pas des programmes personnels disponibles pour un utilisateur réel**. Un nouveau compte peut n’avoir aucun programme personnel. Les noms à l’exécution viennent de `source.name` / `composition[].name` et les séries de `exercises[].rep_targets`. Ni programme actif persistant, ni jours de semaine, ni matériel disponible ou charge observée ne sont déduits.

La suppression du «2séries» était prudente à partir du CR seul. Le JSON complet permet maintenant de le montrer pour ce cas précis ; un total par programme n’autorise toujours pas à inventer une répartition pour un autre objet.

## Deux raccordements à préciser dans la planche

1. **Catalogue** : remplacer «Explorer le catalogue d’exercices» par «Catalogue de séances». MOB-06 sert les modèles de séances et les programmes personnels. Une fiche/bibliothèque d’exercices n’est pas rendue disponible par ce CTA. Le chemin de premier usage sans programme personnel doit rester lisible.
2. **Séance retrouvée** : son identité est celle de la lecture propriétaire actuelle, qui peut différer de la demande initiale. Ne pas recopier le nom du programme/de la séance demandés comme preuve. Le contrôleur conserve actuellement l’identifiant et le profil retrouvés ; un nom éventuel exige sa vraie source consommée. La reprise conserve les gates du profil Legacy/V3 ; la lecture propriétaire n’accorde pas une nouvelle permission scientifique.

Le reste relève de la finition artistique déjà identifiée : proportions, signature de famille, lisibilité des unités, grands textes, ongletsD4 réels et espace IME. Pas de nouvelle variante autonome demandée à Codex. La maturité artistique est explicitement non acquise ; l’opérateur décidera du master avant reconstruction native et nouveaux pixels.

## Continuité technique

Le patch MOB-06 et les résolutions additives BODY/NUT restent conservés. Les preuves1 276mobiles+TypeScript sont celles de la campagne précédente, pas un nouveau run ou uneCI. La composition serveur/migrations n’est pas déclarée fusionnée ou activée. Aucun codeUI, baseline, contratSCI, nouvelAPK, OTA ou déploiement n’a été produit par cette réception ; les GO métier restent acquis.
