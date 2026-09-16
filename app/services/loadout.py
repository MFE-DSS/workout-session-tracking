"""`UI-CP4 LOADOUT` — la projection du REGISTRE TYPÉ.

LA QUESTION QUE CET INSTRUMENT POSSÈDE
--------------------------------------
    « Avec quoi puis-je m'entraîner — quelle configuration je choisis ? »

Il y répond par un **registre**, pas par une grille de cartes : une ligne par
configuration, le détail au dépli, **une** commande dominante dans le dépli.

CE QUI EST TYPÉ, ET POURQUOI ÇA N'EST PAS UNE LISTE PLATE
----------------------------------------------------------
`WorkoutTemplate` et `UserProgram` restent **deux objets de domaine
distincts**. Aucune table n'est fusionnée. Ce qui fusionne est la *perception* :
les deux apparaissent dans le même instrument.

Mais ils n'ont **pas la même sémantique**, et l'arbitrage opérateur l'exige
explicitement : *« do NOT pretend that a multi-session program and a single
executable workout have identical semantics »*. D'où deux types de ligne :

* `SessionRow` — une séance exécutable. Elle porte une commande de démarrage.
* `ProgramRow` — un programme, c'est-à-dire une **composition** de séances.
  Il n'a **aucune** commande de démarrage, parce que le domaine n'en a aucune :
  on ne démarre pas un programme, on démarre l'une de ses séances.

Cette distinction est **structurelle et non conditionnelle** : ce sont deux
classes, et `ProgramRow` n'a aucun champ qui pourrait porter un démarrage. Un
START inventé pour un programme n'est pas seulement interdit — il est
inexprimable.

LA SEULE FORMULE DE SÉRIES DE TRAVAIL
--------------------------------------
`work_sets()` est **la** définition, et elle vaut pour les deux arbres.

⚠ Le plan de tranche annonçait « deux formules concurrentes ». **Vérifié dans
le code : c'était faux.** `RepTarget` (catalogue) n'a **aucune** colonne
`is_warmup` — les échauffements du catalogue sont générés à l'instanciation,
jamais stockés. Les deux écritures rendaient donc la même valeur. Ce qui
divergeait était la *définition*, pas le *résultat*. Et le troisième compte
soupçonné (`user_programs.py`, `existing_set_count`) ne mesure pas une charge :
il énonce ce qu'une régénération **détruirait**. Trois questions différentes,
pas trois réponses à la même.

`getattr(rt, "is_warmup", False)` tient donc les deux arbres avec une seule
phrase, et reste juste si le catalogue gagnait un jour la colonne.

OÙ VIVENT LES ZONES
-------------------
Pas ici. `zones_for_names` est dans `template_zone_context`, son module
d'origine, et c'est **le seul** résolveur de zones du produit. Une première
écriture de cette tranche en avait posé un second ici, avec ses propres
constantes d'état — un doublon qui aurait divergé au premier changement de
taxonomie. Les deux arbres ne nomment pas leur champ pareil
(`TemplateExercise.name` / `UserProgramExercise.exercise_name`) ; c'est
l'appelant qui porte cette différence, pas le résolveur.
"""
from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.services.template_zone_context import TemplateZones, zones_for_names
from app.templating import pluriel


def work_sets(rep_targets) -> int:
    """Séries de travail = plages de reps prescrites, **hors échauffement**.

    LA définition du produit, une seule fois. Voir l'en-tête du module pour
    pourquoi il n'y en avait jamais vraiment eu deux.
    """
    return sum(1 for rt in rep_targets if not getattr(rt, "is_warmup", False))


def _load_shape(sets: int, exercises: int) -> str:
    """La CHARGE, dite avec le descripteur que le type supporte vraiment.

    ⚠ Aucun champ numérique universel (§4). Une séance sans série prescrite ne
    rend pas « 0 séries » — un zéro se lit comme un manque, alors que le LISS
    pur est complet tel quel. Elle dit ce qu'elle est.

    ⚠ Aucune DURÉE, jamais (§5). Le catalogue contient « Session courte — Full
    upper 45 min » et prescrit 18 séries sur 7 exercices, à peine moins que
    Push A (21). La durée n'existe pas comme donnée structurée, et une décision
    antérieure a refusé de l'estimer. Le nom reste un nom ; il n'est ni analysé,
    ni corrigé, ni promu en champ.
    """
    ex = f"{exercises} {pluriel('exercice', exercises)}"
    if sets <= 0:
        if exercises <= 0:
            return "aucune série prescrite"
        return f"aucune série prescrite · {ex}"
    return f"{sets} {pluriel('série', sets)} · {ex}"


@dataclass(frozen=True)
class SessionRow:
    """Une séance — du catalogue, ou d'un programme.

    Elle est **démarrable ou non** selon ce que le domaine sait faire d'elle
    (`is_startable`). Une séance de brouillon existe, se décrit, se compare, et
    ne se démarre pas.
    """

    key: str
    name: str
    #: `strength` / `cardio` — identifiant technique, traduit à l'affichage.
    kind: str
    sets: int
    exercises: int
    zones: TemplateZones
    #: Slug du gabarit : ce qu'on démarre. `None` pour une séance de programme
    #: que le domaine ne sait pas encore exécuter — brouillon, ou séance jamais
    #: matérialisée en gabarit.
    slug: str | None = None
    #: Renseigné pour une séance de programme publié : le démarrage passe alors
    #: par la route du programme, qui trace l'origine.
    program_id: int | None = None
    session_id: int | None = None

    is_program = False

    @property
    def is_startable(self) -> bool:
        """Le domaine sait-il exécuter cette séance ?

        ⚠ Ce n'est PAS un détail d'affichage. Une séance de brouillon existe,
        se décrit, se compare — et ne se démarre pas. Lui prêter une commande
        promettrait une exécution que rien derrière ne sait honorer.
        """
        return self.slug is not None

    @property
    def load_shape(self) -> str:
        return _load_shape(self.sets, self.exercises)


@dataclass(frozen=True)
class ProgramRow:
    """Un programme — une COMPOSITION, pas une séance.

    Aucun champ de démarrage, et c'est le point : le domaine n'expose aucune
    façon de « démarrer un programme ». Ses séances publiées, elles, se
    démarrent — et ce sont des `SessionRow`, dans `sessions`.
    """

    key: str
    program_id: int
    name: str
    status: str
    #: TOUTES les séances du programme, démarrables ou non.
    #:
    #: ⚠ Une première écriture n'y mettait que les démarrables et réduisait les
    #: autres à une liste de noms. Conséquence mesurée au rendu : sur un
    #: brouillon — l'état où un programme passe le plus clair de sa vie —
    #: **aucune** séance n'était dépliable, donc l'état `ZONES_UNKNOWN` ne
    #: pouvait jamais s'afficher. Une branche que son entrée n'atteint jamais
    #: n'est pas une précaution, c'est du code mort qui se croit vivant.
    sessions: tuple[SessionRow, ...] = ()
    exercises: int = 0

    is_program = True

    @property
    def session_count(self) -> int:
        return len(self.sessions)

    @property
    def load_shape(self) -> str:
        """La composition, dite dans l'unité du type : des SÉANCES.

        Un programme ne s'annonce pas en séries — ce serait additionner des
        objets que l'utilisateur ne fait pas le même jour.
        """
        n = self.session_count
        if n <= 0:
            return "aucune séance"
        seances = f"{n} {pluriel('séance', n)}"
        if self.exercises <= 0:
            return seances
        return f"{seances} · {self.exercises} {pluriel('exercice', self.exercises)}"

    @property
    def startable(self) -> tuple[SessionRow, ...]:
        """Les séances que le domaine sait exécuter — souvent aucune."""
        return tuple(s for s in self.sessions if s.is_startable)


@dataclass(frozen=True)
class LoadoutGroup:
    """Un rang du registre. `key` sert aux gardes, `label` à l'écran."""

    key: str
    label: str
    rows: tuple

    def __bool__(self) -> bool:
        return bool(self.rows)


# ── construction du registre ───────────────────────────────────────────────


def session_key(slug: str) -> str:
    return f"t-{slug}"


def program_key(program_id: int) -> str:
    return f"p-{program_id}"


def build_session_row(db: Session, tpl, declared: dict, seen: dict) -> SessionRow:
    """Projette UN gabarit de catalogue en ligne de registre."""
    exercises = list(tpl.exercises)
    return SessionRow(
        key=session_key(tpl.slug),
        name=tpl.name,
        kind=getattr(tpl, "kind", "strength"),
        sets=sum(work_sets(ex.rep_targets) for ex in exercises),
        exercises=len(exercises),
        zones=zones_for_names(db, (ex.name for ex in exercises), declared, seen),
        slug=tpl.slug,
    )


def build_program_row(db: Session, program, declared: dict, seen: dict) -> ProgramRow:
    """Projette UN programme utilisateur en ligne de registre.

    Une séance n'entre dans `sessions` — donc ne devient démarrable — que si le
    domaine la dit démarrable : programme **publié**, **non archivé**, et séance
    **matérialisée** en gabarit. C'est exactement la condition que la page de
    détail applique déjà (`user_programs/detail.html`) ; elle est reprise, pas
    réinventée, parce qu'une seconde écriture de la même règle finirait par
    diverger.
    """
    published = program.status == "published" and program.archived_at is None

    rows: list[SessionRow] = []
    total_exercises = 0

    for s in program.sessions:
        exercises = list(s.exercises)
        total_exercises += len(exercises)
        slug = s.template_slug_snapshot
        startable = bool(published and s.published_template_id and slug)
        rows.append(
            SessionRow(
                key=f"{program_key(program.id)}-s{s.id}",
                name=s.name,
                kind=getattr(s, "kind", "strength"),
                sets=sum(work_sets(ex.rep_targets) for ex in exercises),
                exercises=len(exercises),
                zones=zones_for_names(
                    db, (ex.exercise_name for ex in exercises), declared, seen
                ),
                # Le slug — donc la capacité de démarrer — n'est porté que si le
                # domaine la donne vraiment. Une séance non démarrable se
                # décrit et se compare ; elle ne s'exécute pas.
                slug=slug if startable else None,
                program_id=program.id if startable else None,
                session_id=s.id if startable else None,
            )
        )

    return ProgramRow(
        key=program_key(program.id),
        program_id=program.id,
        name=program.title,
        status=program.status,
        sessions=tuple(rows),
        exercises=total_exercises,
    )


def row_matches_zone(row, code: str) -> bool:
    """Le filtre garde-t-il cette ligne, et peut-elle le justifier ?

    Un programme est gardé dès qu'une de ses séances travaille la zone —
    l'écarter parce que la zone n'est pas sur le programme lui-même cacherait
    une configuration qui répond pourtant à la demande.
    """
    if row.is_program:
        return any(row_matches_zone(s, code) for s in row.sessions)
    return any(z.code == code for z in row.zones.zones)
