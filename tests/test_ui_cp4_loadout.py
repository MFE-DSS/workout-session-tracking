"""`UI-CP4 LOADOUT` — les gardes du REGISTRE TYPÉ.

CE QUE CES GARDES FERMENT
--------------------------
L'arbitrage opérateur a corrigé la proposition sur trois points, et chacun se
franchit sans que le rendu proteste :

1. **UN PROGRAMME GAGNE UN DÉMARRAGE QU'IL N'A PAS.** Le domaine n'expose
   aucune façon de « démarrer un programme » ; on démarre l'une de ses séances.
   Une liste plate d'objets « sémantiquement identiques » y mène en une ligne.
2. **LES TROIS ABSENCES DE ZONE SE REFONDENT EN UN SEUL VIDE.** C'est l'état
   d'avant CP4, et il ressemble à une page propre.
3. **L'AMBRE REDEVIENT UNE CATÉGORIE.** 53 occurrences dans trois rôles, sur un
   écran — sans qu'aucun test ne le voie jamais.

S'y ajoutent les gardes de CAPACITÉ (`CLAUDE.md §5.3`) : une fusion de deux
surfaces est l'occasion parfaite de perdre une action en silence.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIB_TPL = ROOT / "app/templates/library.html"
BASE_TPL = ROOT / "app/templates/base.html"
LOADOUT = ROOT / "app/services/loadout.py"

URL = "/library"
PUSH_A = "t-push-a"


def _uid() -> int:
    from tests.helpers import get_test_user_id

    return get_test_user_id()


def _make_program(title: str, slug_base: str, *, publish: bool = False) -> int:
    """Un programme réel, produit par les VRAIS services.

    Fabriquer un `UserProgram` à la main en base produirait un objet que le
    produit ne sait pas créer — un labo qui ne représente rien.
    """
    from app.database import SessionLocal
    from app.services.user_program_drafts import create_draft

    with SessionLocal() as db:
        prog = create_draft(db, _uid(), title=title, slug_base=slug_base)
        db.commit()
        return prog.id


# ═════════ 1. L'ONTOLOGIE EST TYPÉE, ET LE TYPE EST STRUCTUREL ═════════


def test_a_program_row_cannot_carry_a_start_command_at_all():
    """LA GARDE LA PLUS IMPORTANTE DU FICHIER, et elle est statique.

    `ProgramRow` n'a **aucun** champ qui pourrait porter un démarrage : pas de
    slug, pas d'identifiant de séance. Un START inventé pour un programme n'est
    pas seulement interdit par une revue — il est *inexprimable*.

    Une garde de rendu aurait vérifié qu'on ne l'affiche pas aujourd'hui ; celle
    -ci vérifie qu'on ne *peut pas* l'afficher demain.
    """
    from app.services.loadout import ProgramRow

    champs = set(ProgramRow.__dataclass_fields__)
    for interdit in ("slug", "session_id", "template_slug"):
        assert interdit not in champs, (
            f"`ProgramRow` porte « {interdit} » : le type ne protège plus rien"
        )


def test_the_two_row_types_are_two_classes_not_a_flag():
    """Un drapeau `kind` sur une classe unique laisserait les deux sémantiques
    partager tous leurs champs — donc se confondre au premier oubli de test."""
    from app.services.loadout import ProgramRow, SessionRow

    assert ProgramRow is not SessionRow
    assert ProgramRow.is_program is True
    assert SessionRow.is_program is False


def test_a_draft_program_exposes_no_start_anywhere(client):
    """Un brouillon se décrit, se compare — et ne se démarre pas."""
    pid = _make_program("Brouillon témoin", "brouillon-temoin")
    body = client.get(f"{URL}?loadout=p-{pid}").text
    assert "Brouillon témoin" in body, "le témoin n'est pas rendu"
    assert "Brouillon" in body, "l'état de cycle de vie ne se voit pas"
    assert 'name="template_slug"' not in body
    assert "/start" not in body


def test_both_origins_live_in_the_same_register(client):
    """La fusion est PERÇUE. Deux surfaces répondaient à une seule question."""
    _make_program("Mon programme", "mon-programme")
    body = client.get(URL).text
    assert "Mes programmes" in body
    assert "Mon programme" in body
    assert "Push A" in body, "le catalogue a disparu du registre"


# ═════════ 2. UNE SEULE FORMULE DE SÉRIES DE TRAVAIL ═════════


def test_work_sets_excludes_warmups_on_both_trees():
    """LA définition du produit, et elle vaut pour les deux arbres.

    Le catalogue n'a aucune colonne `is_warmup` (les échauffements y sont
    générés à l'instanciation) ; les programmes en ont une. Une seule phrase
    doit tenir les deux, sinon deux surfaces annonceront deux volumes pour le
    même objet.
    """
    from app.services.loadout import work_sets

    class _Cible:
        def __init__(self, warm=None):
            if warm is not None:
                self.is_warmup = warm

    # Arbre catalogue : aucun attribut `is_warmup` du tout.
    assert work_sets([_Cible(), _Cible(), _Cible()]) == 3
    # Arbre programme : l'échauffement ne compte pas.
    assert work_sets([_Cible(True), _Cible(False), _Cible(False)]) == 2
    assert work_sets([]) == 0


def test_no_second_work_set_formula_is_introduced():
    """Garde STRUCTURELLE : le module ne doit pas se remettre à compter seul."""
    import app.services.loadout as mod
    from tests.helpers import module_code_only

    code = module_code_only(mod)
    # Une seule définition, et tout le module passe par elle.
    assert code.count("def work_sets(") == 1
    assert "len(ex.rep_targets)" not in code, (
        "un comptage brut de plages de reps réintroduit la formule sans "
        "l'échauffement — c'est la divergence que CP4 vient de fermer"
    )


# ═════════ 3. LES TROIS ABSENCES NE SE CONFONDENT PAS (§7) ═════════


def test_the_three_zone_states_are_three_distinct_values():
    from app.services.template_zone_context import (
        ZONES_MAPPED,
        ZONES_NONE_DEFINED,
        ZONES_UNKNOWN,
    )

    assert len({ZONES_MAPPED, ZONES_NONE_DEFINED, ZONES_UNKNOWN}) == 3


def test_no_exercise_at_all_is_KNOWN_not_unknown(client):
    """« Aucune zone prescrite » est une CONNAISSANCE.

    Le LISS pur n'a aucun exercice : le produit SAIT qu'il ne cible aucune zone
    cartographiée. Le ranger sous « inconnu » ferait passer une certitude pour
    une lacune.
    """
    from app.database import SessionLocal
    from app.services.template_zone_context import ZONES_NONE_DEFINED, zones_for_names

    with SessionLocal() as db:
        ev = zones_for_names(db, [], {}, {})
    assert ev.state == ZONES_NONE_DEFINED
    assert ev.zones == ()

    body = client.get(f"{URL}?loadout=t-liss-only").text
    assert "Aucune zone prescrite" in body
    assert "non cartographiées" not in body


def test_unrecognised_exercises_are_UNKNOWN_not_an_absence():
    """Des exercices EXISTENT et aucun n'est reconnu : le seul vrai UNKNOWN."""
    from app.database import SessionLocal
    from app.services.template_zone_context import ZONES_UNKNOWN, zones_for_names

    with SessionLocal() as db:
        ev = zones_for_names(
            db, ["Tirage maison à la sangle", "Presse artisanale inclinée"], {}, {}
        )
    assert ev.state == ZONES_UNKNOWN, (
        "ces noms sont résolus par le référentiel — le témoin ne témoigne plus"
    )
    assert ev.zones == ()


def test_no_priority_match_is_KNOWN_and_writes_no_reproach():
    """Des zones existent, aucune n'est déclarée — et RIEN ne s'écrit.

    Les zones elles-mêmes sont rendues, sans marque : leur présence dit
    l'absence mieux qu'une phrase, et l'écrire en ferait un reproche (`A4`).
    """
    from app.database import SessionLocal
    from app.services.template_zone_context import ZONES_MAPPED, zones_for_names

    with SessionLocal() as db:
        ev = zones_for_names(db, ["Développé couché"], {}, {})

    assert ev.state == ZONES_MAPPED
    assert ev.zones, "le témoin ne résout plus aucune zone"
    assert ev.is_no_priority_match
    assert not ev.declared


def test_the_unknown_state_is_not_distinguished_by_colour_alone():
    """`Sx_UIV3_00 §7` — un inconnu porte toujours un libellé."""
    src = LIB_TPL.read_text(encoding="utf-8")
    assert "Zones non cartographiées" in src


# ═════════ 4. UN SEUL PROPRIÉTAIRE D'ACTION ═════════


def test_the_closed_register_owns_no_action_at_all(client):
    body = client.get(URL).text
    assert "loadout__go" not in body


def test_at_most_one_dominant_command_in_every_open_state(client):
    """L'ambre désigne une décision, jamais une catégorie.

    Mesuré avant CP4 : 53 occurrences d'ambre sur un écran, dans trois rôles
    (0 aplat, 11 bordures, 42 textes).
    """
    pid = _make_program("Programme témoin", "programme-temoin")
    for key in (PUSH_A, "t-liss-only", "t-legs-a", f"p-{pid}"):
        body = client.get(f"{URL}?loadout={key}").text
        n = body.count("loadout__go")
        assert n <= 1, f"« {key} » expose {n} commandes dominantes"


def test_a_declared_zone_is_not_painted_with_the_action_colour():
    """`--t-amber` est « action utilisateur · objet actif ». Une priorité
    déclarée n'est ni l'un ni l'autre : c'est un rappel de ce que l'utilisateur
    a dit. La colorier en ambre est exactement ce qui a produit 42 textes ambre
    sur un écran."""
    from tests.helpers import css_sans_commentaires

    css = css_sans_commentaires(
        (ROOT / "app/static/css/app.css").read_text(encoding="utf-8")
    )
    regle = css.split(".loadout__zone.is-declared {", 1)[1].split("}", 1)[0]
    assert "--t-amber" not in regle, "la marque de priorité reprend l'ambre d'action"
    # Deux canaux non colorimétriques, pour ne pas distinguer par la couleur seule.
    assert "font-weight" in regle
    assert "border-bottom-width" in regle


# ═════════ 5. AUCUNE DURÉE INVENTÉE (§5) ═════════


def test_no_duration_is_ever_derived_or_rendered():
    """« Session courte — Full upper 45 min » prescrit 18 séries sur 7
    exercices, à peine moins que Push A (21). La durée est dans le NOM ; elle
    n'existe pas comme donnée, et une décision antérieure a refusé de l'estimer.
    Le nom reste un nom : ni analysé, ni corrigé, ni promu en champ."""
    import app.services.loadout as mod
    from tests.helpers import module_code_only

    code = module_code_only(mod)
    for interdit in ("duration", "minute", "45", "temps_estime"):
        assert interdit not in code.lower(), (
            f"le registre touche à la durée : « {interdit} »"
        )


def test_the_name_is_rendered_verbatim_not_parsed(client):
    body = client.get(URL).text
    assert "Session courte — Full upper 45 min" in body
    assert "18 séries" in body, "la charge réelle n'est pas dite"


# ═════════ 6. `?loadout=` EST UN ÉTAT DE PRÉSENTATION, PAS DE DOMAINE ═════════


def test_selecting_a_row_writes_nothing(client):
    """Aucune persistance : le domaine n'a aucune « configuration active », et
    en inventer une ici créerait une sémantique que rien ne soutient."""
    from app.database import SessionLocal
    from app.models.decision_trace import DecisionTrace

    with SessionLocal() as db:
        avant = db.query(DecisionTrace).count()
    client.get(f"{URL}?loadout={PUSH_A}")
    client.get(f"{URL}?loadout=t-legs-a")
    with SessionLocal() as db:
        assert db.query(DecisionTrace).count() == avant


def test_an_unknown_selection_key_is_ignored_rather_than_rendered(client):
    """Une clé bricolée ne peut venir que d'une URL trafiquée."""
    body = client.get(f"{URL}?loadout=t-pas-un-gabarit").text
    assert "loadout__open" not in body
    assert "pas-un-gabarit" not in body


def test_the_register_needs_no_javascript():
    src = LIB_TPL.read_text(encoding="utf-8")
    assert "<script" not in src
    assert "addEventListener" not in src


# ═════════ 7. CAPACITÉS PRÉSERVÉES (`CLAUDE.md §5.3`) ═════════


def test_creating_a_program_stays_reachable_with_zero_programs(client):
    """LE PIÈGE LE PLUS VICIEUX DE CETTE TRANCHE.

    L'entrée de coque « Mes programmes » disparaît. Si le rang s'effaçait faute
    de programme, créer un programme deviendrait inatteignable pour exactement
    l'utilisateur qui en a le plus besoin — et l'anomalie serait **invisible sur
    un compte peuplé**, donc invisible sur toute capture de démonstration.
    """
    body = client.get(URL).text
    assert "Mes programmes" in body
    assert "Aucun programme personnel" in body
    assert "Créer un programme" in body


def test_opening_a_program_stays_reachable(client):
    pid = _make_program("Programme ouvrable", "programme-ouvrable")
    body = client.get(f"{URL}?loadout=p-{pid}").text
    assert f"/programs/{pid}" in body, "le programme n'est plus ouvrable"


def test_the_removed_shell_entries_left_no_dead_route(client):
    """Les deux liens secondaires partent ; AUCUNE route n'est supprimée.

    ⚠ La garde lit le gabarit SANS SES COMMENTAIRES. Première écriture : elle
    tombait sur le commentaire qui explique justement le retrait des deux
    variables — une garde qui lit sa propre prose comme du code, et ce dépôt
    en a déjà compté une douzaine.
    """
    assert client.get("/programs", follow_redirects=False).status_code == 200
    src = re.sub(r"\{#[\s\S]*?#\}", " ",
                 BASE_TPL.read_text(encoding="utf-8"))
    assert "is_my_programs" not in src, "variable orpheline laissée en place"
    assert "is_library" not in src


def test_declaring_priorities_stays_reachable(client):
    body = client.get(URL).text
    assert "/plan" in body


def test_filtering_by_zone_stays_reachable(client):
    body = client.get(URL).text
    assert "zone-filter__chip" in body
    assert "?zone=" in body


def test_starting_from_the_catalogue_still_works(client):
    r = client.post(
        "/sessions",
        data={"template_slug": "push-a", "creation_source": "library"},
        follow_redirects=False,
    )
    assert r.status_code in (200, 303), r.text[:200]


# ═════════ 8. LA LIGNE NE DÉMARRE PAS ═════════


def test_the_handle_navigates_it_never_posts(client):
    """La ligne SÉLECTIONNE. Le geste supplémentaire avant de démarrer est le
    prix assumé de l'interdiction du démarrage accidentel."""
    body = client.get(URL).text
    poignees = re.findall(r'<a class="loadout__handle"[\s\S]*?</a>', body)
    assert poignees, "aucune poignée rendue — la garde ne mesurerait rien"
    for p in poignees:
        assert "<form" not in p
        assert "method=" not in p
        assert "loadout=" in p, "une poignée qui ne sélectionne rien"


def test_the_load_shape_says_what_the_type_supports(client):
    """Aucun champ numérique universel : une séance sans série prescrite ne rend
    pas « 0 séries » — un zéro se lit comme un manque, alors que le LISS pur est
    complet tel quel."""
    from app.services.loadout import ProgramRow, SessionRow
    from app.services.template_zone_context import TemplateZones

    cardio = SessionRow(key="t-x", name="LISS", kind="cardio", sets=0,
                        exercises=0, zones=TemplateZones(), slug="x")
    assert cardio.load_shape == "aucune série prescrite"
    assert "0" not in cardio.load_shape

    force = SessionRow(key="t-y", name="Push", kind="strength", sets=21,
                       exercises=7, zones=TemplateZones(), slug="y")
    assert force.load_shape == "21 séries · 7 exercices"

    # Un programme s'annonce en SÉANCES : additionner ses séries reviendrait à
    # cumuler des objets que l'utilisateur ne fait pas le même jour.
    prog = ProgramRow(key="p-1", program_id=1, name="P", status="draft",
                      sessions=(cardio, force), exercises=7)
    assert prog.load_shape == "2 séances · 7 exercices"
    assert "série" not in prog.load_shape
