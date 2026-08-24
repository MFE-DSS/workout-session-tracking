"""`TRAIN1-D` — CONVERGENCE ÉPISTÉMIQUE.

CE QUE CES GARDES FERMENT
--------------------------
Le produit rendait un troisième objet analytique, plus prescriptif que les deux
qu'on venait de retirer. Le Coach Report fixait des objectifs chiffrés — « viser
2 séances/sem sur 4 semaines », « cible OMS 150'/sem » — que rien dans le dépôt
ne soutient, sous l'onglet Progression, à deux touches de l'instrument qui
s'interdit précisément de parler en cibles.

Les gardes portent sur les cinq endroits où cette tranche peut se défaire :

  1. UNE PRESCRIPTION REVIENT — il suffit d'un `f"viser {n} séances"`.
  2. UNE RÉFÉRENCE REDEVIENT UNE CIBLE — l'OMS reste citée ; la faute n'était
     pas de la citer mais de la poser à côté du chiffre réel comme un écart.
  3. LE DOCUMENT REDEVIENT UNE DESTINATION — un `is_coach` réintroduit dans
     `is_prog` suffit.
  4. UN TIRET NU REVIENT SUR UN CHAMP SAISISSABLE.
  5. UN SLUG DE RÈGLE EST RENOMMÉ — et tous les liens profonds cassent en
     silence, sans qu'aucune erreur ne se produise à l'exécution.

MÉTHODE. Comme pour `TRAIN1-C`, chaque garde structurante a été vérifiée en
PLANTANT son défaut. Une garde qui reste verte pendant que le défaut est là ne
garde rien — ce dépôt en a compté treize.
"""
from __future__ import annotations

import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "app/templates"
BASE = TEMPLATES / "base.html"
COACH_TPL = TEMPLATES / "coach_report.html"
PROFILE_TPL = TEMPLATES / "profile.html"
SCIENCE_TPL = TEMPLATES / "science.html"
INFERENCE = ROOT / "app/services/coach_inference.py"

RULES_JSON = ROOT / "data/method_rules.json"

COACH_URL = "/coach-report"
SCIENCE_URL = "/science"
PROFILE_URL = "/profile"


def _uncommented_jinja(src: str) -> str:
    return re.sub(r"\{#.*?#\}", " ", src, flags=re.S)


def _executable_py(src: str) -> str:
    """Retire docstrings ET commentaires — sans quoi la garde serait satisfaite
    par le paragraphe qui explique justement qu'on ne fait plus la chose."""
    body = re.sub(r'"""[\s\S]*?"""', " ", src)
    return "\n".join(line.split("#", 1)[0] for line in body.splitlines())


# ═════════ C1 — LE COACH REPORT EST UN DOCUMENT, PAS UNE DESTINATION ═════════


def test_the_coach_report_no_longer_lights_the_progression_tab():
    body = _uncommented_jinja(BASE.read_text(encoding="utf-8"))
    prog = re.search(r"set is_prog = ([^%]+)%\}", body)
    assert prog, "la définition de `is_prog` a disparu — garde aveugle"
    assert "is_coach" not in prog.group(1)


def test_utility_surfaces_light_no_primary_tab(client):
    """Un document qu'on produit n'est pas un endroit où l'on va. `/export`
    n'a jamais allumé d'onglet ; le Coach Report rejoint cette classe."""
    for path in (COACH_URL, "/export"):
        r = client.get(path)
        assert r.status_code == 200, path
        nav = r.text.split('class="app-bottom-nav"', 1)[1]
        assert 'aria-current="page"' not in nav, path


def test_the_coach_report_is_reachable_from_the_export_surface(client):
    """« Move to Export/utility access » suppose que cet accès existe.

    ⚠ `/export` n'était liée depuis AUCUN gabarit avant cette tranche : la
    route existait, la surface était inatteignable autrement qu'en tapant
    l'URL. Y déplacer un document l'aurait envoyé dans un cul-de-sac.
    """
    r = client.get("/export")
    assert r.status_code == 200
    # ⚠ LIRE LE CONTENU, PAS LA COQUE. La première écriture cherchait
    # « Coach Report » dans toute la page — et passait alors même que le bloc
    # avait été retiré, satisfaite par le lien du MENU UTILITAIRE présent sur
    # toutes les pages. Elle prouvait donc l'existence de la navigation, pas
    # celle de la destination. Trouvé en plantant le défaut.
    main = r.text.split('<main', 1)[1]
    assert COACH_URL in main
    assert "Coach Report" in main


def test_the_utility_menu_exposes_the_backup_surface(client):
    r = client.get("/")
    assert "Sauvegarde" in r.text


# ═════════ C1 — AUCUNE PRESCRIPTION D'ENTRAÎNEMENT ═════════


def test_no_training_prescription_is_produced_by_the_inference():
    """La garde de fond. Les cinq consignes retirées se reconnaissent à leur
    verbe ; aucune ne doit réapparaître dans le producteur."""
    src = _executable_py(INFERENCE.read_text(encoding="utf-8"))
    for verb in ("viser ", "Augmenter le", "Rééquilibrer ", "Diversifier ",
                 "indispensable"):
        assert verb not in src, f"consigne réintroduite : « {verb.strip()} »"


def test_the_prescriptive_block_is_gone_from_the_document(client):
    r = client.get(COACH_URL)
    assert r.status_code == 200
    assert "Axes de travail suggérés" not in r.text
    assert "9. Couverture des données" in r.text


def test_the_facts_the_prescriptions_rested_on_are_all_still_rendered(client):
    """`CLAUDE.md §5.3` — ce n'est pas une soustraction seule. Les consignes
    partaient de faits qui, eux, restent tous à l'écran."""
    r = client.get(COACH_URL)
    for block in ("2. Volume et fréquence", "4. Répartition par zone",
                  "5. Patterns moteurs"):
        assert block in r.text, block


def test_the_zone_block_states_a_fact_not_a_verdict(client):
    """« Zones négligées » imputait une faute depuis un bloc étiqueté
    « Calculé ». Un comptage n'a pas le droit de juger — c'est l'étiquette
    « Inféré » qui l'autorise, et les blocs 7 et 8 sont là pour ça."""
    r = client.get(COACH_URL)
    assert "négligées" not in r.text
    assert "Zones les moins travaillées" in r.text


# ═════════ C1 — LA RÉFÉRENCE EXTERNE N'EST PAS UNE CIBLE ═════════


def test_the_external_guideline_is_never_called_a_target(client):
    body = html.unescape(client.get(COACH_URL).text)
    assert "cible OMS" not in body
    assert "OMS" in body
    assert "n'est pas un objectif calculé pour toi" in body


def test_the_reference_is_not_triggered_by_a_threshold(client):
    """Une référence qui n'apparaît QUE lorsqu'on est en dessous n'est pas une
    référence, c'est un reproche déclenché par un seuil.

    ⚠ VÉRIFIÉE SUR LE COMPORTEMENT, PAS SUR LA SOURCE. La première écriture
    cherchait un `<` dans le corps de la fonction : elle ne voyait donc pas un
    seuil écrit avec `>`, et c'est exactement ce qu'un futur correctif
    écrirait. Trouvé en plantant le défaut.
    """
    from app.services.coach_inference import external_references
    from tests.test_coach_report import _fake_report

    below = external_references(_fake_report(cardio_min_per_week=5))
    above = external_references(_fake_report(cardio_min_per_week=600))
    assert below == above
    assert len(below) == 1


# ═════════ C3 — LE MODÈLE ÉPISTÉMIQUE CANONIQUE ═════════


def test_the_canonical_model_has_four_natures_and_three_coverages():
    from app.services import epistemic

    assert epistemic.NATURES == (
        epistemic.MEASURED, epistemic.DERIVED,
        epistemic.INFERRED, epistemic.NOT_DEDUCIBLE)
    assert epistemic.COVERAGES == (
        epistemic.COMPLETE, epistemic.PARTIAL, epistemic.UNKNOWN)


def test_the_two_axes_are_orthogonal_and_every_nature_is_labelled():
    from app.services import epistemic

    assert epistemic.NATURE_X_COVERAGE_IS_ORTHOGONAL
    for nature in epistemic.NATURES:
        assert nature in epistemic.NATURE_LABELS
        assert nature in epistemic.NATURE_MEANING


def test_an_observed_zero_is_complete_coverage_not_unknown():
    """La distinction qui coûte le plus cher quand on la rate. « Des séances
    existent, aucune n'a touché les onze zones » est une observation ENTIÈRE
    dont la valeur est nulle."""
    from app.services import epistemic

    assert epistemic.coverage_of_zone_state("zero") == epistemic.COMPLETE
    assert epistemic.coverage_of_zone_state("unknown") == epistemic.UNKNOWN
    assert epistemic.coverage_of_zone_state("partial") == epistemic.PARTIAL


def test_an_unrecognised_state_degrades_to_unknown_never_to_complete():
    from app.services import epistemic

    assert epistemic.coverage_of_zone_state("zorglub") == epistemic.UNKNOWN


def test_a_count_is_labelled_derived_not_measured(client):
    """Les blocs 2, 4 et 6 s'annonçaient « Mesuré » alors que ce sont des
    COMPTAGES. Exacts, reproductibles — et des dérivations."""
    body = _uncommented_jinja(COACH_TPL.read_text(encoding="utf-8"))
    for title in ("2. Volume et fréquence", "4. Répartition par zone musculaire",
                  "6. Discipline de logging"):
        line = [ln for ln in body.splitlines() if title in ln]
        assert line, title
        assert "coach-tag--derived" in line[0], title


def test_the_template_invents_no_epistemic_label(client):
    """Le gabarit ne doit rendre que les libellés du foyer canonique."""
    from app.services import epistemic

    body = _uncommented_jinja(COACH_TPL.read_text(encoding="utf-8"))
    rendered = set(re.findall(r'coach-tag--([a-z-]+)', body))
    allowed = set(epistemic.NATURES) | {"reference", "not-deductible"}
    assert rendered <= allowed, f"étiquette inventée : {rendered - allowed}"


def test_the_legend_is_rendered_so_the_labels_mean_something(client):
    """Le rapport étiquetait ses blocs depuis Sb_23 sans jamais dire ce que les
    étiquettes signifient — dans un document destiné à un TIERS."""
    from app.services import epistemic

    body = html.unescape(client.get(COACH_URL).text)
    for nature in epistemic.NATURES:
        assert epistemic.NATURE_MEANING[nature] in body, nature


def test_the_progression_level_one_carries_no_epistemic_badge(client):
    """`OPERATOR_DECISION` C3 — on ne badge pas tout. Un écran couvert
    d'étiquettes ne rend pas le produit plus honnête : il transforme un signal
    en bruit de fond."""
    r = client.get("/progress")
    assert "coach-tag" not in r.text


# ═════════ C2 — LE PROFIL ═════════


def test_an_empty_actionable_fact_offers_to_add_it(client):
    """Six `—` à l'échelle d'une valeur. Ici la donnée manque parce que
    personne ne l'a saisie, et la saisie est à un clic : l'état vide doit
    porter l'action, pas le constat."""
    r = client.get(PROFILE_URL)
    assert r.status_code == 200
    values = re.findall(r"<b>(.*?)</b>", r.text, flags=re.S)
    naked = [v for v in values if v.strip() == "—"]
    assert not naked, f"{len(naked)} tiret(s) nu(s) subsistent"
    assert "Ajouter" in r.text


def test_morphology_says_what_is_left_to_do_not_a_score(client):
    """« 0 / 13 mesures » posait un dénominateur comme un score à remplir,
    dans un produit qui vient de retirer les scores."""
    r = client.get(PROFILE_URL)
    assert "/ 13 mesures" not in r.text
    assert "À compléter" in r.text


def test_the_add_affordances_land_on_a_real_anchor(client):
    """Un lien vers une ancre inexistante est un lien menteur."""
    r = client.get(PROFILE_URL)
    body = r.text
    for anchor in re.findall(r'class="stat-add" href="[^"]*#([\w-]+)"', body):
        assert f'id="{anchor}"' in body, f"ancre absente : #{anchor}"


def test_the_training_configuration_left_level_one(client):
    """Elle répond à « comment je veux m'entraîner », qui est la question de
    Mon plan. `TRAIN2` lui donne son domicile."""
    r = client.get(PROFILE_URL)
    assert "Cadence souhaitée" not in r.text


def test_the_training_configuration_is_still_editable(client):
    """ET ELLE RESTE MODIFIABLE — `weekly_planner` consomme ces valeurs.
    Retirer la lecture sans garder l'écriture aurait cassé le planificateur
    en rendant ses entrées inatteignables."""
    r = client.get(PROFILE_URL)
    assert "Modifier mes préférences" in r.text
    assert "cadence_" in r.text, "les contrôles de cadence ont disparu"


# ═════════ C5 — SCIENCE, DOCUMENT DE RÉFÉRENCE CITABLE ═════════


def test_every_method_rule_exposes_its_stable_identifier(client):
    r = client.get(SCIENCE_URL)
    assert r.status_code == 200
    payload = json.loads(RULES_JSON.read_text(encoding="utf-8"))
    for rule in payload["rules"]:
        assert f'id="rule-{rule["slug"]}"' in r.text, rule["slug"]
        assert f'href="#rule-{rule["slug"]}"' in r.text, rule["slug"]


def test_the_rule_slugs_are_pinned():
    """Renommer un slug casse TOUS les liens profonds qui le visent, et rien à
    l'exécution ne le signale : un `#ancre` absent ne lève aucune erreur, il
    dépose le lecteur en haut de onze écrans de référence."""
    payload = json.loads(RULES_JSON.read_text(encoding="utf-8"))
    assert {r["slug"] for r in payload["rules"]} == {
        "carnet-progression", "plages-repetitions", "series-approche",
        "tempo", "temps-repos", "legende-technique", "rest-pause",
    }


def test_every_deep_link_into_science_targets_an_existing_rule(client):
    """La garde qui compte : un lien profond depuis n'importe quelle surface
    doit viser une règle qui existe."""
    payload = json.loads(RULES_JSON.read_text(encoding="utf-8"))
    known = {r["slug"] for r in payload["rules"]}
    sections = set(re.findall(
        r'id="(section-[\w-]+)"',
        SCIENCE_TPL.read_text(encoding="utf-8")))

    found = 0
    for path in TEMPLATES.rglob("*.html"):
        body = _uncommented_jinja(path.read_text(encoding="utf-8"))
        for target in re.findall(r"science_page'\) \}\}#([\w-]+)", body):
            found += 1
            if target.startswith("rule-"):
                assert target[5:] in known, f"{path.name} → #{target}"
            else:
                assert target in sections, f"{path.name} → #{target}"
    assert found >= 3, f"seulement {found} lien(s) profond(s) — garde faible"
