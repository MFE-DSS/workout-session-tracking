"""`UX4_03B` — rendre perceptible sans rendre plus qu'on ne sait.

CE QUE CES GARDES PROTÈGENT
----------------------------
`UX4_03` a rendu trois signaux réels sur une surface correcte, et les a rendus
**faux** : chacun habillait une donnée absente en mesure. L'audit `UX4_03A` l'a
mesuré, et le dépôt avait déjà écrit la règle dans `recovery_contract` —
« "the user told us nothing" is not a measurement and must not be dressed up as
a neutral reading ».

Les gardes ci-dessous ne protègent donc pas « trois signaux sont visibles »
(c'était l'invariant d'`UX4_03`, et il était satisfait par un rendu refusé).
Elles protègent : **rien à l'écran ne prétend savoir plus que le calcul.**

LES TROIS DÉFAUTS REPLANTÉS
----------------------------
1. `compute_session_fatigue(None, None)` → **45,0**, affiché « 45/100 »
2. `compute_consistency(3)` → **21,4**, affiché « 21/100 » pour un rythme sain
3. `compute_trend(0, 0)` → **« stable »**, affiché à qui n'a jamais rien fait
"""
from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "app/templates/progress.html"
SESSION_TEMPLATE = ROOT / "app/templates/session_detail.html"


def _uncommented(src: str) -> str:
    """Sans les commentaires Jinja.

    Ce gabarit EXPLIQUE les défauts qu'il ferme, donc il cite « 45/100 »,
    « stable » et `fatigue_score` dans sa propre justification. Une garde qui
    lit la prose rougirait sur l'explication du choix — le motif s'est présenté
    **six fois** dans ce dépôt.
    """
    return re.sub(r"\{#.*?#\}", " ", src, flags=re.S)


def _state(**kw):
    """Des `ProgressFacts`, surchargés champ par champ.

    Tous les défauts valent « rien de déclaré, rien d'enregistré » : un test qui
    ne surcharge rien décrit donc l'état INCONNU, celui où le premier rendu
    fabriquait ses valeurs.
    """
    from app.services.progress_facts import ProgressFacts

    return ProgressFacts(**kw)


def _facts_days(*, done=(), cardio=(), active=None, first_known=0):
    """Des `ProgressFacts` dont seules les 14 traces comptent."""
    from app.services.progress_facts import DayTrace, ProgressFacts

    days = []
    for i in range(14):
        if i < first_known:
            state, kind, name = "none", None, None
        elif i == active:
            state, kind, name = "active", None, None
        elif i in done:
            state = "done"
            kind = "cardio" if i in cardio else "strength"
            name = "Push A"
        else:
            state, kind, name = "rest", None, None
        days.append(DayTrace(offset=i, label=f"{8 + i:02d}/08",
                             state=state, kind=kind, name=name))
    return ProgressFacts(days=tuple(days))


# ───────── les trois défauts mesurés d'`UX4_03A`, chacun fermé ─────────


def test_an_undeclared_feeling_reads_as_unknown_not_as_forty_five():
    """**Défaut 1.** `compute_session_fatigue(None, None)` rend 45,0 — le
    milieu de l'échelle. `UX4_03` l'affichait « 45/100 », donc une absence de
    réponse se lisait comme une charge moyenne mesurée."""
    from app.services.behavioral import compute_session_fatigue
    from app.services.progress_signals import build_progress_signals

    # Le défaut est réel, pas supposé.
    assert compute_session_fatigue(global_state=None, concentration=None) == 45.0

    load = build_progress_signals(_state(declared_state=None))[0]
    assert load["known"] is False
    assert load["value"] == "inconnu"
    assert load["context"] == "aucun ressenti déclaré"
    assert "45" not in load["value"]


def test_a_healthy_rhythm_is_not_rendered_as_a_failing_grade():
    """**Défaut 2.** `min(100, n / 14 × 100)` pose une séance par jour comme le
    100 %. Trois séances en quatorze jours — un rythme sain — s'affichaient
    « 21/100 »."""
    from app.services.behavioral import compute_consistency
    from app.services.progress_signals import build_progress_signals

    assert round(compute_consistency(3), 1) == 21.4

    sessions = build_progress_signals(_state(sessions_14d=3))[1]
    assert sessions["value"] == "3"
    assert "/100" not in sessions["value"]
    assert "21" not in sessions["value"]


def test_never_having_trained_is_not_a_stable_rhythm():
    """**Défaut 3 — le plus grave.** `compute_trend(0, 0)` rendait `"stable"`,
    donc l'ancien gabarit annonçait « Continuité stable » à quelqu'un qui
    n'avait jamais enregistré une séance.

    **Migrée.** La garde plantait le défaut en appelant le producteur.
    `UX4_03B` l'a **supprimé** (`OPERATOR_DECISION` D6) : le défaut n'existe
    plus à la source, donc on ne peut plus l'invoquer. Ce qui reste vrai, et
    que cette garde tient désormais, c'est l'invariant de surface : deux
    fenêtres vides ne se lisent jamais comme une stabilité.
    """
    import app.services.behavioral as behavioral
    from app.services.progress_signals import build_progress_rail

    assert not hasattr(behavioral, "compute_trend"), (
        "le producteur du défaut est revenu"
    )

    # `UX4_03D` — MIGRÉE UNE SECONDE FOIS. L'objet « Cadence » est absorbé par
    # le rail (`OPERATOR_DECISION` 2), donc il n'y a plus de valeur à lire.
    # L'invariant qui survit : quatorze jours sans séance ne produisent aucune
    # trace pleine, et donc aucune apparence de rythme.
    cells = build_progress_rail(_facts_days(done=()))
    assert len(cells) == 14
    assert all("--on" not in c["cls"] for c in cells)
    assert all("repos" in c["title"] for c in cells)


def test_the_rail_carries_the_comparison_the_cadence_used_to_state():
    """L'inverse : quand il y a un rythme, le rail le porte.

    La cadence rendait « 4 → 1 ». Le rail rend les quatorze jours : quatre
    traces à gauche, une à droite. C'est la même comparaison, montrée au lieu
    d'être chiffrée — et c'est ce qui autorise le retrait (`§5.3`).
    """
    from app.services.progress_signals import build_progress_rail

    cells = build_progress_rail(_facts_days(done=(0, 2, 4, 6, 12)))
    left = sum(1 for c in cells[:7] if "--on" in c["cls"])
    right = sum(1 for c in cells[7:] if "--on" in c["cls"])
    assert (left, right) == (4, 1)


def test_the_cadence_object_is_gone_from_the_first_level():
    """Garde structurelle du retrait : deux signaux, plus trois."""
    from app.services.progress_signals import build_progress_signals

    rows = build_progress_signals(_state(sessions_last_7=1, sessions_prev_7=4))
    assert [r["name"] for r in rows] == ["Ressenti général", "Séances"]


# ───────── le gabarit ne peut plus lire ce qui a été écarté ─────────


def test_the_template_cannot_read_the_rejected_scores():
    """**Garde structurelle — la plus importante du lot.**

    Corriger les libellés laisserait les trois champs à portée du gabarit, et
    un futur `{{ behavioral.fatigue_score }}` les ramènerait sans qu'aucune
    garde de vocabulaire ne bronche. Le routeur ne passe plus l'état brut :
    la correction est structurelle.
    """
    src = _uncommented(TEMPLATE.read_text(encoding="utf-8"))
    for rejected in ("fatigue_score", "consistency_score", "trend_direction",
                     "behavioral."):
        assert rejected not in src, f"le gabarit relit un champ écarté : {rejected}"


def test_the_router_passes_the_view_model_not_the_raw_state():
    """Le pendant du précédent, côté routeur."""
    router = (ROOT / "app/routers/pages.py").read_text(encoding="utf-8")
    handler = router.split("def progress(", 1)[1].split("\n@router.", 1)[0]
    code = re.sub(r"#.*", " ", handler)
    assert "build_progress_signals(" in code
    assert '"behavioral"' not in code, "l'état brut repart vers le gabarit"


def test_no_new_business_calculation_was_added():
    """Le brief interdit tout calcul nouveau. `progress_signals` traduit un
    état déjà produit : aucune requête, aucune horloge, aucun seuil.

    ⚠ La première version de cette garde cherchait la sous-chaîne `"session"`
    et rougissait sur `_sessions` — **septième occurrence** dans ce dépôt d'une
    garde qui traque un fragment plutôt qu'un nom. On vise donc ce qu'un calcul
    EXIGE structurellement : un accès base, une horloge, ou de l'arithmétique.
    """
    import ast

    tree = ast.parse(
        (ROOT / "app/services/progress_signals.py").read_text(encoding="utf-8")
    )

    imported = {
        node.module or ""
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    } | {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    for forbidden in ("sqlalchemy", "app.models", "datetime"):
        assert not any(m.startswith(forbidden) for m in imported), (
            f"la vue-modèle importe de quoi calculer : {forbidden}"
        )

    # Aucune arithmétique : une traduction compare et met en forme, elle ne
    # divise pas. `compute_consistency` divisait par 14, et c'est précisément
    # le geste que cette tranche retire de la surface.
    arithmetic = [
        n for n in ast.walk(tree)
        if isinstance(n, ast.BinOp)
        and isinstance(n.op, (ast.Div, ast.Mult, ast.Sub, ast.Add))
    ]
    assert not arithmetic, "la vue-modèle fait de l'arithmétique"


# ───────── aucun agrégat, aucune barre proportionnelle ─────────


def test_no_score_out_of_one_hundred_survives_anywhere(client):
    """`FatigueSignal` refuse explicitement l'agrégat : « there is deliberately
    no aggregate ». Un `/100` sur cette surface est ce scalaire."""
    section = _signals_section(client)
    assert "/100" not in section


def test_no_proportional_bar_survives(client):
    """L'Accueil a déjà tranché pour la même classe de signal
    (`Sx_UIV3_01`) : « une barre proportionnelle serait une affirmation de
    pourcentage physiologique ». `UX4_03` en affichait trois, dont la largeur
    ÉTAIT le score."""
    section = _signals_section(client)
    for banned in ("signal__gauge", "signal__fill", "style=\"width:"):
        assert banned not in section, f"jauge proportionnelle rendue : {banned}"


def test_the_disclosure_control_is_not_sized_below_the_product_standard():
    """La divulgation est le SEUL contrôle tactile que cette tranche ajoute.

    Le standard produit AUREN est **44 px** (SC 2.5.5 AAA + Apple HIG) — pas le
    seuil WCAG 2.2 AA de 24 px, que `--space-xs` franchissait déjà. Mesuré au
    navigateur avec `--space-xs` : **26 px**. Conforme AA, sous le standard.

    ⚠ Cette garde est un PROXY, et le dire est plus utile que de la présenter
    comme une preuve : elle lit un token, pas une hauteur rendue. La preuve est
    la mesure au navigateur consignée dans le rapport de sprint. `Progress` est
    `TRANSITIONAL`, donc sans gate pixel en CI — il n'existe pas de garde
    mécanique capable de mesurer ce pixel ici.
    """
    css = (ROOT / "app/static/css/app.css").read_text(encoding="utf-8")
    rule = css.split(".signals__how > summary {", 1)[1].split("}", 1)[0]
    assert "var(--space-xs)" not in rule, (
        "le rembourrage retombe à la valeur mesurée à 26 px"
    )
    assert "var(--space-md)" in rule


def test_the_gauge_styles_are_gone_from_the_sheet():
    """Retirer le balisage en laissant les règles CSS ferait revenir la jauge
    au premier gabarit qui réutilise la classe."""
    css = (ROOT / "app/static/css/app.css").read_text(encoding="utf-8")
    code = re.sub(r"/\*.*?\*/", " ", css, flags=re.S)
    for dead in (".signal__gauge", ".signal__fill", ".signal__unit"):
        assert dead not in code, f"règle de jauge encore vivante : {dead}"


# ───────── les libellés sont cités, pas réécrits ─────────


def test_the_declared_labels_match_the_form_the_user_answered():
    """**Garde anti-dérive.** AUREN cite le mot que l'utilisateur a choisi. Si
    le formulaire de fin de séance dit « Moyen » et que Progression affiche
    « modéré », la surface paraphrase une réponse au lieu de la rapporter.

    La table du formulaire est lue DANS le gabarit : les deux ne peuvent pas
    diverger sans que cette garde rougisse.
    """
    from app.services.progress_signals import DECLARED_STATE_LABELS

    src = SESSION_TEMPLATE.read_text(encoding="utf-8")
    for code, label in DECLARED_STATE_LABELS.items():
        assert f'("{code}", "{label}")' in src, (
            f"« {label} » ne correspond plus au formulaire pour « {code} »"
        )


def test_every_declared_state_is_covered():
    """Un état de l'énumération sans libellé retomberait silencieusement sur
    « inconnue » — une déclaration réelle effacée par un trou de table."""
    from app.enums import SessionGlobalState
    from app.services.progress_signals import DECLARED_STATE_LABELS

    assert {s.value for s in SessionGlobalState} == set(DECLARED_STATE_LABELS)


def test_a_declared_feeling_is_quoted_verbatim():
    from app.services.progress_signals import build_progress_signals

    load = build_progress_signals(
        _state(declared_state="fatigued", declared_is_latest=True))[0]
    assert load["value"] == "Fatigué"
    assert load["known"] is True


# ───────── le signal dit ce que la question posait, et quand ─────────


def test_the_subjective_signal_is_not_named_after_perceived_exertion():
    """**Correction opérateur.** Le formulaire demande « Énergie générale —
    Comment te sentais-tu pendant la séance ? ». C'est une question sur le
    RESSENTI.

    « Charge perçue » est le vocabulaire du RPE, une échelle d'effort perçu que
    ce dépôt ne collecte nulle part. L'employer ferait passer une question
    d'humeur pour une mesure d'intensité — et rendrait le terme indisponible le
    jour où AUREN mesurera réellement l'effort perçu.
    """
    from app.services.progress_signals import SUBJECTIVE_LABEL

    assert SUBJECTIVE_LABEL == "Ressenti général"
    for rpe in ("charge perçue", "rpe", "effort perçu", "intensité perçue"):
        assert rpe not in SUBJECTIVE_LABEL.lower()


def test_the_source_question_is_really_about_feeling():
    """La garde précédente vaut ce que vaut sa prémisse. On lit le formulaire
    plutôt que de la croire sur parole : si la question devient un jour une
    question d'effort, c'est ici que ça doit rougir."""
    src = SESSION_TEMPLATE.read_text(encoding="utf-8")
    assert "Comment te sentais-tu pendant la séance" in src
    assert "global_state" in src


def test_an_older_declaration_carries_its_date():
    """**La fraîcheur ne se fabrique pas.**

    Remonter à la dernière déclaration réelle est accepté. La rendre comme si
    elle datait de la dernière séance ne l'est pas : ce serait le défaut du
    45,0 déplacé du contenu vers le temps.
    """
    from datetime import UTC, datetime

    from app.services.progress_signals import build_progress_signals

    old = datetime(2026, 8, 12, 18, 30, tzinfo=UTC)
    row = build_progress_signals(
        _state(declared_state="flat", declared_at=old, declared_is_latest=False)
    )[0]
    assert row["value"] == "Moyen"
    assert row["context"] == "dernière déclaration · 12/08"


def test_the_most_recent_declaration_is_not_dated():
    """L'inverse : dater ce qui vient de la dernière séance ajouterait du bruit
    sans rien apprendre. La date signale un ÉCART, pas une provenance."""
    from datetime import UTC, datetime

    from app.services.progress_signals import build_progress_signals

    row = build_progress_signals(_state(
        declared_state="good",
        declared_at=datetime(2026, 8, 20, 9, 0, tzinfo=UTC),
        declared_is_latest=True,
    ))[0]
    assert row["context"] == "déclaré en fin de séance"
    assert "/" not in row["context"]


def test_the_unknown_value_agrees_with_the_signal_name():
    """« Ressenti » est masculin. L'ancien « inconnue » s'accordait avec
    « Charge » — un accord orphelin après le renommage se lit comme une faute,
    pas comme un état."""
    from app.services.progress_signals import UNKNOWN_VALUE

    assert UNKNOWN_VALUE == "inconnu"


def test_the_producer_reports_whether_the_declaration_is_the_latest():
    """Garde structurelle : sans ces deux champs, la surface ne PEUT pas
    distinguer une déclaration fraîche d'une déclaration ancienne, et le
    libellé daté serait invérifiable."""
    import dataclasses

    from app.services.progress_facts import ProgressFacts

    fields = {f.name for f in dataclasses.fields(ProgressFacts)}
    assert {"declared_at", "declared_is_latest"} <= fields


def test_the_facts_are_counted_against_a_real_database(client):
    """**La garde que le TypeError m'a apprise.**

    La première version de `progress_facts` chargeait les dates de la fenêtre
    et dérivait la demi-fenêtre en Python — une requête au lieu de deux. Elle
    plantait : SQLite rend des datetimes **naïfs** même pour une colonne
    déclarée `DateTime(timezone=True)`, et `naïf >= aware` lève.

    Aucun test de la vue-modèle ne pouvait le voir : ils construisent des
    `ProgressFacts` à la main et ne touchent jamais la base. Seul un test qui
    COMPTE RÉELLEMENT ferme ce trou — et il vérifie les valeurs, pas seulement
    l'absence d'exception, sinon il ne garderait que contre le crash.
    """
    from datetime import UTC, datetime, timedelta

    from app.database import SessionLocal
    from app.models.session import WorkoutSession
    from app.services.progress_facts import build_progress_facts
    from tests.helpers import get_test_user_id

    now = datetime(2026, 8, 21, 12, 0, tzinfo=UTC)
    uid = get_test_user_id()
    # 3 séances dans les 7 derniers jours, 2 dans les 7 précédents,
    # 1 hors fenêtre, et 1 exclue des stats qui ne doit RIEN compter.
    plan = [(1, False), (3, False), (5, False), (9, False), (12, False),
            (30, False), (2, True)]
    with SessionLocal() as db:
        for days, excluded in plan:
            db.add(WorkoutSession(
                user_id=uid, template_slug_snapshot="push-a",
                template_name_snapshot="Push A", status="completed",
                excluded_from_stats=excluded,
                global_state="flat" if days == 3 else None,
                started_at=now - timedelta(days=days),
            ))
        db.commit()
        facts = build_progress_facts(db, uid, now=now)

    assert facts.sessions_14d == 5
    assert facts.sessions_last_7 == 3
    assert facts.sessions_prev_7 == 2
    # La plus récente (1 j) ne porte pas de déclaration : on remonte à 3 j.
    assert facts.declared_state == "flat"
    assert facts.declared_is_latest is False


def test_the_surface_does_not_grow_a_frozen_decision_engine():
    """**La garde que le full sweep m'a apprise.**

    La première version de cette tranche ajoutait cinq champs à
    `BehavioralState`. C'était tentant — le moteur calcule déjà ces valeurs puis
    les jette. `test_no_decision_engine_was_touched` a rougi, et elle avait
    raison : depuis `e8614bd`, trois moteurs sont gelés au nom de « la
    présentation ne décide de rien », et faire grossir un moteur gelé pour
    servir une surface inverse la dépendance que ce gel protège.

    L'argument « ce n'est qu'additif » est exactement celui que la garde existe
    pour refuser : un champ additif aujourd'hui est une lecture couplée demain.

    Celle-ci est le pendant local : elle échoue si la surface Progression se
    remet à dépendre du moteur, sans attendre le sweep complet.
    """
    for module in ("app/services/progress_facts.py",
                   "app/services/progress_signals.py"):
        src = (ROOT / module).read_text(encoding="utf-8")
        code = re.sub(r'""".*?"""', " ", src, flags=re.S)
        code = re.sub(r"#.*", " ", code)
        assert "behavioral" not in code, (
            f"{module} dépend d'un moteur de décision gelé"
        )

    router = (ROOT / "app/routers/pages.py").read_text(encoding="utf-8")
    handler = router.split("def progress(", 1)[1].split("\n@router.", 1)[0]
    assert "compute_behavioral_state" not in re.sub(r"#.*", " ", handler)


# ───────── densité : une divulgation partagée, pas trois notes ─────────


def test_one_shared_disclosure_replaces_the_three_notes(client):
    """Le verdict opérateur interdit les ~77 mots supplémentaires d'`UX4_03`.
    Trois notes disaient trois fois la même chose : d'où vient le chiffre."""
    section = _signals_section(client)
    assert section.count("signals__how") >= 1
    assert "Comment AUREN calcule ces signaux" in section
    assert "signal__note" not in section, "les notes par signal sont revenues"


def test_the_disclosure_costs_one_line_when_closed(client):
    """Repliée par défaut : une divulgation ouverte serait les 77 mots, dans un
    autre emballage."""
    section = _signals_section(client)
    disclosure = section[section.index("signals__how"):]
    assert "<details" in section
    assert "open" not in disclosure[:disclosure.index(">")], (
        "la divulgation est dépliée par défaut"
    )


# ───────── invariants conservés d'`UX4_03` ─────────


def test_the_signals_live_on_progression_not_on_the_profile(client):
    """`UX4_01` les a retirés du Profil pour une raison."""
    profile = client.get("/profile").text
    for signal in ("Ressenti général", "Cadence 7 j"):
        assert signal not in profile, f"{signal} est revenu sur le Profil"


def test_the_daily_streak_is_never_rendered(client):
    """`OPERATOR_DECISION / DO_NOT_SURFACE`.

    On traque un streak PRÉSENTÉ — un libellé de compteur, un mot-valise, une
    flamme — pas le vocabulaire : la divulgation écrit « aucune série de jours
    n'est comptée », et bannir le terme ferait rougir la phrase qui énonce la
    décision.
    """
    body = client.get("/progress").text.lower()
    for banned in ("jours de série", "série en cours", "streak", "🔥"):
        assert banned not in body, f"streak quotidien rendu : « {banned} »"


def test_the_template_never_reads_streak_days():
    assert "streak_days" not in _uncommented(TEMPLATE.read_text(encoding="utf-8"))


def test_streak_days_is_still_computed():
    """Ne pas rendre n'est pas supprimer."""
    import dataclasses

    from app.services.behavioral import BehavioralState

    fields = {f.name for f in dataclasses.fields(BehavioralState)}
    assert "streak_days" in fields


def test_no_medical_wording_anywhere_on_the_surface(client):
    """« Charge perçue » décrit ce que l'utilisateur a DÉCLARÉ. Aucun terme n'a
    le droit de suggérer un état physiologique mesuré."""
    body = client.get("/progress").text.lower()
    for banned in ("diagnostic", "patholog", "symptôme", "surentraînement",
                   "syndrome", "prescription médicale"):
        assert banned not in body, f"vocabulaire médical rendu : « {banned} »"


def test_no_fake_ai_score_is_claimed(client):
    body = client.get("/progress").text.lower()
    for banned in ("score ia", "intelligence artificielle", "algorithme prédit",
                   "prédiction"):
        assert banned not in body, f"revendication non fondée : « {banned} »"


def test_the_surface_needs_no_javascript(client):
    """`<details>` est natif : le dépliant ne coûte pas une ligne de script."""
    section = _signals_section(client)
    for js in ("<script", "onclick", "data-chart", "hx-get"):
        assert js not in section, f"dépendance JS introduite : {js}"


def test_no_body_map_or_anatomical_asset_was_added():
    """⚠ `plate` seul matchait `template_kpis`. Un fragment n'est pas un nom."""
    src = TEMPLATE.read_text(encoding="utf-8").lower()
    for banned in ("bodymap", "body-map", "regional_plate", "muscle_focus",
                   "svg/anat"):
        assert banned not in src, f"asset anatomique introduit : {banned}"


def test_the_page_promises_only_what_it_shows(client):
    """Le chapeau annonçait « la régularité », un mot auquel plus aucun libellé
    ne répond. Une promesse invisible déplacée d'un cran resterait une promesse
    invisible — c'est exactement ce qu'`UX4_03` devait fermer."""
    body = client.get("/progress").text
    lede = body[body.index('class="lede"'):][:220]
    assert "régularité" not in lede.lower()


# ───────── outillage ─────────


def _with_traces(client, uid: int = 1):
    """Donne au compte du harnais de quoi instrumenter.

    `TRAIN1-A` / A4 — POURQUOI CE HELPER EXISTE MAINTENANT.
    Le `conftest` crée un utilisateur **sans aucune séance**, et `/progress`
    rend depuis cette tranche un état COMPACT quand la fenêtre ne porte aucune
    trace : une ligne « Aucune séance · 14 j », ni signaux ni rail. Les gardes
    ci-dessous éprouvent l'INSTRUMENT ; elles doivent donc le faire exister.

    Ce n'est pas un affaiblissement : leur invariant — « rien à l'écran ne
    prétend savoir plus que le calcul » — est inchangé, et il porte désormais
    sur l'état où l'instrument se rend vraiment.
    """
    from datetime import UTC, datetime, timedelta

    from app.database import SessionLocal
    from app.models.session import WorkoutSession
    from app.models.user import User

    now = datetime.now(UTC)
    with SessionLocal() as db:
        u = db.get(User, uid)
        # Un compte créé à l'instant rend légitimement quatorze jours « hors
        # historique » depuis cette tranche.
        u.created_at = now - timedelta(days=90)
        db.add(WorkoutSession(
            user_id=uid, template_slug_snapshot="s",
            template_name_snapshot="Push A",
            started_at=now - timedelta(days=2), status="completed",
            excluded_from_stats=False, global_state="good",
        ))
        db.commit()
    return client


def _signals_section(client) -> str:
    """La section des signaux seule — le reste de Progression contient des
    jauges et des pourcentages légitimes qui ne relèvent pas de cette tranche.
    """
    body = _with_traces(client).get("/progress").text
    start = body.index('class="signals"')
    return body[start:body.index("Rythme récent")]


# ── `UX4_03D` — les décisions d'architecture d'information ───────────────────


def test_the_two_weekly_counters_cannot_disagree_again(client):
    """**Le défaut principal de l'audit, refermé.**

    `weekly_loop` affichait « 2 séances cette semaine » et le KPI
    « 3 sessions cette semaine » — MÊME fenêtre ISO, les deux appellent
    `_start_of_iso_week`. La seule différence était le filtre : le KPI comptait
    tous les statuts, séances exclues comprises. Rien à l'écran ne permettait
    de le deviner.

    `PROGRESSION_SESSION_COUNT = COMPLETED_STAT_ELIGIBLE` : sur Progression, une
    séance compte si et seulement si elle est terminée et non exclue.

    ⚠ La première écriture inspectait la fonction ENTIÈRE. Elle est restée
    verte quand j'ai retiré le filtre, parce que `status == "completed"`
    apparaît ailleurs dans le même corps, pour d'autres requêtes. Une garde qui
    cherche une chaîne dans un bloc trop large ne garde rien. On découpe donc
    autour de l'affectation visée.
    """
    import inspect

    from app.services import kpis as kpis_mod
    from app.services import weekly_loop as wl_mod

    src = inspect.getsource(kpis_mod.compute_global_kpis)
    query = src.split("sessions_this_week = ", 1)[1].split(").scalar_one()", 1)[0]
    assert 'status == "completed"' in query, (
        "le compteur hebdomadaire de Progression ne filtre plus sur les "
        "séances terminées"
    )
    assert "excluded_from_stats" in query, (
        "le compteur hebdomadaire de Progression ne filtre plus les séances "
        "exclues des statistiques"
    )

    wl = inspect.getsource(wl_mod._load_window_sessions)
    assert 'status == "completed"' in wl, (
        "weekly_loop ne filtre plus sur les séances terminées — les deux "
        "compteurs peuvent diverger de nouveau"
    )
    assert "excluded_from_stats" in wl, (
        "weekly_loop ne filtre plus les séances exclues — les deux compteurs "
        "peuvent diverger de nouveau"
    )


def test_the_weekly_counter_ignores_an_open_session(client):
    """La garde précédente lit du code ; celle-ci COMPTE.

    Une séance ouverte aujourd'hui faisait diverger les deux blocs. On la pose
    et on vérifie que le compteur ne bouge pas.
    """
    from datetime import UTC, datetime

    from app.database import SessionLocal
    from app.models.session import WorkoutSession
    from app.services.kpis import compute_global_kpis
    from tests.helpers import get_test_user_id

    uid = get_test_user_id()
    now = datetime.now(UTC)
    with SessionLocal() as db:
        before = compute_global_kpis(db, user_id=uid).sessions_this_week
        db.add(WorkoutSession(
            user_id=uid, template_slug_snapshot="push-a",
            template_name_snapshot="Push A", started_at=now,
            status="in_progress", excluded_from_stats=False))
        db.commit()
        after = compute_global_kpis(db, user_id=uid).sessions_this_week

    assert after == before, (
        "une séance ouverte compte de nouveau dans le KPI hebdomadaire — la "
        "contradiction avec weekly_loop est revenue"
    )


def test_no_behavioural_verdict_prose_at_the_first_level(client):
    """`OPERATOR_DECISION` 4 — les verdicts en prose quittent le L1.

    « Semaine régulière — garde ce rythme » et « Continue sur cette base »
    trônaient au-dessus de tous les objets de la page.
    """
    body = client.get("/progress").text
    for verdict in ("garde ce rythme", "Continue sur cette base",
                    "Hint de la semaine"):
        assert verdict not in body, f"verdict en prose rendu : « {verdict} »"


def test_the_unique_weekly_objects_survive():
    """Le pendant : `weekly_loop` est RECOMPOSÉ, pas supprimé (`§5.3`).
    Dominantes et anomalie sont des objets réels et restent.

    ⚠ `TRAIN1-C` — CETTE GARDE LISAIT UN GABARIT QUE PLUS RIEN NE RENDAIT.
    Elle vérifiait la survie des deux faits dans `_partials/weekly_loop.html`,
    orphelin depuis que `TRAIN1-A` a retiré son `include`. Elle était donc
    verte quoi qu'il arrive à la vraie page — la treizième garde de cette
    famille. Le partiel est supprimé ; elle lit désormais la SURFACE, là où
    les deux faits ont réellement atterri.
    """
    body = _uncommented(TEMPLATE.read_text(encoding="utf-8"))
    # la dominance hebdomadaire, absorbée dans « Par programme »
    assert "tk.week_count" in body
    assert "cette sem." in body
    # l'anomalie, absorbée en ligne de l'instrument temporel
    assert "top_anomaly" in body


def test_coexisting_counts_of_the_same_entity_state_their_window():
    """`OPERATOR_DECISION` 3 — « Push A · 2× » et « Push A · 5 sessions »
    comptaient le même programme sur deux fenêtres muettes.

    ⚠ La première écriture lisait la PAGE RENDUE, donc elle passait au vert
    quand la fixture n'avait ni programme dominant ni KPI par programme —
    une garde qui ne garde que si les données veulent bien exister. On lit les
    gabarits : la fenêtre doit être écrite à côté du nombre, données ou pas.

    ⚠ `TRAIN1-C` — sa moitié « dominantes » lisait elle aussi le partiel
    orphelin `weekly_loop.html`. Les DEUX comptes vivent maintenant dans la
    même entrée « Par programme » : c'est cette entrée, et elle seule, qui doit
    porter les deux fenêtres.
    """
    prog = _uncommented(TEMPLATE.read_text(encoding="utf-8"))
    entry = prog.split('class="template-kpi"', 1)[1].split("</li>", 1)[0]

    # fenêtre 1 — la semaine ISO en cours, collée au compte hebdomadaire
    assert "cette sem." in entry, (
        "les dominantes ne disent plus sur quelle fenêtre elles comptent"
    )
    # fenêtre 2 — tout l'historique. Sur la ligne de métadonnées et non collée
    # au nombre : inline, à 390 px, elle repliait la ligne.
    assert "historique" in entry, (
        "le compte par programme ne dit plus sur quelle fenêtre il porte"
    )


def test_the_session_type_is_encoded_by_texture_not_by_colour():
    """`OPERATOR_DECISION` 5 — musculation et cardio sont deux actions
    utilisateur. Leur donner deux couleurs inventerait une hiérarchie que le
    socle ne porte pas, où l'ambre signifie « action / actuel »."""
    import pathlib

    css = (pathlib.Path(__file__).resolve().parent.parent
           / "app/static/css/app.css").read_text(encoding="utf-8")
    block = css.split(".rail__c--cardio {", 1)[1].split("}", 1)[0]
    assert "repeating-linear-gradient" in block, "la texture a disparu"
    for hue in ("--accent", "--danger", "--warn", "--good", "#"):
        assert hue not in block, f"le type de séance est codé par la couleur : {hue}"


def test_an_unknown_session_type_is_not_guessed():
    """`quality_score.session_kind` retombe sur « strength » quand le template
    a été supprimé — un repli sûr pour un SCORE, un mensonge pour un affichage.
    Une trace de type inconnu ne reçoit aucune texture."""
    from app.services.progress_facts import DayTrace, ProgressFacts
    from app.services.progress_signals import build_progress_rail

    facts = ProgressFacts(days=(DayTrace(
        offset=0, label="08/08", state="done", kind=None, name="Push A"),))
    assert "--cardio" not in build_progress_rail(facts)[0]["cls"]


def test_the_rail_is_one_object_not_fourteen_targets(client):
    """À 390 px une trace fait ~25 px. La rendre tactile passerait l'exception
    d'espacement WCAG 2.2 AA et violerait QUATORZE FOIS le standard produit
    AUREN de 44 px. Un instrument neuf ne se bâtit pas sur des dérogations."""
    body = _with_traces(client).get("/progress").text
    # `TRAIN1-A` / A5 — le rail s'ouvre désormais, mais l'invariant tient : la
    # cible est le `<summary>` pleine largeur, jamais les quatorze traces. On
    # borne donc la lecture au `<div class="rail">` lui-même, pas au bloc
    # jusqu'à l'axe — qui contient maintenant le niveau 2, et ses liens
    # LÉGITIMES vers les séances.
    start = body.index('<div class="rail"')
    section = body[start:body.index("</div>", start)]
    for interactive in ("<a ", "<button", "onclick", "tabindex"):
        assert interactive not in section, (
            f"les traces du rail sont devenues des cibles : {interactive}"
        )


# ── `UX4_03D` — le rail masqué DOIT avoir son équivalent textuel ─────────────


def test_the_hidden_rail_has_a_server_rendered_textual_equivalent(client):
    """**Blocage opérateur, refermé.**

    Le rail est `aria-hidden` à juste titre : le compte est déjà en texte
    au-dessus, et une étiquette d'image le répétait. Mais il porte DAVANTAGE —
    répartition des jours, terminée contre en cours, couverture de
    l'historique, type de séance. Masquer un objet dont l'information n'existe
    nulle part ailleurs le rend visuel-seulement.
    """
    body = _with_traces(client).get("/progress").text
    assert 'class="rail" aria-hidden="true"' in body, "le rail n'est plus masqué"

    start = body.index('class="rail" aria-hidden')
    tail = body[start:start + 3000]
    assert 'class="sr-only"' in tail, (
        "le rail est masqué SANS équivalent textuel — son information devient "
        "visuelle-seulement"
    )
    assert "Quatorze derniers jours" in tail


def test_the_textual_equivalent_carries_what_the_rail_shows():
    """Il ne suffit pas qu'un texte existe : il doit porter ce que le rail
    montre en plus du compte."""
    from app.services.progress_signals import build_rail_summary

    # ⚠ `first_known=2` fait des index 0 et 1 des jours HORS historique : une
    # séance qu'on y placerait ne compterait pas. La première écriture de ce
    # test l'ignorait et attendait 3 séances là où la fixture n'en produisait
    # que 2 — le test était faux, pas le code.
    txt = build_rail_summary(_facts_days(done=(4, 8, 12), cardio=(4,),
                                         active=13, first_known=2))
    assert "3 séances terminées" in txt
    assert "12/08 cardio" in txt               # le type distingué
    assert "16/08 musculation" in txt          # une date, et son type
    assert "Séance en cours, non comptée" in txt
    assert "2 jours hors historique" in txt


def test_the_textual_equivalent_never_guesses_a_type():
    """Un template supprimé rend `kind is None`. Le rail n'affiche alors aucune
    texture ; le texte ne doit inventer aucun mot."""
    from app.services.progress_facts import DayTrace, ProgressFacts
    from app.services.progress_signals import build_rail_summary

    txt = build_rail_summary(ProgressFacts(days=(DayTrace(
        offset=0, label="08/08", state="done", kind=None, name="Push A"),)))
    assert "08/08." in txt
    assert "musculation" not in txt
    assert "cardio" not in txt


def test_the_textual_equivalent_is_not_visible_prose(client):
    """`OPERATOR_DECISION` — aucune prose VISIBLE ajoutée au premier niveau.
    L'équivalent vit dans `.sr-only`, donc hors flux visuel."""
    import pathlib
    import re as _re

    src = _uncommented(TEMPLATE.read_text(encoding="utf-8"))
    line = [ln for ln in src.splitlines() if "rail_summary" in ln]
    assert line, "l'équivalent textuel a disparu du gabarit"
    assert 'class="sr-only"' in line[0], (
        "l'équivalent textuel est devenu de la prose visible"
    )

    css = (pathlib.Path(__file__).resolve().parent.parent
           / "app/static/css/app.css").read_text(encoding="utf-8")
    block = css.split(".sr-only {", 1)[1].split("}", 1)[0]
    assert "clip" in block
    assert _re.search(r"width:\s*1px", block)


def test_the_textual_equivalent_recalculates_nothing():
    """Une seule source. Deux producteurs sur les mêmes faits divergeraient le
    jour où l'un change — et la divergence serait invisible, puisque l'un des
    deux ne se voit pas."""
    import ast
    import inspect

    from app.services import progress_signals as ps

    tree = ast.parse(inspect.getsource(ps.build_rail_summary))
    assert not [n for n in ast.walk(tree)
                if isinstance(n, ast.BinOp)
                and isinstance(n.op, (ast.Div, ast.Mult, ast.Sub))], (
        "l'équivalent textuel calcule au lieu de lire `facts.days`"
    )
    src = inspect.getsource(ps.build_rail_summary)
    assert "facts.days" in src, "il ne lit plus la source canonique du rail"
