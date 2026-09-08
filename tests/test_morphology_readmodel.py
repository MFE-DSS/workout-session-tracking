"""Sb_MORPHO_PROFILE_READMODEL_01 — rendre le profil inspectable, sans pouvoir.

Deux propriétés portent cette tranche, et les deux se testent par ce que la page
**ne dit pas** : elle n'affiche pas de valeur de remplacement pour un fait
absent, et elle ne promet aucun effet sur le programme.
"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

# Même contrainte que la tranche 1 : la fixture `client` purge `sys.modules`,
# donc aucun import `app.*` au niveau module.

PROFILE_URL = "/profile"
MORPHO_TITLE = "Mesures morphologiques"
WINGSPAN_MISSING = "Envergure non renseignée"
#: `UI-CP1` — la morphologie n'a plus de carte à elle : elle est une bande du
#: relevé corporel. C'est l'instrument entier qui sert de périmètre
#: d'inspection, et il est nommé par sa classe racine plutôt que par un titre
#: de carte — un titre est une formulation, une racine d'instrument est une
#: structure.
LEDGER_ANCHOR = 'class="body-ledger"'


@pytest.fixture(autouse=True)
def _app_db(client):
    return client


def _add(db, uid, *, days_ago=0, **fields):
    from app.models.measurement import BodyMeasurement

    row = BodyMeasurement(
        user_id=uid,
        measured_at=datetime.now(UTC) - timedelta(days=days_ago),
        **fields,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def _set_height(db, uid, height):
    from sqlalchemy import select

    from app.models.user import User

    db.execute(select(User).where(User.id == uid)).scalar_one().height_cm = height
    db.commit()


def _session():
    from app.database import SessionLocal

    return SessionLocal()


def _uid():
    from tests.helpers import get_test_user_id

    return get_test_user_id()


def _readmodel():
    from app.services.morphology_readmodel import build_morphology_readmodel

    with _session() as db:
        return build_morphology_readmodel(db, _uid())


def _section(client) -> str:
    """L'INSTRUMENT CORPOREL ENTIER — successeur de la carte morphologique.

    `UI-CP1` — CE QUI A CHANGÉ, ET POURQUOI CE N'EST PAS UN AFFAIBLISSEMENT.

    Cette fonction découpait la page à partir du titre « Mesures
    morphologiques », c'est-à-dire à partir d'une CARTE. BODY_LEDGER dissout
    cette carte par conception : la morphologie n'est plus un bloc à côté des
    autres, c'est une bande du relevé corporel. Le point d'ancrage devait donc
    suivre l'objet, sinon trente et une gardes tombaient d'un coup en accusant
    un défaut qui n'existe pas.

    La docstring d'origine justifiait le découpage par « pour que la prose
    voisine ne masque pas un défaut ». Élargir à l'instrument entier ne peut
    RIEN masquer : c'est un sur-ensemble strict de ce qui était inspecté. Une
    formulation interdite qui aurait migré vers une bande voisine est
    désormais attrapée, alors qu'elle échappait à l'ancien découpage.

    La garde est donc plus large qu'avant, pas plus permissive.
    """
    page = client.get(PROFILE_URL).text
    start = page.index(LEDGER_ANCHOR)
    return page[start:page.index("</section>", start)]


def _visible_text(client) -> str:
    """The section with markup removed — what a reader actually sees.

    Needed because inline styles carry `width:100%`, which is a layout value
    and not a confidence shown to anyone. Scanning raw HTML for a percentage
    would fail on CSS and prove nothing about the copy.
    """
    import re

    return re.sub(r"<[^>]+>", " ", _section(client))


def _readouts(client) -> str:
    """Les BANDES DE RELEVÉ seules — sans le rail de tiroirs.

    `UI-CP1` — l'invariant « aucune valeur inventée » porte sur ce que
    l'instrument AFFIRME du corps, pas sur tout ce que la page contient. En
    élargissant le périmètre d'inspection à l'instrument entier, la date
    d'inscription du compte — un fait réel, ni corporel ni inventé — entrait
    dans le champ d'un test qui interdit tout chiffre à l'état vide.

    Découper avant le rail garde la garde exactement sur son objet.
    """
    import re

    section = _section(client)
    bandes = section.split('class="bl-drawers"', 1)[0]
    return re.sub(r"<[^>]+>", " ", bandes)


# ── États de données ─────────────────────────────────────────────────────────


def test_a_new_user_sees_the_surface_without_inventing_a_single_value(client):
    """**Migré par `UX4_01`, invariant conservé.**

    La garde exigeait que la surface ÉNUMÈRE chaque mesure absente
    (« Envergure non renseignée · Tour de taille non renseigné · … »). La
    décision opérateur du 2026-08-20 l'interdit : *un seul état vide représente
    le domaine et donne au plus un prochain pas véridique*. Sept façons de dire
    la même absence, et la liste s'allongeait à chaque champ ajouté au modèle.

    **L'invariant qui compte n'est pas l'énumération — c'est de ne rien
    inventer.** Il est conservé et durci : aucun chiffre ne doit apparaître
    dans l'état vide. Le read-model, lui, continue de nommer chaque manque —
    les gardes sur `rm.missing` sont inchangées.
    """
    section = _section(client)
    assert "Aucune mesure morphologique" in section
    # Aucune valeur inventée : pas un seul chiffre dans les RELEVÉS à l'état
    # vide. Le rail de tiroirs est hors champ — voir `_readouts`.
    import re
    assert not re.search(r"\d", _readouts(client)), (
        "un nombre apparaît alors qu'aucune mesure n'existe"
    )


def test_partial_measurements_show_what_exists_and_name_what_does_not():
    with _session() as db:
        _add(db, _uid(), waist_cm=80.0)
    rm = _readmodel()
    keys = {f.key for f in rm.facts}
    assert "waist_cm" in keys
    assert "chest_cm" not in keys
    assert WINGSPAN_MISSING in rm.missing


def test_a_full_profile_exposes_every_supported_fact():
    with _session() as db:
        uid = _uid()
        _set_height(db, uid, 180)
        _add(db, uid, wingspan_cm=186.0, waist_cm=78.0, chest_cm=104.0,
             thigh_cm_left=60.0, thigh_cm_right=60.0,
             calf_cm_left=38.0, calf_cm_right=38.0)
    rm = _readmodel()
    assert {f.key for f in rm.facts} == {
        "height_cm", "wingspan_cm", "waist_cm", "chest_cm", "thigh_cm", "calf_cm",
    }
    assert rm.missing == ()


def test_mixed_date_facts_are_announced_as_such():
    with _session() as db:
        uid = _uid()
        _add(db, uid, days_ago=60, chest_cm=100.0)
        _add(db, uid, days_ago=1, waist_cm=80.0)
    rm = _readmodel()
    assert rm.is_mixed_date is True
    assert "dates différentes" in rm.mixed_date_notice


def test_the_readmodel_runs_without_any_observation():
    """No observation surface exists; the read model must not require one."""
    with _session() as db:
        uid = _uid()
        _set_height(db, uid, 180)
        _add(db, uid, waist_cm=78.0, chest_cm=104.0)
    rm = _readmodel()
    assert rm.has_anything


# ── Envergure absente ────────────────────────────────────────────────────────


def test_a_missing_wingspan_is_named_not_neutralised():
    with _session() as db:
        uid = _uid()
        _set_height(db, uid, 180)
        _add(db, uid, waist_cm=80.0)
    rm = _readmodel()
    assert rm.ape_index is None
    assert WINGSPAN_MISSING in rm.missing


def test_the_page_never_shows_a_neutral_ape_index(client):
    """Absence of the row is the invariant — not the absence of a phrasing.

    An earlier version only banned the literals "ape index neutre" and
    "ape index : 0". Planting a `value=0.0, basis="neutre"` fallback left this
    test green, because the rendered cells never spell either phrase. It now
    asserts the row is simply not there.
    """
    with _session() as db:
        uid = _uid()
        _set_height(db, uid, 180)
        _add(db, uid, waist_cm=80.0)
    text = _visible_text(client).lower()
    assert "ape index" not in text
    # `UX4_01` — la surface n'énumère plus les manques (décision n°5) ; c'est
    # le read-model qui les nomme, et les gardes sur `rm.missing` le vérifient.
    # Ce qui est gardé ici reste l'essentiel : **aucun indice dérivé n'apparaît
    # tant que ses deux faits n'existent pas**.
    assert WINGSPAN_MISSING in _readmodel().missing


def test_the_ape_index_appears_only_when_both_facts_exist():
    with _session() as db:
        uid = _uid()
        _set_height(db, uid, 180)
        _add(db, uid, wingspan_cm=186.0)
    rm = _readmodel()
    assert rm.ape_index is not None
    assert rm.ape_index.value == 6.0


# ── Interprétations ──────────────────────────────────────────────────────────


def test_every_interpretation_exposes_layer_confidence_and_evidence():
    with _session() as db:
        uid = _uid()
        _set_height(db, uid, 180)
        _add(db, uid, wingspan_cm=186.0, waist_cm=78.0, chest_cm=104.0)
    rm = _readmodel()
    assert rm.interpretations
    for i in rm.interpretations:
        assert i.layer_label
        assert i.confidence_label
        assert i.evidence
        assert i.rationale


def test_confidence_is_a_category_never_a_percentage():
    with _session() as db:
        uid = _uid()
        _set_height(db, uid, 180)
        _add(db, uid, wingspan_cm=186.0, waist_cm=78.0, chest_cm=104.0)
    rm = _readmodel()
    for i in rm.interpretations:
        assert "%" not in i.confidence_label


def test_descriptors_are_deterministic():
    with _session() as db:
        uid = _uid()
        _set_height(db, uid, 180)
        _add(db, uid, wingspan_cm=186.0, waist_cm=78.0, chest_cm=104.0)
    first = _readmodel()
    second = _readmodel()
    assert [i.descriptor_id for i in first.interpretations] == \
        [i.descriptor_id for i in second.interpretations]


def test_fact_descriptors_are_not_duplicated_as_interpretations():
    with _session() as db:
        uid = _uid()
        _set_height(db, uid, 180)
        _add(db, uid, waist_cm=78.0)
    rm = _readmodel()
    assert not any(i.descriptor_id.startswith("fact_") for i in rm.interpretations)


# ── Garde de formulation ─────────────────────────────────────────────────────

FORBIDDEN_COPY = (
    "diagnostic", "diagnostique", "pathologie", "posture", "insertion",
    "fémur", "humérus", "longueur osseuse", "masse grasse", "body fat",
    "morphotype", "ectomorphe", "endomorphe", "mésomorphe",
    "blessure", "risque de blessure", "morphologie optimale", "optimal",
    "tu es fait pour", "génétique",
)


@pytest.mark.parametrize("banned", FORBIDDEN_COPY)
def test_the_rendered_section_never_uses_forbidden_wording(client, banned):
    with _session() as db:
        uid = _uid()
        _set_height(db, uid, 180)
        _add(db, uid, wingspan_cm=186.0, waist_cm=78.0, chest_cm=104.0,
             thigh_cm_left=60.0, thigh_cm_right=60.0, calf_cm_left=38.0,
             calf_cm_right=38.0)
    assert banned not in _section(client).lower()


def test_the_rendered_section_shows_no_percentage_confidence(client):
    import re

    with _session() as db:
        uid = _uid()
        _set_height(db, uid, 180)
        _add(db, uid, wingspan_cm=186.0, waist_cm=78.0, chest_cm=104.0)
    assert not re.search(r"\d+\s*%", _visible_text(client))


def test_the_engine_denial_is_not_rendered_to_the_user(client):
    """The guardrail is a denial — printing it puts the medical frame in view.

    It stays available on the read model for audit, and off the page.
    """
    with _session() as db:
        uid = _uid()
        _set_height(db, uid, 180)
        _add(db, uid, wingspan_cm=186.0, waist_cm=78.0, chest_cm=104.0)
    rm = _readmodel()
    assert any(i.guardrail for i in rm.interpretations)   # kept for audit
    assert "aucun diagnostic" not in _section(client).lower()


# ── Aucune promesse de conséquence ───────────────────────────────────────────


def test_the_surface_states_that_the_program_is_not_affected_yet(client):
    section = _section(client)
    assert "ne modifient pas encore automatiquement ton programme" in section


@pytest.mark.parametrize(
    "promise",
    ["change ton programme", "adapte ton programme", "ton programme a été"],
)
def test_the_surface_promises_no_planner_effect(client, promise):
    assert promise not in _section(client).lower()


# ── Surface ──────────────────────────────────────────────────────────────────


def test_the_surface_lives_on_the_existing_profile_page(client):
    """Aucune route dédiée : la morphologie se lit sur `/profile`.

    `UI-CP1` — la garde vérifiait la présence d'un TITRE DE CARTE. Le titre a
    disparu avec la carte ; le fait, lui, doit toujours être rendu là. On
    vérifie donc le FAIT et non son cadre : un tour de taille saisi doit
    apparaître avec sa valeur sur la page du profil.
    """
    with _session() as db:
        _add(db, _uid(), waist_cm=80.0)
    page = client.get(PROFILE_URL).text
    assert LEDGER_ANCHOR in page, "l'instrument corporel n'est pas rendu"
    assert "Tour de taille" in page
    assert "80.0" in page, "la valeur mesurée n'atteint pas l'écran"


def test_no_dedicated_morphology_route_is_added(client):
    for path in ("/morphologie", "/morphology"):
        assert client.get(path, follow_redirects=False).status_code == 404


def test_the_section_is_labelled_for_assistive_technology(client):
    """L'instrument et chacune de ses bandes portent un nom accessible.

    `UI-CP1` — la garde épinglait `aria-labelledby="morpho-title"`, l'écriture
    exacte d'UNE carte. La CAPACITÉ — un lecteur d'écran sait ce qu'il lit —
    est vérifiée ici sur l'instrument ET sur ses relevés, donc sur davantage
    de choses qu'avant.
    """
    with _session() as db:
        _add(db, _uid(), waist_cm=80.0)
    page = client.get(PROFILE_URL).text
    assert 'aria-label="Ce qu\'AUREN sait de ton corps"' in page, (
        "l'instrument n'a pas de nom accessible"
    )
    for ancre in ('aria-labelledby="bl-measured"', 'id="bl-measured"'):
        assert ancre in page, f"la bande de relevé n'est pas nommée : {ancre}"


def test_each_measured_fact_is_associated_with_its_value(client):
    """LA CAPACITÉ QUE LE TABLEAU PORTAIT, ET QU'IL FALLAIT REMPLACER.

    Le relevé était un `<table>` avec `scope="row"` / `scope="col"` et une
    `<caption>` : une vraie capacité d'accessibilité, pas un ornement. Ce
    tableau a été retiré parce que ses trois colonnes cassaient leurs cellules
    à 390 px — mesuré au rendu, pas supposé.

    Le retirer SANS remplacer son association libellé↔valeur aurait été une
    régression invisible : les tests seraient restés verts, et un lecteur
    d'écran aurait perdu le lien entre « Tour de taille » et « 80,0 cm ».
    `<dt>` / `<dd>` rend cette association NATIVE.

    ⚠ Cette garde vérifie l'ASSOCIATION, pas le choix de balise : elle exige
    que la valeur soit décrite par son libellé, ce qu'un `<dl>` fait et qu'une
    pile de `<span>` ne fait pas.
    """
    import re

    with _session() as db:
        _add(db, _uid(), waist_cm=80.0)
    section = _section(client)
    paires = re.findall(r"<dt[^>]*>(.*?)</dt>\s*<dd[^>]*>(.*?)</dd>",
                        section, re.S)
    assert paires, "aucun couple libellé/valeur associé dans le relevé"
    aplati = [(re.sub(r"\s+", " ", t).strip(), re.sub(r"\s+", " ", v).strip())
              for t, v in paires]
    assert ("Tour de taille", "80.0 cm") in aplati, aplati


# ── Isolation du planificateur ───────────────────────────────────────────────


def test_the_readmodel_module_is_read_only_by_construction():
    """No write API reaches the database from this module."""
    import pathlib

    import app.services as services_pkg

    src = (pathlib.Path(services_pkg.__file__).parent
           / "morphology_readmodel.py").read_text(encoding="utf-8")
    for banned in ("db.add(", "db.commit(", "db.delete(", "db.merge("):
        assert banned not in src


def test_no_frozen_planner_module_imports_the_readmodel():
    import pathlib

    import app.services as services_pkg

    root = pathlib.Path(services_pkg.__file__).parent
    for name in ("weekly_volume_budget", "weekly_planner",
                 "weekly_capacity_allocator", "weekly_set_allocation",
                 "weekly_plan_materialization", "set_contribution",
                 "adaptive_replan", "recommendation"):
        src = (root / f"{name}.py").read_text(encoding="utf-8")
        assert "morphology_readmodel" not in src, name


def test_reading_the_profile_does_not_move_the_weekly_plan(client):
    from app.services.training_preferences import TrainingPreferencesData
    from app.services.weekly_planner import build_weekly_plan

    prefs = TrainingPreferencesData(
        sessions_per_week=4, focus_priorities=("arms",),
    )
    before = build_weekly_plan(prefs)

    with _session() as db:
        uid = _uid()
        _set_height(db, uid, 180)
        _add(db, uid, wingspan_cm=188.0, waist_cm=78.0, chest_cm=104.0)
    client.get(PROFILE_URL)

    after = build_weekly_plan(prefs)
    assert after.fingerprint == before.fingerprint


# ═══════════════════════════════════════════════════════════════════════════
# LA FRAÎCHEUR D'UNE DONNÉE CORPORELLE — les gardes que `UI-CP1` a OUBLIÉES
#
# ⚠ POURQUOI CE BLOC EXISTE, dit sans enjoliver. `UI-CP1` (PR #226) a livré la
# fraîcheur corporelle — `FactRow.age_label`, `weight_age_label`, les trois
# régimes de confiance — et **n'a porté AUCUNE garde de sa substance**. Ses
# tests vérifiaient la STRUCTURE (association `dt`/`dd`, zéro carte, zéro
# tiroir ouvert, la réponse avant le formulaire) et rien de ce que la tranche
# apportait réellement. Le trou a été trouvé au nettoyage, en inspectant ce
# qu'un worktree contenait avant de le supprimer.
#
# C'est exactement le mode d'échec que ce dépôt catalogue depuis des semaines,
# commis sur la tranche qui le documentait.
#
# CES GARDES EXERCENT LE PRODUIT. Chercher `age_label` dans le read-model
# prouverait que le champ existe, pas qu'il atteint un œil.
# ═══════════════════════════════════════════════════════════════════════════


def test_l_age_d_un_fait_atteint_la_page(client):
    """Le geste central de la tranche, vérifié par le TEXTE VISIBLE.

    `FactRow.measured_at` était peuplé, transporté intact jusqu'au gabarit, et
    jeté à la dernière ligne. La phrase juste au-dessus avouait pourtant que
    les valeurs sont « prises à des dates différentes » : l'écran reconnaissait
    la mêlée et refusait de la chiffrer.
    """
    with _session() as db:
        _add(db, _uid(), days_ago=7, waist_cm=81.0)

    vu = _visible_text(client)
    assert "Tour de taille" in vu
    assert "il y a 7 j" in vu, (
        f"l'ancienneté n'atteint pas la page — vu : {vu[:400]}"
    )


def test_le_poids_porte_son_age(client):
    """La RÉPONSE PRIMAIRE de l'instrument, et la seule clé que `UI-CP1` a
    ajoutée au contexte de la route — non gardée jusqu'ici.

    Le poids est la donnée corporelle la plus volatile et la seule que
    l'entraînement consomme. Sans son âge, « 78,4 kg » de ce matin et
    « 78,4 kg » de mars se rendent EXACTEMENT PAREIL : ce n'est plus une
    donnée, c'est un souvenir.
    """
    with _session() as db:
        _add(db, _uid(), days_ago=3, weight_kg=78.4)

    vu = _visible_text(client)
    assert "78.4" in vu, f"le poids n'atteint pas la page — vu : {vu[:400]}"
    assert "il y a 3 j" in vu, (
        f"le poids est affiché SANS son âge — vu : {vu[:400]}"
    )


def test_les_trois_regimes_de_confiance_ne_se_confondent_pas(client):
    """LE CŒUR DU CONTRAT, et il ne tient que si les régimes DIFFÈRENT.

    `UI-CP1` a décidé que la fraîcheur ne s'applique pas uniformément :

      OBSERVATION       le tour de taille → porte son âge
      RÉFÉRENCE STABLE  la taille → n'en porte PAS. Une taille d'adulte ne
                        périme pas ; lui coller un âge suggérerait qu'elle
                        doit être reprise, et noierait les âges qui comptent
      INCONNU           la FC repos → `users.resting_hr` est un `Integer` nu,
                        le schéma N'A PAS de colonne de date. L'ignorance se
                        dit, elle ne se maquille pas

    Une garde qui vérifierait seulement « il y a un âge quelque part »
    laisserait passer la régression la plus probable : appliquer le même
    traitement aux trois, ce qui détruit l'information que la tranche apporte.
    """
    with _session() as db:
        uid = _uid()
        _set_height(db, uid, 179)
        _add(db, uid, days_ago=12, waist_cm=81.0)
        from sqlalchemy import select

        from app.models.user import User

        db.execute(select(User).where(User.id == uid)).scalar_one().resting_hr = 58
        db.commit()

    vu = _visible_text(client)

    # OBSERVATION — l'âge est chiffré.
    assert "il y a 12 j" in vu, f"observation sans âge — vu : {vu[:500]}"

    # RÉFÉRENCE STABLE — nommée comme telle, et SANS ancienneté.
    assert "Donnée de référence" in vu, (
        f"la taille ne se déclare pas référence stable — vu : {vu[:500]}"
    )

    # INCONNU — dit en toutes lettres.
    assert "date inconnue" in vu, (
        f"la FC repos passe pour datée — vu : {vu[:500]}"
    )


def test_aucune_couleur_d_alerte_ne_se_pose_sur_l_anciennete(client):
    """⚠ UNE DÉCISION OPÉRATEUR QUE RIEN NE GARDAIT.

    Une implémentation de référence antérieure peignait en AMBRE la ligne la
    plus ancienne. L'opérateur l'a interdit : une sémantique d'avertissement
    sur l'âge suppose une POLITIQUE DE DOMAINE, et **aucun seuil de validité
    corporelle n'existe dans ce dépôt**. Emprunter ceux de `recovery_contract`
    — qui portent sur la récupération d'entraînement — aurait été inventer une
    règle en la déguisant en réemploi.

    L'ambre est réservé au propriétaire d'action dominant. L'âge est un FAIT,
    rendu comme les autres.

    Cette garde empêche qu'une tranche future le réintroduise « par confort de
    lecture », ce qui est exactement la forme sous laquelle il était arrivé.
    """
    import re

    with _session() as db:
        uid = _uid()
        _add(db, uid, days_ago=40, chest_cm=104.0)
        _add(db, uid, days_ago=2, waist_cm=81.0)

    rm = _readmodel()
    assert rm.is_mixed_date, "prémisse invalide : les dates doivent être mêlées"

    section = _section(client)
    # La provenance et l'âge vivent dans `.bl-row__meta`. Aucune de ces cellules
    # ne doit porter une classe modificatrice autre que celles décidées.
    metas = re.findall(r'class="bl-row__meta([^"]*)"', section)
    assert metas, "aucune ligne de provenance rendue — prémisse invalide"
    autorises = {"", " bl-row__meta--unknown"}
    inattendus = sorted({m for m in metas if m not in autorises})
    assert not inattendus, (
        f"une classe non décidée peint l'ancienneté : {inattendus}. L'âge est "
        "un fait, pas un verdict — aucun seuil corporel n'existe ici."
    )


def test_le_derive_ne_se_dit_pas_non_date(client):
    """L'ape index n'a pas d'âge PROPRE : il vaut celui de ses deux sources.

    Le dire « date inconnue » serait faux — il est daté, deux fois, et pas
    forcément du même jour. Le mot juste est « dérivé ».
    """
    with _session() as db:
        uid = _uid()
        _set_height(db, uid, 180)
        _add(db, uid, wingspan_cm=188.0)

    rm = _readmodel()
    assert rm.ape_index is not None, "prémisse invalide : pas d'ape index"
    vu = _visible_text(client)
    assert "dérivé" in vu, f"le dérivé ne se nomme pas — vu : {vu[:400]}"


def test_un_horodatage_naif_ne_fait_pas_exploser_la_page(client):
    """LE PIÈGE MESURÉ : la colonne ment sur son propre type.

    `BodyMeasurement.measured_at` est déclarée `DateTime(timezone=True)` et
    **SQLite rend un datetime NAÏF** — vérifié en base. Soustraire un
    `datetime.now(UTC)` d'un naïf lève `TypeError`, et la page entière tombe
    en 500. `relative_hours_ago` absorbe l'écart ; c'est la raison principale
    de l'appeler plutôt que de soustraire à la main.

    ⚠ DEUX NIVEAUX, délibérément. L'unitaire plante le naïf explicitement,
    sans dépendre du hasard du pilote de base ; le second vérifie que la PAGE
    tient — parce que c'est la page qui tombait.
    """
    from datetime import datetime as _dt

    from app.services.morphology_readmodel import _age

    naif = _dt(2026, 8, 9, 7, 30)              # aucun tzinfo, comme SQLite
    assert naif.tzinfo is None, "prémisse du test invalide"
    rendu = _age(naif, None)                    # référence = maintenant, aware
    assert rendu and "il y a" in rendu, f"attendu une ancienneté, vu {rendu!r}"

    with _session() as db:
        _add(db, _uid(), days_ago=5, waist_cm=81.0)
    assert client.get(PROFILE_URL).status_code == 200


def test_as_of_gouverne_l_anciennete_affichee():
    """`as_of` borne la lecture dans le PASSÉ — il est donc la référence.

    Un profil rejoué au 1er août ne doit pas afficher l'ancienneté
    d'aujourd'hui, sans quoi « rejouer le profil tel qu'il était » ment sur la
    seule chose que la tranche ajoute.

    ⚠ La première écriture de cette garde assertait
    `_age(...) == "hier" or "j" in _age(...)`. La seconde branche est vraie
    pour « il y a 2 j », « il y a 30 j » ET « il y a 3 mois » — donc la
    disjonction ne pouvait pratiquement pas échouer. Les valeurs sont
    désormais exactes.
    """
    from datetime import datetime as _dt

    from app.services.morphology_readmodel import _age

    mesure = _dt(2026, 8, 1, 12, 0, tzinfo=UTC)
    assert _age(mesure, _dt(2026, 8, 2, 12, 0, tzinfo=UTC)) == "hier"
    assert _age(mesure, _dt(2026, 8, 3, 12, 0, tzinfo=UTC)) == "il y a 2 j"
    assert _age(mesure, _dt(2026, 12, 1, 12, 0, tzinfo=UTC)) == "il y a 4 mois"


def test_la_provenance_et_l_age_restent_UN_SEUL_fait(client):
    """LA DÉCISION DE DENSITÉ, épinglée — parce que le RENDU l'a imposée.

    Le premier jet rendait le relevé en tableau et ajoutait une QUATRIÈME
    colonne pour la date. Les tests étaient verts ; le rendu à 390 px l'a
    réfutée : « 179.0 / cm », « mesure / directe » et « Tour de / poitrine »
    passaient chacun sur deux lignes. Seul l'œil l'a dit (`CLAUDE.md §5.1`).

    D'où vient une valeur et de quand elle date sont **un seul fait** —
    « mesure directe · il y a 7 j » — pas deux informations à mettre en
    colonnes. Chaque ligne porte donc AU PLUS UNE cellule de provenance.

    Cette garde empêche qu'une tranche future rouvre la quatrième colonne sans
    repasser par un rendu.
    """
    import re

    with _session() as db:
        uid = _uid()
        _set_height(db, uid, 180)
        _add(db, uid, days_ago=3, waist_cm=81.0, chest_cm=104.0)

    section = _section(client)
    # Un « bloc de ligne » = un `dt` et tout ce qui le suit jusqu'au `dt`
    # suivant. Chacun doit contenir exactement une valeur et au plus une
    # provenance.
    blocs = re.split(r"<dt\b", section)[1:]
    assert blocs, "aucune ligne de relevé rendue — prémisse invalide"
    for bloc in blocs:
        provenances = len(re.findall(r'class="bl-row__meta', bloc))
        assert provenances <= 1, (
            f"une ligne porte {provenances} cellules de provenance — la "
            "quatrième colonne a été réfutée par le rendu à 390 px"
        )
