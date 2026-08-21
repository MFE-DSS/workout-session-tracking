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
    """**Défaut 3 — le plus grave.** `compute_trend(0, 0)` rend `"stable"`.
    L'ancien gabarit annonçait « Continuité stable » à quelqu'un qui n'avait
    jamais enregistré une séance."""
    from app.services.behavioral import compute_trend
    from app.services.progress_signals import build_progress_signals

    assert compute_trend(0, 0) == "stable"

    cadence = build_progress_signals(_state(sessions_last_7=0, sessions_prev_7=0))[2]
    assert cadence["known"] is False
    assert cadence["value"] == "—"
    assert "stable" not in cadence["value"].lower()


def test_a_real_cadence_shows_both_counts():
    """L'inverse du précédent : quand il y a un rythme, il se lit — sinon la
    correction aurait supprimé le signal au lieu de le corriger."""
    from app.services.progress_signals import build_progress_signals

    cadence = build_progress_signals(_state(sessions_last_7=1, sessions_prev_7=4))[2]
    assert cadence["known"] is True
    assert cadence["value"] == "4 → 1"


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


def _signals_section(client) -> str:
    """La section des signaux seule — le reste de Progression contient des
    jauges et des pourcentages légitimes qui ne relèvent pas de cette tranche.
    """
    body = client.get("/progress").text
    start = body.index('class="signals"')
    return body[start:body.index("Rythme récent")]
