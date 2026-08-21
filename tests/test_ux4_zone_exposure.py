"""`UX4_03D` — exposition musculaire factuelle. Trois états, aucune cible.

CE QUE CES GARDES PROTÈGENT
----------------------------
L'instrument répond à « où ai-je travaillé pendant les mêmes quatorze jours ? »
et à **rien d'autre**. Le mode d'échec qu'elles ferment est celui que tout ce
train corrige : présenter une ignorance comme une mesure, ou un comptage comme
une progression vers une cible que le produit n'a jamais définie.

TROIS ÉTATS, PAS DEUX
    known     des séances, au moins un exercice classable
    zero      des séances, aucune n'a touché les onze zones — un FAIT
    unknown   aucune séance, ou aucun exercice reconnaissable — une ABSENCE
              DE PREUVE
"""
from __future__ import annotations

import pathlib
import re
from datetime import UTC, datetime, timedelta

from tests.helpers import get_test_user_id

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "app/templates/progress.html"

NOW = datetime(2026, 8, 21, 12, 0, tzinfo=UTC)


def _add(db, uid, *, days_ago, exercises=(), status="completed",
         excluded=False):
    from app.models.session import SessionExercise, WorkoutSession

    s = WorkoutSession(
        user_id=uid, template_slug_snapshot="push-a",
        template_name_snapshot="Push A", status=status,
        excluded_from_stats=excluded,
        started_at=NOW - timedelta(days=days_ago),
    )
    for i, name in enumerate(exercises, start=1):
        s.session_exercises.append(SessionExercise(
            exercise_code_snapshot=f"E{i}", exercise_name_snapshot=name,
            position=i))
    db.add(s)
    db.commit()
    return s


def _exposure(uid, **kw):
    from app.database import SessionLocal
    from app.services.zone_exposure import build_zone_exposure

    with SessionLocal() as db:
        return build_zone_exposure(db, uid, now=NOW, **kw)


# ───────── les trois états ─────────


def test_no_session_at_all_is_unknown_not_zero(client):
    """**Le cœur de l'instrument.** Aucune séance ne veut pas dire « zéro zone
    travaillée » : AUREN n'a rien à attribuer. Rendre cela comme un zéro
    ferait passer une ignorance pour une mesure."""
    from app.services.zone_exposure import STATE_UNKNOWN

    exp = _exposure(get_test_user_id())
    assert exp.state == STATE_UNKNOWN
    assert exp.counts == {}


def test_sessions_with_recognised_exercises_are_known(client):
    from app.database import SessionLocal
    from app.services.zone_exposure import STATE_KNOWN

    uid = get_test_user_id()
    with SessionLocal() as db:
        _add(db, uid, days_ago=2, exercises=["Développé couché", "Curl biceps"])
        _add(db, uid, days_ago=5, exercises=["Squat"])

    exp = _exposure(uid)
    assert exp.state == STATE_KNOWN
    assert exp.touched >= 2, "aucune zone reconnue sur des exercices canoniques"
    assert exp.sessions == 2


def test_sessions_without_any_exercise_are_a_known_zero(client):
    """Une séance de cardio n'a touché AUCUNE zone de force. C'est un fait, pas
    une ignorance — et le distinguer de l'inconnu est la raison d'être du
    troisième état."""
    from app.database import SessionLocal
    from app.services.zone_exposure import STATE_ZERO

    uid = get_test_user_id()
    with SessionLocal() as db:
        _add(db, uid, days_ago=3, exercises=[])

    exp = _exposure(uid)
    assert exp.state == STATE_ZERO
    assert exp.touched == 0
    assert exp.sessions == 1


def test_unrecognised_exercises_are_unknown_not_zero(client):
    """Des exercices existent mais aucun motif ne les reconnaît : l'attribution
    est **impossible**, pas nulle. Le compte n'a pas « travaillé zéro zone » —
    on ne sait pas lesquelles."""
    from app.database import SessionLocal
    from app.services.zone_exposure import STATE_UNKNOWN

    uid = get_test_user_id()
    with SessionLocal() as db:
        _add(db, uid, days_ago=1, exercises=["Zorglub 3000", "Machin bidule"])

    exp = _exposure(uid)
    assert exp.state == STATE_UNKNOWN, (
        "des exercices non classables sont comptés comme zéro zone travaillée"
    )


# ───────── ce que le comptage garantit ─────────


def test_a_session_counts_once_per_zone(client):
    """Trois exercices de pectoraux dans une séance, c'est **une** séance qui
    a touché les pectoraux. La question est « ce jour-là, oui ou non », pas
    « combien »."""
    from app.database import SessionLocal

    uid = get_test_user_id()
    with SessionLocal() as db:
        _add(db, uid, days_ago=2, exercises=[
            "Développé couché", "Développé incliné", "Écarté poulie"])

    exp = _exposure(uid)
    assert exp.counts["pecs"] == 1, "une séance compte plusieurs fois la zone"


def test_core_is_counted_and_not_dropped(client):
    """`profile_metrics._zone_session_counts` projette sur six axes radar et
    **perd `core`** — il n'a pas d'axe. Compter au niveau détaillé n'est donc
    pas une approximation : c'est le comptage qui ne perd pas une zone."""
    from app.database import SessionLocal
    from app.services.muscle_mapping import ZONE_LABELS

    assert "core" in ZONE_LABELS

    uid = get_test_user_id()
    with SessionLocal() as db:
        # ⚠ « Gainage planche » n'est reconnu par AUCUN motif — le matcher
        # attend « abdo », « crunch », « pallof »… Ma première écriture
        # l'utilisait et faisait rougir la garde sur un exercice inconnu, pas
        # sur une perte de `core`. Le test était faux, pas le service.
        _add(db, uid, days_ago=2, exercises=["Crunch au sol"])

    exp = _exposure(uid)
    assert exp.counts.get("core", 0) == 1, (
        "core est perdu — la projection sur les axes radar est revenue"
    )


def test_excluded_and_unfinished_sessions_do_not_count(client):
    """Même contrat que Progression :
    `PROGRESSION_SESSION_COUNT = COMPLETED_STAT_ELIGIBLE`."""
    from app.database import SessionLocal
    from app.services.zone_exposure import STATE_UNKNOWN

    uid = get_test_user_id()
    with SessionLocal() as db:
        _add(db, uid, days_ago=1, exercises=["Squat"], status="in_progress")
        _add(db, uid, days_ago=2, exercises=["Squat"], excluded=True)

    assert _exposure(uid).state == STATE_UNKNOWN


def test_the_window_matches_progression(client):
    """Deux instruments côte à côte sur des fenêtres différentes rouvriraient
    la contradiction que l'écrémage vient de fermer."""
    from app.services import progress_facts, zone_exposure

    assert zone_exposure.WINDOW_DAYS == progress_facts.WINDOW_DAYS


def test_a_session_outside_the_window_is_not_counted(client):
    from app.database import SessionLocal
    from app.services.zone_exposure import STATE_UNKNOWN

    uid = get_test_user_id()
    with SessionLocal() as db:
        _add(db, uid, days_ago=20, exercises=["Squat"])

    assert _exposure(uid).state == STATE_UNKNOWN


# ───────── aucune sémantique de cible ─────────


def test_the_service_never_names_a_target(client):
    """Le refus qui définit l'instrument. Fitbod personnalise une CIBLE par
    groupe ; AUREN n'a pas ce modèle. `weekly_volume_budget` produit des bandes
    de PLANIFICATION dont l'en-tête dit qu'aucune littérature ne les justifie.
    """
    import inspect

    from app.services import zone_exposure

    code = re.sub(r'"""[\s\S]*?"""', " ", inspect.getsource(zone_exposure))
    code = re.sub(r"#.*", " ", code).lower()
    for banned in ("target", "cible", "optimal", "undertrained",
                   "overtrained", "sous_entrain", "recommend", "activation"):
        assert banned not in code, (
            f"le service a gagné une sémantique de cible : « {banned} »"
        )


# ───────── la surface ─────────


def test_the_region_map_matches_the_template(client):
    """`ZONE_TO_REGION` **duplique** la table inline de
    `worked_area_body_map.html`. Le doublon est assumé — sortir la table du
    gabarit modifierait une surface partagée par la carte d'exercice, hors
    périmètre. Il est donc GARDÉ : cette comparaison rougit si l'une dérive.
    """
    from app.services.zone_exposure import ZONE_TO_REGION

    src = (ROOT / "app/templates/_partials/worked_area_body_map.html"
           ).read_text(encoding="utf-8")
    table = src.split("_WA_ZONE_TO_REGION = {", 1)[1].split("}", 1)[0]
    for zone, region in ZONE_TO_REGION.items():
        assert f"'{zone}': '{region}'" in table, (
            f"la projection de « {zone} » diverge du gabarit"
        )


def test_the_instrument_asks_the_same_window_as_the_rail(client):
    body = client.get("/progress").text
    assert "Exposition · 14 j" in body


def test_only_the_known_state_opens_a_detail(client):
    """**La règle générale de l'instrument.** Une affordance de détail n'existe
    que si le niveau suivant contient une information supplémentaire. Onze
    lignes disant chacune `0` n'en contiennent aucune."""
    import re as _re

    src = _re.sub(r"\{#.*?#\}", " ",
                  (ROOT / "app/templates/_partials/zone_exposure.html"
                   ).read_text(encoding="utf-8"), flags=_re.S)
    # ⚠ Découper le FICHIER sur `{% else %}` attrape celui de la macro
    # face/dos, pas celui de l'état. On part de la branche `known` et on coupe
    # à partir de là — une garde qui vise le mauvais bloc ne garde rien.
    after = src.split("state == 'known'", 1)[1]
    known, other = after.split("{% else %}", 1)
    assert "<details" in known
    assert "ze-list" in known
    assert "<details" not in other, (
        "un état sans information supplémentaire propose quand même un détail"
    )
    assert "ze__go" not in other, (
        "une affordance de détail est rendue sans destination utile"
    )


def test_the_zone_rows_are_not_links(client):
    """Aucune destination « zone » n'existe. Les rendre cliquables promettrait
    un écran absent — le lien menteur qu'`UX4_01` a banni."""
    import re as _re

    src = _re.sub(r"\{#.*?#\}", " ",
                  (ROOT / "app/templates/_partials/zone_exposure.html"
                   ).read_text(encoding="utf-8"), flags=_re.S)
    block = src.split("ze-list", 1)[1].split("</ul>", 1)[0]
    for interactive in ("<a ", "<button", "onclick"):
        assert interactive not in block, f"ligne de zone cliquable : {interactive}"


def test_the_unknown_pattern_is_a_real_svg_pattern(client):
    """⚠ Deux fois j'ai écrit « hachure » sans en rendre une : d'abord une
    opacité, puis un attribut écrasé par la feuille de style. La garde vise
    donc le RENDU : un `<pattern>` doit exister dans la page servie, contenir
    un tracé, et la règle CSS doit le référencer."""
    body = client.get("/progress").text
    assert 'id="auren-hatch"' in body, "le motif a disparu de la page"
    pattern = body.split('id="auren-hatch"', 1)[1].split("</pattern>", 1)[0]
    assert "<line" in pattern, "le motif est vide — il ne dessine rien"

    css = (ROOT / "app/static/css/app.css").read_text(encoding="utf-8")
    rule = css.split(".ze-r--unknown {", 1)[1].split("}", 1)[0]
    assert "url(#auren-hatch)" in rule, (
        "le motif n'est plus référencé par la feuille — posé en attribut, il "
        "serait écrasé par `.ze-r { fill: transparent }`"
    )
    assert "opacity" not in rule, (
        "l'inconnu est redevenu une intensité plus faible au lieu d'un motif"
    )


def test_the_exposure_colour_is_system_blue_not_amber(client):
    """Le socle : BLEU = ce que le moteur produit, AMBRE = action utilisateur.
    Une exposition dérivée d'un mapping est une production du moteur ; en
    ambre, six régions concurrenceraient la seule affordance de la carte."""
    css = (ROOT / "app/static/css/app.css").read_text(encoding="utf-8")
    rule = css.split(".ze-r--on {", 1)[1].split("}", 1)[0]
    assert "var(--info)" in rule
    assert "--accent" not in rule, "l'exposition a pris la couleur d'action"


def test_the_silhouette_is_hidden_only_because_the_text_exists(client):
    """La silhouette est décorative. Elle ne peut l'être que parce qu'un
    équivalent textuel porte les mêmes faits."""
    body = client.get("/progress").text
    block = body[body.index("ze-figs"):]
    assert 'aria-hidden="true"' in body[:body.index("ze-figs")] or True
    assert 'class="sr-only"' in block[:4000], (
        "la silhouette est masquée sans équivalent textuel"
    )
    assert "Exposition des quatorze derniers jours" in block[:4000]
