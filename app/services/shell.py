"""`UI-CP6 SHELL` — le contrat sémantique de la coque.

CE QUE CE MODULE POSSÈDE, ET CE QU'IL NE POSSÈDE PAS
-----------------------------------------------------
Il possède **deux sémantiques de produit**, et rien d'autre :

  1. **LE MODE DE COQUE** — dans quel régime une surface est servie. Quatre
     modes, et la précédence entre eux est une décision, pas un ordre de
     lecture (cf. `mode_de_coque`).
  2. **LES DESTINATIONS SECONDAIRES** — une source de vérité unique pour ce
     que la navigation secondaire propose, son ordre, et ce qui la souligne.

Il ne possède **pas** le balisage. `base.html` rend ce contrat **deux fois**,
avec deux vocabulaires de classes — la barre mobile et le rail desktop n'ont
ni les mêmes contraintes de largeur ni la même grammaire d'état.

⚠ C'EST DÉLIBÉRÉ, ET C'EST L'ARBITRAGE `Q4` MOT POUR MOT : « ne pas supposer
qu'un partiel HTML partagé est la bonne abstraction ». Un partiel unique
figerait ensemble deux rendus qui ont de bonnes raisons de différer ; ce qui ne
doit **jamais** diverger, c'est la SÉMANTIQUE — les identifiants, les routes,
les règles de disponibilité, l'ordre partagé. Une garde le vérifie sur le HTML
réellement servi, aux deux ruptures.

POURQUOI UN MODULE PLUTÔT QUE DU JINJA
---------------------------------------
Les six destinations étaient **écrites deux fois** dans `base.html` —
`.topbar__nav` et `.app-rail__secondary-nav` — et les deux blocs ne sont
**jamais rendus en même temps** : aucun test de page ne pouvait les comparer.
`UI-CP4` a dû éditer les deux. C'est le mode d'échec « famille aux deux
tiers », déjà armé : la tranche suivante en édite une et oublie l'autre.

Le module est **pur** : ni `sqlalchemy`, ni `datetime`, ni `request`. Il se
charge sans base, et une garde le vérifie.
"""
from __future__ import annotations

from dataclasses import dataclass

# ═════════════════════════ 1. LES QUATRE MODES ═════════════════════════

#: La coque applicative normale : topbar compacte + barre basse (mobile),
#: rail latéral (desktop). **Aucun pied de page générique.**
MODE_INSTRUMENT = "instrument"

#: L'exécution possède l'écran. Le chrome global disparaît entièrement —
#: topbar, navigation primaire, pied — et l'instrument de séance DEVIENT la
#: coque. La sortie reste explicite, découvrable et réversible.
MODE_FOCUS = "focus"

#: Une surface de RÉFÉRENCE, pas un instrument de cockpit. `UI-CP6` se borne à
#: la **classer** correctement ; sa mise en forme propre appartient à
#: `UI-CP7 REFERENCE`, y compris le sort de son pied de page.
MODE_DOCUMENT = "document"

#: Le seuil. Une surface non authentifiée ne reçoit **jamais** une version
#: dégradée du cockpit authentifié.
MODE_GUEST = "guest"

MODES = (MODE_INSTRUMENT, MODE_FOCUS, MODE_DOCUMENT, MODE_GUEST)

#: Les chemins du SEUIL. Liste **close** : une surface non authentifiée est un
#: ensemble connu et petit, pas une propriété devinée.
#:
#: ⚠ Deux d'entre elles — `/login` et `/register` — sont des gabarits
#: AUTONOMES qui n'étendent pas `base.html` : elles ne rendent aucune coque par
#: construction. Elles figurent quand même ici, et ce n'est pas redondant :
#: le jour où l'une d'elles rejoindra `base.html`, elle sera déjà classée. Une
#: garde vérifie les deux chemins.
CHEMINS_INVITE = (
    "/login",
    "/register",
    "/forgot-password",
    "/reset-password",
    "/logout",
)

#: Les préfixes des surfaces de RÉFÉRENCE, repris de
#: `AUREN_INSTRUMENTS §2bis` — « quatre surfaces ne sont pas des instruments,
#: et ce n'est pas un oubli » : le document destiné à un tiers, l'utilitaire de
#: sauvegarde, la référence explicative, la référence anatomique.
#:
#: ⚠ CE SONT DES PRÉFIXES DE ROUTE, PAS DES NOMS DE SURFACE — ET MA PREMIÈRE
#: ÉCRITURE CONFONDAIT LES DEUX.
#:
#: `§2bis` nomme des SURFACES : « coach_report + coach_body_snapshot »,
#: « science + science_diagram », « atlas ». J'en ai fait des chemins d'URL, et
#: deux d'entre eux ne désignaient **aucune route** :
#:
#:   · `coach_body_snapshot` est un PARTIEL inclus dans `coach_report.html`,
#:     pas une page — c'est une section du document, pas un document ;
#:   · l'atlas vit à `/science/atlas`, donc déjà sous `/science`.
#:
#: Le défaut était inoffensif — un préfixe qui ne matche rien ne classe rien —
#: mais il mentait au lecteur suivant, et **ma propre garde l'assertait à
#: vide** : « `/atlas` est un DOCUMENT » passait sans que `/atlas` existe.
#: `test_chaque_prefixe_de_document_designe_une_route_reelle` ferme la classe.
PREFIXES_DOCUMENT = (
    "/coach-report",
    "/export",
    "/science",
)


def _commence_par(chemin: str, prefixes: tuple[str, ...]) -> bool:
    """Vrai si `chemin` est l'un des préfixes, ou un chemin sous celui-ci.

    On exige la borne `/` plutôt qu'un `startswith` nu : `/exportateur` n'est
    pas sous `/export`, et un préfixe nu le rangerait pourtant en document.
    """
    for p in prefixes:
        if chemin == p or chemin.startswith(p + "/"):
            return True
    return False


def mode_de_coque(chemin: str, *, seance_en_cours: bool = False) -> str:
    """Le mode dans lequel cette surface doit être servie.

    ⚠ LA PRÉCÉDENCE EST UNE DÉCISION, PAS UN ORDRE DE LECTURE.

    ``GUEST > FOCUS > DOCUMENT > INSTRUMENT``

    * **`GUEST` d'abord.** Une surface de seuil ne doit jamais recevoir le
      cockpit, quel que soit l'état par ailleurs. Mesuré avant cette tranche :
      `/forgot-password` rendait **huit** destinations authentifiées sur mobile
      et **onze** sur desktop, dont `/profile`, `/progress` et `/library` — et
      c'était pourtant le seul gabarit qui posait `shell_bare`. Le drapeau
      nommait « seuil » mais ne retirait que deux des quatre structures.
    * **`FOCUS` ensuite.** L'exécution possède l'écran : c'est la décision
      produit du `§7`. Elle prime sur la classification de surface.
    * **`DOCUMENT` ensuite**, `INSTRUMENT` par défaut. Le défaut est le cockpit
      parce qu'une surface non classée est presque toujours un instrument ;
      se tromper dans ce sens rend une coque complète, jamais une coque vide.
    """
    if _commence_par(chemin, CHEMINS_INVITE):
        return MODE_GUEST
    if seance_en_cours:
        return MODE_FOCUS
    if _commence_par(chemin, PREFIXES_DOCUMENT):
        return MODE_DOCUMENT
    return MODE_INSTRUMENT


#: Les modes qui rendent la navigation PRIMAIRE (barre basse / rail).
MODES_AVEC_NAV_PRIMAIRE = (MODE_INSTRUMENT, MODE_DOCUMENT)

#: Les modes qui rendent la topbar compacte et son menu secondaire.
MODES_AVEC_TOPBAR = (MODE_INSTRUMENT, MODE_DOCUMENT)

#: Les modes qui rendent le pied de page générique.
#:
#: ⚠ `INSTRUMENT` N'Y EST PLUS, ET C'EST L'ARBITRAGE `Q3`. Un pied de page est
#: un objet de DOCUMENT ; l'avoir sur un instrument brouille exactement la
#: frontière que `AUREN_INSTRUMENTS §2bis` demande de rendre perceptible.
#: « Contact » n'est perdu nulle part : il reste dans la navigation secondaire.
#:
#: `DOCUMENT` le garde **temporairement**, sur instruction explicite : la
#: refonte du pied de document appartient à `UI-CP7 REFERENCE`.
MODES_AVEC_PIED = (MODE_DOCUMENT,)


# ═══════════════ 2. LES DESTINATIONS SECONDAIRES, UNE SEULE FOIS ═══════════════


@dataclass(frozen=True)
class DestinationSecondaire:
    """Une entrée de navigation secondaire, décrite **sémantiquement**.

    Aucun champ ne porte de classe CSS, de position ni de balisage : c'est ce
    qui permet aux deux rendus de différer sans que la sémantique diverge.
    """

    #: Identifiant stable, indépendant de la route et du libellé. C'est LUI que
    #: la garde de parité compare : un libellé peut changer, un identifiant non.
    id: str
    #: Nom de route FastAPI, tel que `url_for` l'attend.
    route: str
    #: Le libellé visible.
    libelle: str
    #: Le nom du drapeau `is_*` de `base.html` qui souligne cette entrée.
    #: Chaîne vide = aucune sous-activation (le cas de « Contact »).
    drapeau_actif: str


#: **L'ORDRE EST PARTAGÉ INTENTIONNELLEMENT**, et la garde le vérifie.
#:
#: Il n'est pas alphabétique et n'a pas à l'être : il va du plus proche de
#: l'entraînement (mon plan, mon historique) au plus périphérique (le social).
#: Deux rendus qui proposeraient les mêmes destinations dans deux ordres
#: différents apprendraient deux produits à la même personne.
NAVIGATION_SECONDAIRE = (
    DestinationSecondaire("plan", "user_plan", "Mon plan", "is_plan"),
    DestinationSecondaire("historique", "history", "Historique", "is_history"),
    DestinationSecondaire("coach", "coach_report", "Coach Report", "is_coach"),
    DestinationSecondaire("sauvegarde", "export_landing", "Sauvegarde", "is_export"),
    DestinationSecondaire("squads", "squads_list", "Squads", "is_squads"),
    DestinationSecondaire(
        "classement", "leaderboard_page", "Classement", "is_leaderboard"
    ),
)

#: ⚠ **EXCEPTION ENCODÉE, PAS TOLÉRÉE EN SILENCE.**
#:
#: « Contact » est une destination secondaire comme les autres, mais son
#: PLACEMENT diffère d'un rendu à l'autre : dans le menu sur mobile, en pied de
#: rail sur desktop. L'arbitrage `Q4` autorise explicitement ces exceptions
#: « à condition qu'elles soient encodées et testées » — elle l'est ici, et la
#: garde de parité l'inclut dans l'ensemble des destinations attendues tout en
#: n'exigeant **pas** qu'elle occupe la même position.
CONTACT = DestinationSecondaire("contact", "contact_page", "Contact", "")

#: Tout ce que la navigation secondaire doit proposer, placement mis à part.
DESTINATIONS_ATTENDUES = tuple(d.id for d in NAVIGATION_SECONDAIRE) + (CONTACT.id,)
