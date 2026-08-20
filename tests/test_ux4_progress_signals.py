"""`UX4_03` — rendre perceptible ce qui était déjà calculé.

LE PROBLÈME QUE CETTE TRANCHE FERME
------------------------------------
Trois signaux existaient, calculés à chaque requête, et n'étaient rendus
**nulle part** : `/progress` annonçait « la régularité » dans son chapeau sans
jamais l'afficher, et `UX4_01` les avait retirés du Profil parce qu'ils y
répondaient à la mauvaise question.

`AUREN ne doit pas annoncer des signaux invisibles.`

LA DÉCISION QUE CES GARDES PROTÈGENT
-------------------------------------
`streak_days` **existe et n'est pas rendu**. Il compte des jours calendaires
CONSÉCUTIFS : un jour de repos correctement pris le remet à zéro. Le rendre
contredirait frontalement la décision produit — *« la régularité ne doit pas
être un streak quotidien »*.

C'est une décision de PRÉSENTATION, pas un calcul nouveau : le service reste
inchangé, seule la surface choisit ce qu'elle montre. Les gardes ci-dessous
empêchent que le streak revienne par inadvertance, et que le vocabulaire
glisse vers le médical.
"""
from __future__ import annotations

import pathlib
import re

TEMPLATE = (pathlib.Path(__file__).resolve().parent.parent
            / "app/templates/progress.html")


def _uncommented(src: str) -> str:
    """Sans les commentaires Jinja.

    Ce gabarit EXPLIQUE pourquoi le streak n'est pas rendu, donc le mot
    apparaît dans sa propre justification. Une garde qui lit la prose rougirait
    sur l'explication du choix — le motif s'est présenté cinq fois dans ce
    dépôt.
    """
    return re.sub(r"\{#.*?#\}", " ", src, flags=re.S)


# ───────────── A1 · les trois signaux sont visibles ─────────────


def test_the_three_signals_are_rendered(client):
    """**A1.** Ils étaient calculés et visibles nulle part."""
    body = client.get("/progress").text
    for signal in ("Charge ressentie", "Régularité", "Continuité"):
        assert signal in body, f"signal absent de la surface : {signal}"


def test_each_signal_carries_a_real_value(client):
    """Rendre l'étiquette sans la valeur serait annoncer une seconde fois un
    signal invisible."""
    body = client.get("/progress").text
    assert body.count('class="signal__value') >= 3
    assert 'class="signal__fill"' in body, "aucune jauge rendue"


def test_the_page_no_longer_promises_what_it_does_not_show(client):
    """Le chapeau annonçait « la régularité » ; elle est désormais rendue."""
    body = client.get("/progress").text
    lede = body[body.index("class=\"lede\""):][:200]
    assert "régularité" in lede
    assert "Régularité" in body


# ───────────── A2 · la bonne surface ─────────────


def test_the_signals_live_on_progression_not_on_the_profile(client):
    """**A2.** `UX4_01` les a retirés du Profil pour une raison ; les y
    ramener annulerait la tranche précédente."""
    profile = client.get("/profile").text
    for signal in ("Charge ressentie", "Régularité", "Continuité"):
        assert signal not in profile, f"{signal} est revenu sur le Profil"


# ───────────── A3 · aucun diagnostic médical ─────────────


def test_no_medical_wording_anywhere_on_the_surface(client):
    """**A3.** « Charge ressentie » décrit ce que l'utilisateur a DÉCLARÉ en
    fin de séance. Aucun terme n'a le droit de suggérer un état
    physiologique mesuré ni un diagnostic."""
    body = client.get("/progress").text.lower()
    # Termes qui ne peuvent PAS apparaître innocemment. « santé » et
    # « médical » en sont volontairement absents : la surface écrit « pas un
    # indicateur de santé », et une garde qui bannit le mot rougirait sur le
    # démenti lui-même. On traque l'AFFIRMATION, pas le vocabulaire.
    for banned in ("diagnostic", "patholog", "symptôme", "surentraînement",
                   "syndrome", "prescription médicale"):
        assert banned not in body, f"vocabulaire médical rendu : « {banned} »"


def test_the_fatigue_signal_states_its_own_source(client):
    """Un chiffre sans provenance se lit comme une mesure objective."""
    body = client.get("/progress").text
    assert "déclaré en fin de séance" in body
    # ⚠ Le démenti disait d'abord « pas un indicateur de santé ». La garde
    # PRÉEXISTANTE `test_no_forbidden_wording_in_progress` interdit ce mot dans
    # le gabarit, commentaires compris — et elle est plus stricte que la
    # mienne, à raison : une règle mécanique ne se discute pas au cas par cas,
    # et un démenti reste une occurrence. La copie a changé, pas la garde.
    assert "rien d'autre" in body


def test_no_fake_ai_score_is_claimed(client):
    """Aucun « score IA » : ces valeurs sont des moyennes pondérées, et le
    dire autrement serait une revendication fausse."""
    body = client.get("/progress").text.lower()
    for banned in ("score ia", "intelligence artificielle", "algorithme prédit",
                   "prédiction"):
        assert banned not in body, f"revendication non fondée : « {banned} »"


# ───────────── A4 · aucun streak quotidien ─────────────


def test_the_daily_streak_is_never_rendered(client):
    """**A4 — la garde centrale.**

    `streak_days` compte des jours calendaires consécutifs : un jour de repos
    le remet à zéro. Le rendre contredirait « un jour de repos correctement
    pris ne casse rien ».
    """
    body = client.get("/progress").text.lower()
    # `jours consécutifs` n'est PAS banni : la surface écrit « aucun compteur
    # de jours consécutifs », et bannir le terme ferait rougir la garde sur la
    # phrase qui énonce la décision. Ce qu'on traque, c'est un streak PRÉSENTÉ
    # — un libellé de compteur, un mot-valise, une flamme.
    for banned in ("jours de série", "série en cours", "streak", "🔥"):
        assert banned not in body, f"streak quotidien rendu : « {banned} »"


def test_the_template_never_reads_streak_days(client):
    """Garde structurelle : tant que le gabarit ne LIT pas la valeur, elle ne
    peut pas réapparaître par un simple changement de libellé."""
    assert "streak_days" not in _uncommented(TEMPLATE.read_text(encoding="utf-8"))


def test_streak_days_is_still_computed():
    """Ne pas rendre n'est pas supprimer. Le service reste intact — la tranche
    est une décision de présentation, pas un changement de calcul."""
    import dataclasses

    from app.services.behavioral import BehavioralState

    fields = {f.name for f in dataclasses.fields(BehavioralState)}
    assert "streak_days" in fields, (
        "le calcul a été supprimé alors que seule sa présentation était en jeu"
    )


def test_continuity_compares_two_windows_rather_than_counting_days(client):
    """La continuité doit EXPLIQUER le rythme réel, pas le gamifier."""
    body = client.get("/progress").text
    assert "sept derniers jours" in body
    assert "sept précédents" in body


def test_the_regularity_note_says_a_rest_day_costs_nothing(client):
    """La décision produit est écrite à l'écran, pas seulement dans le
    dépôt : c'est l'utilisateur qui doit savoir qu'il ne casse rien."""
    assert "Un jour de repos ne" in client.get("/progress").text


# ───────────── contraintes de construction ─────────────


def test_no_new_business_calculation_was_added():
    """Le brief interdit tout calcul nouveau si les signaux existent. La
    tranche compose `compute_behavioral_state` — le service que consomme déjà
    l'accueil — et n'en écrit aucun autre."""
    router = (pathlib.Path(__file__).resolve().parent.parent
              / "app/routers/pages.py").read_text(encoding="utf-8")
    handler = router.split("def progress(", 1)[1].split("\n@router.", 1)[0]
    code = re.sub(r"#.*", " ", handler)
    assert "compute_behavioral_state(db, user.id)" in code
    for invented in ("def compute_", "sum(", "/ 14", "timedelta("):
        assert invented not in code, (
            f"calcul écrit dans le routeur au lieu d'être composé : {invented}"
        )


def test_the_surface_needs_no_javascript(client):
    """La jauge est une largeur en pourcentage. Aucune dépendance JS
    obligatoire — le brief l'interdit."""
    body = client.get("/progress").text
    section = body[body.index("class=\"signals\""):body.index("Rythme récent")]
    for js in ("<script", "onclick", "data-chart", "hx-get"):
        assert js not in section, f"dépendance JS introduite : {js}"


def test_the_gauge_has_an_accessible_name(client):
    """Une barre sans nom accessible ne dit rien à qui ne la voit pas."""
    body = client.get("/progress").text
    assert 'role="img"' in body
    assert "aria-label=\"Charge ressentie" in body


def test_no_body_map_or_anatomical_asset_was_added():
    """Interdits explicites du brief."""
    src = TEMPLATE.read_text(encoding="utf-8").lower()
    # ⚠ `plate` seul matchait `template_kpis`. Un fragment n'est pas un nom :
    # on vise des identifiants entiers.
    for banned in ("bodymap", "body-map", "regional_plate", "muscle_focus",
                   "svg/anat"):
        assert banned not in src, f"asset anatomique introduit : {banned}"


def test_the_colour_carries_no_verdict():
    """Une charge haute et une charge basse ont le MÊME remplissage : seule la
    longueur change. Colorer une fatigue élevée en rouge en ferait un verdict,
    et ce n'en est pas un."""
    css = (pathlib.Path(__file__).resolve().parent.parent
           / "app/static/css/app.css").read_text(encoding="utf-8")
    block = css.split(".signal__fill {", 1)[1].split("}", 1)[0]
    assert "var(--accent)" in block
    for judged in ("--danger", "--warn", "--good", "red", "green"):
        assert judged not in block, (
            f"la jauge encode un jugement par la couleur : {judged}"
        )
