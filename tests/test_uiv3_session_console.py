"""`UIV3_SESSION_EXECUTION_CONSOLE_01` — l'état contrôle la commande.

POURQUOI CES GARDES EXISTENT
----------------------------
La console proposait **deux commandes concurrentes en permanence**. Mesuré à
390 px, l'étiquette de la seconde demandait ~180 px dans un bouton de 62 et se
peignait par-dessus la première : la coexistence était un artefact de
réparation, pas un besoin (`Sx_UIV3_02B §D2`).

Ces tests pinnent **les causes**, pas des pixels — la géométrie est mesurée au
navigateur et consignée dans le rapport de tranche, conformément à
`CLAUDE.md §5.1`.

**Un piège domine tous les autres** et justifie à lui seul la moitié du
module : `update_exercise_card` boucle sur TOUTES les `set_logs` et écrit
`sl.weight_kg = to_float(form.get(...))`. Un champ absent du DOM renvoie
`None`, donc **efface la série**. Les lignes compactes portent leurs valeurs en
`input type="hidden"` ; les retirer serait une perte de données silencieuse,
invisible à la lecture du gabarit.
"""
from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
CARD = ROOT / "app/templates/_partials/exercise_card.html"
DETAIL = ROOT / "app/templates/session_detail.html"
HEADER = ROOT / "app/templates/_partials/session_focus_header.html"
REST = ROOT / "app/templates/_partials/rest_timer.html"
JS = ROOT / "app/static/js/session_focus.js"
CSS = ROOT / "app/static/css/session_focus.css"


# ══════════════════════════════════════════════════════════════════════
#  Dérivation d'état — unitaire, sans HTTP
# ══════════════════════════════════════════════════════════════════════


class _Set:
    """Double minimal d'un `SetLog` : le service ne lit que ces attributs."""

    def __init__(self, id_, kind, index, completed=False):
        self.id = id_
        self.kind = kind
        self.set_index = index
        self.completed = completed
        self.weight_kg = 60.0 if completed else None
        self.reps = 10 if completed else None


class _Exercise:
    def __init__(self, sets):
        self.set_logs = sets


def _exercise(warmups=1, works=3, works_done=0, warmups_done=0):
    sets = [
        _Set(100 + i, "warmup", i + 1, i < warmups_done) for i in range(warmups)
    ] + [
        _Set(200 + i, "work", i + 1, i < works_done) for i in range(works)
    ]
    return _Exercise(sets)


def test_pending_warmup_wins_over_everything():
    from app.services.console_state import WARMUP, build_console_state

    st = build_console_state(_exercise(), next_code="E2")
    assert st.state == WARMUP
    assert st.current_set.kind == "warmup"


def test_work_set_becomes_current_once_warmups_are_done():
    from app.services.console_state import CURRENT_SET, build_console_state

    st = build_console_state(_exercise(warmups_done=1), next_code="E2")
    assert st.state == CURRENT_SET
    assert st.current_set.set_index == 1
    assert [s.set_index for s in st.future_sets] == [2, 3]


def test_rest_is_a_request_scoped_presentation_state():
    """`G4` — jamais persisté, jamais un champ, jamais un modèle.

    Il n'existe que parce qu'un paramètre de requête le dit, et il disparaît
    au rechargement suivant. Le persister ferait de la durée de repos une
    affirmation du produit alors qu'elle est une suggestion.
    """
    from app.services.console_state import (
        CURRENT_SET,
        REST,
        build_console_state,
    )

    ex = _exercise(warmups_done=1, works_done=1)
    assert build_console_state(ex, next_code="E2").state == CURRENT_SET
    assert build_console_state(
        ex, next_code="E2", rest_signal=True
    ).state == REST


def test_rest_never_survives_the_last_set():
    """Annoncer « repos » quand l'exercice est fini promettrait une série
    qui n'existe pas."""
    from app.services.console_state import EXERCISE_COMPLETE, build_console_state

    ex = _exercise(warmups_done=1, works=3, works_done=3)
    st = build_console_state(ex, next_code="E2", rest_signal=True)
    assert st.state == EXERCISE_COMPLETE


def test_last_exercise_is_distinguished_from_any_other():
    from app.services.console_state import (
        EXERCISE_COMPLETE,
        LAST_EXERCISE_COMPLETE,
        build_console_state,
    )

    ex = _exercise(warmups_done=1, works_done=3)
    assert build_console_state(ex, next_code="E2").state == EXERCISE_COMPLETE
    assert build_console_state(ex, next_code=None).state == LAST_EXERCISE_COMPLETE


def test_correction_outranks_the_exercise_progress():
    """Q3 — l'utilisateur a demandé à revenir sur une série validée. Cette
    demande ne doit pas être arbitrée par l'avancement de l'exercice."""
    from app.services.console_state import CORRECTION, build_console_state

    ex = _exercise(warmups_done=1, works_done=2)
    st = build_console_state(ex, next_code="E2", fix_set_id=200)
    assert st.state == CORRECTION
    assert st.current_set.id == 200


def test_correction_never_renders_a_completed_set_twice():
    """La garde que je n'avais pas écrite, et que Sonar a écrite pour moi.

    `future_sets` prenait « toutes les séries sauf la corrigée », ce qui y
    remettait les séries DÉJÀ validées — présentes aussi dans `past_sets`.
    Une série terminée sortait donc deux fois : en `✓` et en `○`, avec le
    même `id` d'ancre et les mêmes `name` de champs masqués.

    Aucun des 34 tests neufs ni des 1178 du broad sweep ne comparait
    `CORRECTION` à **deux** séries déjà validées. `Web:S7930` l'a vu.
    """
    from app.services.console_state import build_console_state

    ex = _exercise(warmups_done=1, works=3, works_done=2)
    st = build_console_state(ex, next_code="E2", fix_set_id=200)

    past_ids = {s.id for s in st.past_sets}
    future_ids = {s.id for s in st.future_sets}
    assert past_ids & future_ids == set(), (
        f"séries rendues deux fois : {past_ids & future_ids}"
    )
    # Et le futur ne contient QUE ce qui reste réellement à faire.
    still_pending = [s.completed for s in st.future_sets]
    assert still_pending == [False] * len(still_pending)


def test_a_hostile_fix_parameter_is_ignored_not_fatal():
    """Un paramètre d'URL est une entrée hostile. `?fix=999999` rend la page
    normalement — refuser bruyamment ferait d'un lien mal recopié un 500."""
    from app.services.console_state import CURRENT_SET, build_console_state

    ex = _exercise(warmups_done=1, works_done=1)
    assert build_console_state(
        ex, next_code="E2", fix_set_id=999999
    ).state == CURRENT_SET


def test_an_uncompleted_set_cannot_be_corrected():
    """Corriger une série jamais validée n'a pas de sens : c'est déjà la
    série courante."""
    from app.services.console_state import CURRENT_SET, build_console_state

    ex = _exercise(warmups_done=1, works_done=1)
    st = build_console_state(ex, next_code="E2", fix_set_id=201)
    assert st.state == CURRENT_SET


# ══════════════════════════════════════════════════════════════════════
#  Commandes — libellés figés par l'opérateur
# ══════════════════════════════════════════════════════════════════════


def test_exactly_one_dominant_command_per_state():
    from app.services.console_state import build_console_state, command_for

    # `D3 = B`, tranché par l'opérateur sur trois variantes rendues à 360 px.
    # Les codes `É`/`S` avaient quitté les lignes de série en `DF-C` ; le
    # bouton continuait de les employer, si bien que plus rien à l'écran ne
    # portait le nom qu'il annonçait. Le libellé reprend désormais le mot que
    # le nom accessible emploie déjà.
    cases = [
        (_exercise(), None, "VALIDER ÉCHAUFFEMENT 1"),
        (_exercise(warmups_done=1), None, "VALIDER SÉRIE 1"),
        (_exercise(warmups_done=1, works_done=3), "E2", "CONTINUER → E2"),
        (_exercise(warmups_done=1, works_done=3), None, "ALLER AU BILAN"),
    ]
    for ex, nxt, label in cases:
        cmd = command_for(build_console_state(ex, next_code=nxt))
        assert cmd["label"] == label, (label, cmd)


def test_valider_e2_is_definitively_gone():
    """`Valider · E2` faisait porter à une commande de SÉRIE la destination
    d'un EXERCICE. Il est supprimé, pas déplacé.

    Les commentaires sont retirés AVANT la recherche : la première écriture
    de cette garde a échoué sur sa propre prose, qui cite le libellé pour
    expliquer sa suppression. C'est la douzième fois que ce dépôt rencontre
    ce motif, et la première où il est attrapé à l'écriture."""
    markup = _uncommented(CARD.read_text(encoding="utf-8"))
    assert "Valider · E" not in markup
    assert "Enregistrer et passer à" not in markup


def test_early_exit_survives_at_every_incomplete_state():
    """Q2, tranché par l'opérateur — le produit ne force JAMAIS la complétion
    d'un exercice. Retirer cette sortie serait une soustraction seule, que
    `CLAUDE.md §5.3` interdit."""
    from app.services.console_state import build_console_state, secondary_for

    for ex in (_exercise(), _exercise(warmups_done=1),
               _exercise(warmups_done=1, works_done=1)):
        kinds = [s["kind"] for s in secondary_for(
            build_console_state(ex, next_code="E2")
        )]
        assert "skip" in kinds, kinds


def test_correction_offers_a_named_removal():
    """Q3 — vider les deux champs dé-complétait DÉJÀ la série, mais
    silencieusement, comme effet de bord d'un champ effacé par accident. La
    sémantique ne change pas : elle devient nommée."""
    from app.services.console_state import build_console_state, secondary_for

    ex = _exercise(warmups_done=1, works_done=2)
    labels = [s["label"] for s in secondary_for(
        build_console_state(ex, next_code="E2", fix_set_id=200)
    )]
    assert "RETIRER CETTE SÉRIE" in labels


def test_warmup_and_correction_do_not_start_a_rest():
    """Mesuré au navigateur : valider le dernier échauffement avec `nav=stay`
    faisait démarrer le décompte AVANT la première série de travail."""
    from app.services.console_state import build_console_state, command_for

    assert command_for(
        build_console_state(_exercise(), next_code="E2")
    )["nav"] == "stay_norest"
    assert command_for(
        build_console_state(
            _exercise(warmups_done=1, works_done=2),
            next_code="E2", fix_set_id=200,
        )
    )["nav"] == "stay_norest"
    assert command_for(
        build_console_state(_exercise(warmups_done=1), next_code="E2")
    )["nav"] == "stay"


# ══════════════════════════════════════════════════════════════════════
#  DeltaReadout — aucun faux delta
# ══════════════════════════════════════════════════════════════════════


def test_identical_reference_values_are_folded_not_repeated():
    from app.services.console_state import condense_reference

    assert condense_reference("57.5 / 57.5 / 57.5", "11 / 11 / 11") == (
        "57.5 kg × 11"
    )


def test_a_genuinely_varying_reference_keeps_its_detail():
    """Replier « 60 / 55 / 50 » en « 60 » inventerait une séance qui n'a pas
    eu lieu."""
    from app.services.console_state import condense_reference

    out = condense_reference("60 / 55 / 50", "10 / 9 / 8")
    assert "55" in out
    assert "50" in out


def test_no_reference_means_no_reference():
    from app.services.console_state import condense_reference

    assert condense_reference("", "") is None


def test_first_time_is_said_rather_than_faked():
    """`§7.12` — sans référence, « Première fois ». Jamais « Non disponible »,
    jamais une valeur inventée dans le champ."""
    markup = CARD.read_text(encoding="utf-8")
    assert "Première fois" in markup
    assert "Non disponible" not in markup


# ══════════════════════════════════════════════════════════════════════
#  Sérialisation — le piège qui efface des données
# ══════════════════════════════════════════════════════════════════════


def _uncommented(text: str) -> str:
    """Un commentaire Jinja n'est pas du balisage vivant.

    Onze gardes de ce dépôt ont déjà passé sur leur propre prose — et la
    douzième a été écrite dans ce module même, avant d'être corrigée.
    """
    return re.sub(r"\{#.*?#\}", "", text, flags=re.DOTALL)


def _js_code() -> str:
    """Le JS sans ses commentaires.

    Le bandeau d'en-tête de `session_focus.js` cite `data-start-rest` pour
    expliquer le défaut corrigé. Chercher la chaîne dans le fichier entier
    ferait échouer la garde sur l'explication du défaut plutôt que sur le
    défaut.
    """
    src = JS.read_text(encoding="utf-8")
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.DOTALL)
    return re.sub(r"//[^\n]*", "", src)


def test_compact_lines_still_carry_their_values():
    """Le POST lit `form.get("set_<id>_weight_kg")` pour CHAQUE série. Un
    champ absent renvoie `None` et efface la ligne. Les lignes passées et
    futures sont compactes à l'œil, intactes au POST."""
    markup = _uncommented(CARD.read_text(encoding="utf-8"))
    macro = re.search(r"macro set_values\(sl\)(.*?)endmacro", markup, re.DOTALL)
    assert macro, "la macro de conservation des valeurs a disparu"
    body = macro.group(1)
    assert 'type="hidden"' in body
    assert "set_{{ sl.id }}_weight_kg" in body
    assert "set_{{ sl.id }}_reps" in body


def test_every_rendered_line_kind_emits_both_field_names():
    """Passée, future, courante, échauffement replié : quatre rendus, un seul
    contrat de nom."""
    markup = _uncommented(CARD.read_text(encoding="utf-8"))
    for macro_name in ("past_line", "future_line"):
        block = re.search(
            rf"macro {macro_name}\(.*?endmacro", markup, re.DOTALL
        )
        assert block, macro_name
        assert "set_values(sl)" in block.group(0), macro_name


def test_the_visible_fields_keep_their_accessible_names():
    """Deux champs sans nom accessible annonçaient « zone de texte » sans dire
    de quelle série ni de quelle grandeur. Le placeholder ne fait pas
    étiquette : il disparaît à la saisie."""
    markup = _uncommented(CARD.read_text(encoding="utf-8"))
    block = re.search(r"macro set_inputs\(.*?endmacro", markup, re.DOTALL)
    assert block
    assert block.group(0).count("aria-label=") == 2
    assert 'inputmode="decimal"' in block.group(0)
    assert 'inputmode="numeric"' in block.group(0)


# ══════════════════════════════════════════════════════════════════════
#  D3 — le minuteur de repos ne tourne plus pendant la série
# ══════════════════════════════════════════════════════════════════════


def test_the_countdown_is_gated_on_the_server_signal():
    """LE défaut de la tranche précédente. Le gabarit émettait
    `data-rest-started` après une série réellement enregistrée ; le JS
    démarrait sur `[data-start-rest]`, rendu inconditionnellement. Personne ne
    lisait l'attribut. Mesuré : `running=True` sans qu'aucune série n'ait été
    saisie.

    Cette garde lit la SÉLECTION du JS, pas une chaîne de HTML — c'est
    précisément ce que les deux gardes précédentes ne faisaient pas.

    ⚠ `DF-B` — elle visait d'abord TOUTE sélection par attribut du fichier, et
    exigeait qu'il n'y en ait qu'une. C'était trop large : l'auto-validation a
    légitimement besoin de sa propre racine (`[data-session-form]`), qui n'a
    rien à voir avec le minuteur. La garde vise donc désormais la ligne qui
    assigne les RACINES DU MINUTEUR — ce qu'elle a toujours voulu protéger —
    et reste insensible aux sélections voisines."""
    js = _js_code()
    roots = re.findall(
        r"roots\s*=\s*document\.querySelectorAll\(\s*\"(\[[^\"]+\])\"", js)
    assert roots, "aucune sélection de racine de minuteur trouvée"
    assert roots == ["[data-rest-started]"], roots


def test_the_unconditional_start_attribute_is_gone():
    """`data-start-rest` était rendu sur toute carte active. Le laisser dans
    le gabarit rouvrirait le défaut à la première relecture du JS."""
    assert "data-start-rest" not in _uncommented(REST.read_text(encoding="utf-8"))
    assert "data-start-rest" not in _js_code()


def test_the_rest_readout_only_exists_in_the_rest_state():
    markup = _uncommented(CARD.read_text(encoding="utf-8"))
    include = markup.find('_partials/rest_timer.html')
    assert include != -1, "le minuteur n'est plus inclus du tout"
    before = markup[:include]
    assert "cs.is_resting" in before.rsplit("{% if", 1)[-1] or (
        "is_resting" in before[-400:]
    ), "le minuteur n'est plus gardé par l'état repos"


def test_the_rest_adjustment_never_persists():
    """Amendement C — 90 s est un repli de PRÉSENTATION. Un
    `rest_target_seconds` par exercice serait une prescription, donc une
    feature métier séparée."""
    js = JS.read_text(encoding="utf-8")
    for forbidden in ("localStorage", "sessionStorage", "fetch(",
                      "XMLHttpRequest", "navigator.sendBeacon"):
        assert forbidden not in js, forbidden


def test_skip_rest_speaks_french():
    """« Skip rest » au milieu d'une interface française était un vestige de
    maquette, pas une signature."""
    markup = _uncommented(CARD.read_text(encoding="utf-8"))
    assert "Skip rest" not in markup
    assert "PASSER LE REPOS" in ROOT.joinpath(
        "app/services/console_state.py"
    ).read_text(encoding="utf-8")


# ══════════════════════════════════════════════════════════════════════
#  Q1 — le rail collant est parti, la navigation est restée
# ══════════════════════════════════════════════════════════════════════


def test_no_sticky_layer_remains_on_the_session_surface():
    """Trois couches collantes se partageaient une bande de 109 px, en z et
    non en y : la bande `E1…E7` recouvrait le titre de la séance pendant
    toute l'exécution."""
    detail = _uncommented(DETAIL.read_text(encoding="utf-8"))
    header = _uncommented(
        ROOT.joinpath("app/templates/_partials/session_focus_header.html")
        .read_text(encoding="utf-8")
    )
    card = _uncommented(CARD.read_text(encoding="utf-8"))
    for name in ("session-focus__sticky-jump",
                 "session-focus__sticky-header",
                 "session-focus__sticky-cta"):
        assert name not in detail, name
        assert name not in header, name
        assert name not in card, name


def test_arbitrary_exercise_navigation_is_preserved():
    """Q1 amendé — la suppression part avec son remplaçant. Un déclencheur
    ouvre la MÊME liste d'ancres, en `details` natif donc sans JS. Aucune
    primitive nouvelle.

    Correction opérateur du même soir : le déclencheur EST `E1 / 7`, qui
    décrivait la position sans être actionnable. Le bloc a donc rejoint le
    partial d'en-tête, avec la position."""
    header = _uncommented(HEADER.read_text(encoding="utf-8"))
    assert 'class="session-head__nav ex-nav"' in header
    assert "#exercise-{{ se.id }}" in header
    assert "#session-feedback" in header
    assert "session-pos__current" in header, (
        "la position doit être le déclencheur, pas un libellé inerte"
    )


def test_the_navigation_trigger_is_reachable_without_js():
    header = _uncommented(HEADER.read_text(encoding="utf-8"))
    block = header[header.find('class="session-head__nav ex-nav"'):]
    block = block[:block.find("</details>")]
    assert "<summary" in block
    assert "onclick" not in block
    assert "data-js" not in block


# ══════════════════════════════════════════════════════════════════════
#  Q4 — le bilan est la seule sortie de séance
# ══════════════════════════════════════════════════════════════════════


def test_only_the_review_surface_closes_the_session():
    detail = _uncommented(DETAIL.read_text(encoding="utf-8"))
    card = _uncommented(CARD.read_text(encoding="utf-8"))
    assert 'name="action" value="end"' in detail
    assert 'value="end"' not in card, (
        "la console ne doit pas pouvoir terminer la séance directement"
    )
    assert "TERMINER LA SÉANCE" in detail


def test_the_review_surface_can_receive_focus():
    """Une ancre qui ne déplace que le défilement laisse le clavier derrière
    elle."""
    detail = _uncommented(DETAIL.read_text(encoding="utf-8"))
    form = detail[detail.find('id="session-feedback"') - 300:]
    assert 'tabindex="-1"' in form[:600]


def test_no_new_feedback_field_was_added():
    """« Do not add new feedback fields » — opérateur, 2026-08-19."""
    detail = DETAIL.read_text(encoding="utf-8")
    names = set(re.findall(r'name="([a-z_]+)"', detail))
    known = {
        "cardio_duration_min", "cardio_bpm_avg", "cardio_machine_type",
        "cardio_machine_calories", "concentration", "global_state",
        "bodyweight_kg", "free_note", "action",
    }
    assert names <= known, names - known


# ══════════════════════════════════════════════════════════════════════
#  Palette — une seule autorité, celle de `:root`
# ══════════════════════════════════════════════════════════════════════


def test_the_console_consumes_the_cockpit_palette():
    """C'est ce que `UIV3_COCKPIT_LADDER_01` a rendu possible : avant B0, les
    `--t-*` vivaient sous `.today-home` et cette feuille en comptait zéro."""
    css = CSS.read_text(encoding="utf-8")
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)
    for token in ("--t-amber", "--t-fg", "--t-raised", "--t-line-strong"):
        assert f"var({token})" in css, token


def test_the_console_declares_no_palette_token_of_its_own():
    """Une seconde autorité ferait diverger la Séance de l'Accueil sans
    qu'aucun autre test ne bronche."""
    css = re.sub(r"/\*.*?\*/", "", CSS.read_text(encoding="utf-8"), flags=re.DOTALL)
    redeclared = re.findall(r"(--t-[\w-]+)\s*:", css)
    assert redeclared == [], redeclared


def test_the_dominant_command_has_a_pressed_state():
    """`00A §5` — sans `:active`, la latence SSR fait retaper l'utilisateur,
    qui soumet deux fois."""
    css = re.sub(r"/\*.*?\*/", "", CSS.read_text(encoding="utf-8"), flags=re.DOTALL)
    assert re.search(r"\.dock__cmd:active\s*\{", css)


# ══════════════════════════════════════════════════════════════════════
#  `Web:S7930` — la preuve que l'analyseur se trompe SUR CE FICHIER
# ══════════════════════════════════════════════════════════════════════


def _rendered_ids(body: str) -> list[str]:
    return re.findall(r'id="(set-\d+)"', body)


def test_set_anchors_are_unique_in_every_rendered_state(client):
    """Aucun identifiant d'ancre dupliqué, à AUCUN état, au RENDU.

    `Web:S7930` signale quatre identifiants dupliqués dans
    `exercise_card.html`. L'analyseur lit un gabarit Jinja comme un document
    HTML statique : il voit le littéral `id="set-{{ sl.id }}"` écrit dans
    plusieurs macros et conclut à une duplication. Il ne peut pas savoir que
    ces macros sont MUTUELLEMENT EXCLUSIVES — une série est passée, ou
    courante, ou future, jamais deux à la fois.

    Cette garde est la preuve que la sortie réelle est saine. Elle n'a pas
    été écrite pour faire taire l'analyseur : sa première exécution aurait
    ÉCHOUÉ, parce qu'à l'état `CORRECTION` une série déjà validée sortait
    bien deux fois — c'est le vrai défaut que `S7930` a permis de trouver et
    que `future_sets=list(pending_works)` corrige.
    """
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog

    r = client.post("/sessions", data={"template_slug": "push-a"},
                    follow_redirects=False)
    sid = int(re.match(r"/sessions/(\d+)", r.headers["location"]).group(1))

    with SessionLocal() as db:
        se = db.execute(
            select(SessionExercise)
            .where(SessionExercise.session_id == sid)
            .order_by(SessionExercise.position.asc()).limit(1)
        ).scalar_one()
        se_id = se.id
        work = db.execute(
            select(SetLog).where(SetLog.session_exercise_id == se_id)
            .where(SetLog.kind == "work").order_by(SetLog.set_index.asc())
        ).scalars().all()
        # DEUX séries validées — la configuration exacte que le défaut
        # exigeait, et qu'aucune garde ne couvrait.
        for sl in work[:2]:
            sl.completed, sl.weight_kg, sl.reps = True, 60.0, 10
        for sl in db.execute(
            select(SetLog).where(SetLog.session_exercise_id == se_id)
            .where(SetLog.kind == "warmup")
        ).scalars().all():
            sl.completed, sl.weight_kg, sl.reps = True, 40.0, 12
        db.commit()
        first_done = work[0].id

    for label, url in (
        ("current_set", f"/sessions/{sid}?active={se_id}"),
        ("rest", f"/sessions/{sid}?active={se_id}&rest=1"),
        ("correction", f"/sessions/{sid}?active={se_id}&fix={first_done}"),
    ):
        ids = _rendered_ids(client.get(url).text)
        duplicates = {i for i in ids if ids.count(i) > 1}
        assert duplicates == set(), f"{label} : ancres dupliquées {duplicates}"
        assert ids, f"{label} : aucune ancre rendue — la garde ne garderait rien"
