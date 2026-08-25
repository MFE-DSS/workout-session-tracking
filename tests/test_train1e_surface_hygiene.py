"""`TRAIN1-E` — hygiène de surface et surfaces sociales.

CE QUE CES GARDES FERMENT
--------------------------
`TRAIN1-C` a retiré la doctrine du score de Progression. Elle survivait
ailleurs, et au pire endroit possible : sur le profil **des autres**. Le
classement rendait un radar des six axes physiques par ligne, et le profil
public un « Score · N/100 » — c'est-à-dire une lecture corporelle d'autrui,
dans un produit dont le rapport coach s'interdit explicitement « toute
comparaison vs autres utilisateurs ».

  1. LE RADAR REVIENT — il vivait sous **trois** classes CSS différentes ;
     une garde qui n'en viserait qu'une en laisserait deux.
  2. LA LETTRE DISPARAÎT — elle doit RESTER : c'est la note sociale du
     classement, et un classement sans ordre n'est pas un classement.
  3. UNE CIBLE TACTILE RETOMBE SOUS LE STANDARD sur l'Historique.
  4. UN MODULE VIDE PLEINE TAILLE REVIENT.
  5. UN SECOND APPEL À CRÉER APPARAÎT — la duplication de CTA qu'A4 interdit.

MÉTHODE. Chaque garde structurante est vérifiée en PLANTANT son défaut.
"""
from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "app/templates"
LB_SERVICE = ROOT / "app/services/leaderboard.py"
LB_ROUTER = ROOT / "app/routers/leaderboard.py"
CLOSURE_CSS = ROOT / "app/static/css/target_closure.css"
LEGACY_DOC = ROOT / "docs/LEGACY_SCORE_CONSUMERS.md"

#: Les TROIS classes sous lesquelles le radar physique vivait.
RADAR_CLASSES = ("tooltip-radar", "radar-wrap", "profile-preview__radar")

LEADERBOARD_URL = "/leaderboard"
PUBLIC_PROFILE_URL = "/users/testuser"


def _uncommented(src: str) -> str:
    return re.sub(r"\{#.*?#\}", " ", src, flags=re.S)


def _executable_py(src: str) -> str:
    body = re.sub(r'"""[\s\S]*?"""', " ", src)
    return "\n".join(line.split("#", 1)[0] for line in body.splitlines())


# ═════════ C4 — L'ANALYTIQUE PHYSIQUE QUITTE LES SURFACES SOCIALES ═════════


def test_no_physique_radar_survives_on_any_social_surface():
    """Les trois classes, pas une. Chercher `tooltip-radar` seul aurait laissé
    `radar-wrap` sur le profil public et `profile-preview__radar` dans la carte
    d'aperçu — deux radars sur trois, invisibles à la garde."""
    social = ("leaderboard.html", "user_profile.html",
              "_partials/profile_preview.html")
    for name in social:
        body = _uncommented((TEMPLATES / name).read_text(encoding="utf-8"))
        for cls in RADAR_CLASSES:
            assert cls not in body, f"{name} rend « {cls} »"


def test_the_public_profile_no_longer_scores_someone_else(client):
    r = client.get(PUBLIC_PROFILE_URL)
    assert r.status_code == 200
    assert "global_score" not in r.text
    assert "/100</b>" not in r.text


def test_the_social_grade_survives_because_it_is_a_game_grade(client):
    """LE PENDANT, et il compte autant. Une garde qui ne vérifie que le retrait
    laisserait passer une suppression trop large : la lettre vient de
    `compute_grade`, dérivée de la qualité de séance, pas du physique."""
    assert "grade-badge" in client.get(LEADERBOARD_URL).text
    assert "grade-badge" in client.get(PUBLIC_PROFILE_URL).text


def test_the_leaderboard_no_longer_depends_on_the_scoring_service():
    """Il appelait `compute_physique_dashboard` UNE FOIS PAR LIGNE, pour rendre
    l'analytique physique en infobulle."""
    for path in (LB_SERVICE, LB_ROUTER):
        src = _executable_py(path.read_text(encoding="utf-8"))
        assert "compute_physique_dashboard" not in src, path.name
        assert "radar_svg" not in src, path.name


def test_the_legacy_register_records_the_two_departures():
    doc = LEGACY_DOC.read_text(encoding="utf-8")
    assert "SORTI" in doc
    assert "DO_NOT_ACTIVATE_AS_STANDALONE" in doc


# ═════════ C6 — L'HISTORIQUE ═════════


def test_the_history_row_is_the_primary_action(client):
    """La ligne entière est un lien vers la séance : c'est elle l'action, pas
    un contrôle posé à côté."""
    body = _uncommented((TEMPLATES / "history.html").read_text(encoding="utf-8"))
    assert 'class="session-card"' in body
    assert "url_for('session_detail'" in body


def test_the_management_actions_stay_behind_one_disclosure():
    body = _uncommented((TEMPLATES / "history.html").read_text(encoding="utf-8"))
    assert body.count('<details class="history-item__actions">') == 1
    row = body.split('<details class="history-item__actions">', 1)[1]
    assert "toggle_exclude" in row
    assert "delete_session" in row


def test_every_history_control_declares_44px():
    """⚠ CHAQUE RÈGLE, PAS LE BLOC. La première écriture cherchait
    `min-height: 44px` **quelque part** dans la section : abaisser le seul
    `.history-item__toggle` à 26 px la laissait verte, satisfaite par la règle
    voisine des boutons. Trouvé en plantant le défaut.

    Les deux sélecteurs sont donc extraits séparément et vérifiés chacun.
    """
    css = CLOSURE_CSS.read_text(encoding="utf-8")
    for selector in (".history-item__toggle", ".history-item__btn"):
        m = re.search(re.escape(selector) + r"\s*\{([^}]*)\}", css)
        assert m, f"règle absente : {selector}"
        assert "min-height: 44px" in m.group(1), (
            f"{selector} ne déclare plus 44 px : {m.group(1).strip()[:60]}")


def test_the_standard_is_named_as_a_product_standard_not_wcag():
    """44 px est le STANDARD PRODUIT AUREN, pas le seuil WCAG 2.2 (24×24 avec
    exception d'espacement, déjà satisfait avant cette tranche). La feuille
    doit le dire, sinon la prochaine tranche croira corriger une
    non-conformité réglementaire qui n'existe pas."""
    block = CLOSURE_CSS.read_text(encoding="utf-8").split("`TRAIN1-E` / C6", 1)[1]
    assert "WCAG" in block
    assert "STANDARD PRODUIT" in block


def test_the_deferral_that_expired_is_named_not_silently_dropped():
    """`UIV3_TARGETS_44_01` avait déféré ces cibles avec une raison mesurée.
    L'annuler sans dire laquelle des deux moitiés a expiré effacerait le
    raisonnement au lieu de le poursuivre."""
    css = CLOSURE_CSS.read_text(encoding="utf-8")
    # `python:S9073` — le `or` triple cachait laquelle des trois traces on
    # exige réellement. C'est la tranche d'origine qui doit rester nommée.
    assert "UIV3_TARGETS_44_01" in css
    block = css.split("`TRAIN1-E` / C6", 1)[1]
    assert "EXPIRÉ" in block
    assert "JUSTE" in block


# ═════════ C7 — LES MODULES VIDES ═════════


def test_the_scheduled_backup_card_is_not_instantiated_empty(client):
    r = client.get("/export")
    assert r.status_code == 200
    assert "Aucune sauvegarde locale" not in r.text
    assert "Sauvegarde planifiée" not in r.text


def test_the_export_summary_shows_no_naked_dash(client):
    r = client.get("/export")
    values = re.findall(r"<b>(.*?)</b>", r.text, flags=re.S)
    assert not [v for v in values if v.strip() == "—"]


def test_the_programs_empty_state_is_compact(client):
    r = client.get("/programs")
    assert r.status_code == 200
    assert "Pourquoi ce plan" not in r.text
    assert 'class="empty-line"' in r.text


def test_the_programs_page_carries_exactly_one_create_cta(client):
    """A4 interdit la duplication de CTA. Le bouton existait déjà en tête de
    page ; en ajouter un second dans l'état vide aurait rejoué exactement la
    faute que la doctrine ferme."""
    r = client.get("/programs")
    assert r.text.count("Créer un programme") == 1


# ═════════ C11 — LE STATUT DES SURFACES ═════════


def test_the_surface_status_is_recorded():
    doc = LEGACY_DOC.read_text(encoding="utf-8")
    assert "PROGRESSION_L1" in doc
    assert "SOVEREIGN" in doc
    assert "PROGRESSION_L2" in doc
    assert "EVOLVABLE" in doc
