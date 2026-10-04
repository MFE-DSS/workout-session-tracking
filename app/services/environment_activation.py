"""La frontière d'ACTIVATION de l'environnement (`Sb_TRAIN_A_ENV_ACT_01`).

`TRAIN A` a bâti le résolveur et l'a laissé sans consommateur. Ce module est
le consommateur — **le seul**. Il ne rend aucun verdict par lui-même : il
appelle `environment_resolution` et compose son résultat avec le classement
déjà produit par la politique servie.

**Ce qu'il ne fait jamais**, et c'est ce qui l'empêche de devenir un second
moteur :

* il ne **classe** pas — il retire des candidats prouvés infaisables et
  laisse l'ordre survivant intact, bit pour bit ;
* il ne **cherche** aucun substitut — la liste autorisée lui est fournie,
  dans l'ordre que le moteur de substitution a produit ;
* il ne rend **aucun score**.

**LA RÈGLE QUI PROTÈGE TOUS LES UTILISATEURS ACTUELS.** La porte ne
s'applique **que** si l'environnement concret est DÉCLARÉ. Sur `NULL`, elle
est inerte et le chemin servi est identique à celui d'avant.

Ce n'est pas de la prudence : c'est mesuré. Sur un environnement `NULL`,
seuls 2 gabarits sur 18 sont `SERVABLE` — filtrer y retirerait 16 gabarits
d'un coup. `NULL` signifie « environnement concret non résolu », pas
« l'utilisateur n'a rien ». La porte `G7` l'exige, et la directive aussi :
*« for the user's effective DECLARED environment »*.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from app.services.environment_resolution import (
    ADAPTABLE,
    NO_SERVABLE_CANDIDATE,
    SERVABLE,
    identite_materielle_environnement,
    materialization_plan,
    resolve_catalogue,
    resolve_template,
)

#: `(position, prescrit, exécuté)` — la forme que consomme la matérialisation.
Adaptation = tuple[int, str, str]


@dataclass(frozen=True)
class CandidatsEnvironnement:
    """Ce que la porte rend au chemin servi.

    `actif = False` est le cas hérité : tout le reste est neutre, et
    l'appelant doit pouvoir s'en servir sans écrire de condition.
    """

    #: La porte s'est-elle appliquée ? `False` sur environnement non déclaré.
    actif: bool
    #: Les candidats retenus, **dans l'ordre reçu**.
    candidats: list = field(default_factory=list)
    #: slug → adaptations à matérialiser. Vide si rien ne s'adapte.
    adaptations: dict[str, tuple[Adaptation, ...]] = field(default_factory=dict)
    #: État du catalogue, ou `None` quand la porte n'a pas tourné. `None` et
    #: `NO_SERVABLE_CANDIDATE` sont deux faits distincts : « rien n'a été
    #: calculé » et « rien n'est servable » ne doivent pas se ressembler.
    etat_catalogue: str | None = None
    #: Identité matérielle de l'environnement, pour l'empreinte (`G9`).
    #: `None` tant que la porte n'a pas causalement agi.
    identite: str | None = None


_INERTE = CandidatsEnvironnement(actif=False)


def filtrer_par_environnement(candidats, objets_declares) -> CandidatsEnvironnement:
    """Applique la faisabilité d'environnement au classement déjà produit.

    `candidats` est une suite d'objets portant `.slug` et `.creneaux`, ce
    dernier étant une suite de `(prescrit, substituts_autorisés)`.

    `objets_declares` : `None` = non déclaré ⇒ **porte inerte**.

    Trois sorties, et elles suivent le `§1` :

    * au moins un gabarit **prouvé** servable ⇒ seuls ceux-là survivent ;
    * aucun prouvé mais au moins un **incertain** ⇒ la liste reçue est
      rendue **telle quelle** — l'incertitude n'est pas une impossibilité,
      et fabriquer une faisabilité serait pire que ne rien filtrer ;
    * aucun prouvé et aucun incertain ⇒ `NO_SERVABLE_CANDIDATE`, liste vide.
    """
    candidats = list(candidats)
    if objets_declares is None:
        return CandidatsEnvironnement(actif=False, candidats=candidats)

    objets = tuple(objets_declares)
    resolutions = [
        resolve_template(c.slug, c.creneaux, objets) for c in candidats
    ]
    catalogue = resolve_catalogue(resolutions)
    par_slug = {r.template_slug: r for r in resolutions}

    if catalogue.state == SERVABLE:
        servables = {r.template_slug for r in catalogue.servable}
        retenus = [c for c in candidats if c.slug in servables]
        adaptations = {
            c.slug: materialization_plan(par_slug[c.slug])
            for c in retenus
            if materialization_plan(par_slug[c.slug])
        }
        return CandidatsEnvironnement(
            actif=True, candidats=retenus, adaptations=adaptations,
            etat_catalogue=catalogue.state,
            identite=identite_materielle_environnement(resolutions),
        )

    if catalogue.state == NO_SERVABLE_CANDIDATE:
        return CandidatsEnvironnement(
            actif=True, candidats=[], etat_catalogue=NO_SERVABLE_CANDIDATE,
            identite=identite_materielle_environnement(resolutions),
        )

    # Incertain : on rend la liste REÇUE, sans adaptation. Ne rien prouver
    # n'autorise ni à bloquer, ni à matérialiser.
    return CandidatsEnvironnement(
        actif=True, candidats=candidats, etat_catalogue=catalogue.state,
        identite=identite_materielle_environnement(resolutions),
    )


def plan_de_materialisation(
    resultat: CandidatsEnvironnement, slug: str
) -> tuple[Adaptation, ...]:
    """Ce qu'il faut écrire sur la séance AVANT son démarrage (`§2`, `G6`).

    Vide quand la porte est inerte : un utilisateur `NULL` ne reçoit jamais
    d'adaptation, parce qu'aucun environnement ne l'a demandée.
    """
    if not resultat.actif:
        return ()
    return resultat.adaptations.get(slug, ())


def identite_pour_empreinte(resultat: CandidatsEnvironnement) -> str | None:
    """L'identité d'environnement à mêler à l'empreinte de contexte (`G9`).

    `None` tant que la porte n'a pas tourné : l'empreinte ne devient
    environnementale qu'à l'activation **causale**, jamais avant. Sans cette
    règle, activer le module périmerait d'un coup tous les refus enregistrés
    par des utilisateurs dont l'environnement n'a jamais compté.
    """
    return resultat.identite if resultat.actif else None


# ---------------------------------------------------------------------------
# Adaptation au chemin servi — la seule partie qui connaît le modèle
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class _Vue:
    """Ce que la porte a besoin de savoir d'un candidat : rien de plus."""

    slug: str
    creneaux: list
    verdict: object = None


def environnement_declare(
    db, user_id: int, *, strict: bool = False
) -> tuple[str, ...] | None:
    """L'environnement concret DÉCLARÉ, ou `None`.

    Lu par la frontière canonique des préférences, jamais par une requête
    dispersée.

    **Deux tolérances, parce qu'il y a deux rôles.** Lire l'environnement
    pour CLASSER peut échouer sans conséquence : une recommandation dégradée
    vaut mieux qu'un écran cassé, donc l'échec rend `None` et la porte
    devient inerte. Lire l'environnement pour DÉCIDER DE CRÉER UNE SÉANCE ne
    le peut pas : là, une panne qui se déguise en « non déclaré » ferait
    démarrer une séance que l'utilisateur ne peut pas exécuter. `strict`
    laisse alors remonter.
    """
    from app.services.training_preferences import get_training_preferences

    if strict:
        return get_training_preferences(db, user_id).available_equipment_items
    try:
        return get_training_preferences(db, user_id).available_equipment_items
    except Exception:
        return None


def _creneaux_du_template(template) -> list:
    """`(prescrit, substituts autorisés)` par créneau, dans l'ordre du moteur.

    Les substituts ne sont pas cherchés ici : `all_suggestions_flat` les
    produit déjà, `N1` puis `N2` puis `N3`, chacun trié par proximité.
    """
    from app.services.substitution import all_suggestions_flat

    return [
        (te.name, [s.name for s in all_suggestions_flat(te)])
        for te in sorted(template.exercises, key=lambda x: x.position)
    ]


def appliquer(db, user_id: int, verdicts) -> CandidatsEnvironnement:
    """Applique la porte au classement servi. Point d'entrée du chemin réel.

    Reçoit les `Verdict` **déjà ordonnés** et rend les survivants dans le
    même ordre. Toute exception rend la porte inerte : l'environnement est
    un raffinement, il ne doit jamais empêcher de recommander.
    """
    objets = environnement_declare(db, user_id)
    if objets is None:
        return CandidatsEnvironnement(actif=False, candidats=list(verdicts))
    try:
        vues = [
            _Vue(v.template.slug, _creneaux_du_template(v.template), v)
            for v in verdicts
        ]
    except Exception:
        return CandidatsEnvironnement(actif=False, candidats=list(verdicts))

    resultat = filtrer_par_environnement(vues, objets)
    return CandidatsEnvironnement(
        actif=resultat.actif,
        candidats=[vue.verdict for vue in resultat.candidats],
        adaptations=resultat.adaptations,
        etat_catalogue=resultat.etat_catalogue,
        identite=resultat.identite,
    )


def plan_pour_template(db, user_id: int, template) -> tuple[Adaptation, ...]:
    """Ce qu'il faut matérialiser pour CE gabarit, au moment du démarrage.

    Recalculé ici plutôt que transporté depuis l'écran : le geste de
    démarrer peut suivre la recommandation de loin, et c'est l'environnement
    **au moment du démarrage** qui fait foi. Une fois la séance créée, plus
    rien n'est recalculé — la matérialisation est persistée.
    """
    objets = environnement_declare(db, user_id)
    if objets is None:
        return ()
    try:
        vue = _Vue(template.slug, _creneaux_du_template(template), None)
    except Exception:
        return ()
    return plan_de_materialisation(
        filtrer_par_environnement([vue], objets), template.slug
    )


# ---------------------------------------------------------------------------
# La frontière de DÉMARRAGE — `Sb_TRAIN_A_ENV_EXP_01`
# ---------------------------------------------------------------------------
#
# `plan_pour_template` ne savait pas refuser : `NO_SERVABLE_CANDIDATE` et
# « rien à adapter » rendaient tous deux `()`. Le signal de refus était donc
# jeté exactement à la frontière que la création de séance utilise.
#
# Cinq états nommés le remplacent. Aucun nombre, aucun booléen : un appelant
# ne doit pas pouvoir confondre « rien à faire » et « ne pas faire ».

#
# ⚠ `ADAPTABLE` n'est PAS redéfini ici. Le résolveur le possède déjà, avec la
# même valeur et le même sens — « exécutable via des substituts autorisés ».
# En écrire une seconde copie dans ce module a fait rougir
# `test_no_second_resolver_was_introduced`, et la garde avait raison : deux
# définitions du même fait finissent toujours par diverger. Il est importé en
# tête, et ré-exporté pour que les appelants du préflight lisent les cinq
# états au même endroit.

#: Environnement non déclaré. Chemin hérité, strictement rien.
NON_APPLICABLE = "non_applicable"
#: Prouvé exécutable tel quel.
NATIF = "natif"
#: §1.B — aucune voie prouvée, mais au moins une inconnue. Non bloquant.
INCERTAIN = "incertain"
#: Toutes les voies autorisées sont connues incompatibles.
REFUSE = "refuse"


@dataclass(frozen=True)
class PreparationDemarrage:
    """Ce que le préflight autorise, et à quelles conditions exactes."""

    etat: str
    slug: str | None = None
    #: Les adaptations à poser. Vide sauf en `ADAPTABLE`.
    plan: tuple[Adaptation, ...] = ()

    @property
    def attendu(self) -> int:
        """Combien d'adaptations DOIVENT être posées.

        L'appelant compare ce nombre à ce qu'il a réellement écrit. En poser
        moins est un **échec**, jamais un demi-succès.
        """
        return len(self.plan)

    @property
    def autorise(self) -> bool:
        return self.etat != REFUSE


def preparer_demarrage(db, user_id: int, template) -> PreparationDemarrage:
    """Décide, AVANT toute instanciation, si cette séance peut démarrer.

    Appelée par **chaque** route qui crée une séance — une garde par AST
    vérifie qu'aucun appelant d'`instantiate_session` ne s'en dispense. La
    version précédente n'en câblait qu'une sur deux.

    Lecture **stricte** de l'environnement : ici, une panne ne se déguise
    pas en « non déclaré ».
    """
    objets = environnement_declare(db, user_id, strict=True)
    if objets is None:
        return PreparationDemarrage(NON_APPLICABLE, getattr(template, "slug", None))

    slug = template.slug
    vue = _Vue(slug, _creneaux_du_template(template), None)
    resultat = filtrer_par_environnement([vue], tuple(objets))

    if resultat.etat_catalogue == NO_SERVABLE_CANDIDATE:
        return PreparationDemarrage(REFUSE, slug)
    plan = resultat.adaptations.get(slug, ())
    if plan:
        return PreparationDemarrage(ADAPTABLE, slug, tuple(plan))
    if resultat.etat_catalogue == SERVABLE:
        return PreparationDemarrage(NATIF, slug)
    return PreparationDemarrage(INCERTAIN, slug)


__all__ = [
    "ADAPTABLE",
    "INCERTAIN",
    "NATIF",
    "NON_APPLICABLE",
    "REFUSE",
    "PreparationDemarrage",
    "preparer_demarrage",
    "Adaptation",
    "CandidatsEnvironnement",
    "appliquer",
    "environnement_declare",
    "filtrer_par_environnement",
    "identite_pour_empreinte",
    "plan_de_materialisation",
    "plan_pour_template",
]
