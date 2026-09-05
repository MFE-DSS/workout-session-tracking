"""Un horodatage UTC rendu brut affiche la mauvaise date une nuit sur deux.

LE DÉFAUT, PROUVÉ PLUTÔT QUE DÉDUIT

    séance réellement commencée : 06/09/2026 à 00 h 30 (Paris)
    stockée en UTC              : 05/09/2026 22:30

    strftime brut       → « 05/09/2026 »   ← ce que l'écran affichait
    strftime | local    → « 06/09/2026 »   ← la vraie date

Paris est en avance sur UTC. Tout ce qui se passe entre minuit et 01 h ou 02 h
locale s'affichait **la veille**. Pour quelqu'un qui s'entraîne tard, ce n'est
pas un détail de fuseau : c'est sa séance rangée au mauvais jour.

CE QUE CE FICHIER GARDE, ET POURQUOI IL NE PEUT PAS ÊTRE UNE RÈGLE UNIQUE

Recensé : **17 appels à `strftime`** dans les gabarits, dont 3 passaient déjà
par `| local`. Sur les 14 restants, **8 devaient être corrigés et 6 devaient
être laissés intacts** :

* 5 portent des colonnes `Date` (`recorded_on`, `starts_at`, `ends_at`) — un
  jour de calendrier n'a pas de fuseau, et un défi qui commence le 6 septembre
  commence le 6 septembre partout ;
* 1 porte `modified_at`, produit par `datetime.fromtimestamp(stat.st_mtime)`
  **sans `tz`** — donc déjà en heure système locale et naïf. Le localiser une
  seconde fois l'aurait avancé d'une ou deux heures.

Une garde qui exigerait `| local` partout aurait donc **cassé six rendus
corrects** pour en réparer huit. Elle tient la liste des exemptions, chacune
avec sa raison, et interdit qu'on en ajoute une sans l'écrire.
"""
from __future__ import annotations

import pathlib
import re
from datetime import UTC, datetime

from app.templating import to_local

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "app/templates"
JINJA_COMMENT = re.compile(r"\{#.*?#\}", re.S)

#: Un `{{ … .strftime( … }}` dans un gabarit.
APPEL = re.compile(r"\{\{[^{}]*?\.strftime\(")

#: Les sites qui doivent rester BRUTS, avec la raison. La clé est
#: `gabarit::attribut` — pas un numéro de ligne, qui se périmerait au premier
#: ajout de commentaire au-dessus.
EXEMPTES = {
    "readiness_history.html::recorded_on":
        "colonne `Date` — un état du jour est rattaché à un JOUR",
    "squad_challenge_detail.html::starts_at":
        "colonne `Date` — un défi qui commence le 6 septembre commence le "
        "6 septembre partout",
    "squad_challenge_detail.html::ends_at":
        "colonne `Date` — même raison que `starts_at` ci-dessus",
    "squad_challenges.html::starts_at":
        "colonne `Date` — un jour de calendrier n'a pas de fuseau",
    "squad_challenges.html::ends_at":
        "colonne `Date` — même raison que `starts_at` ci-dessus",
    "export.html::modified_at":
        "`datetime.fromtimestamp(st_mtime)` SANS tz — déjà en heure locale, "
        "naïf ; le localiser l'avancerait d'une à deux heures",
}


def _sites() -> list[tuple[str, str, bool]]:
    """(gabarit, attribut, localisé) pour chaque appel à `strftime`."""
    trouves = []
    for f in sorted(TEMPLATES.rglob("*.html")):
        src = JINJA_COMMENT.sub(" ", f.read_text(encoding="utf-8"))
        for m in APPEL.finditer(src):
            frag = m.group(0)
            attr = frag.rsplit(".strftime", 1)[0].rsplit(".", 1)[-1].strip()
            localise = "| local" in frag or "|local" in frag
            trouves.append((str(f.relative_to(TEMPLATES)), attr, localise))
    return trouves


def test_the_defect_is_real_and_this_is_the_case():
    """La preuve, exécutable. Si `to_local` cessait d'agir, cette assertion
    tomberait avant toutes les autres, et on saurait pourquoi elles tombent."""
    minuit_trente_paris = datetime(2026, 9, 5, 22, 30, tzinfo=UTC)
    assert minuit_trente_paris.strftime("%d/%m/%Y") == "05/09/2026"
    assert to_local(minuit_trente_paris).strftime("%d/%m/%Y") == "06/09/2026"


def test_every_timestamp_is_localised_unless_it_is_exempt():
    """Le cœur de la garde."""
    manquants = [
        f"{gab}::{attr}"
        for gab, attr, localise in _sites()
        if not localise and f"{gab}::{attr}" not in EXEMPTES
    ]
    assert not manquants, (
        "`strftime` sur un horodatage UTC sans `| local` — la date affichée "
        "sera fausse d'un jour pour tout ce qui se passe après minuit local.\n"
        "Ajouter `| local`, ou inscrire le site dans EXEMPTES **avec sa "
        "raison** s'il porte une `Date` ou un datetime déjà local :\n  "
        + "\n  ".join(manquants)
    )


def test_no_exemption_is_stale():
    """Une exemption qui ne correspond plus à rien est un mensonge qui dort.

    Si un gabarit disparaît ou si son site passe à `| local`, l'entrée doit
    partir — sinon la liste finit par autoriser des sites qu'elle ne décrit
    plus.
    """
    reels = {f"{gab}::{attr}" for gab, attr, loc in _sites() if not loc}
    perimees = sorted(set(EXEMPTES) - reels)
    assert not perimees, (
        "exemptions qui ne correspondent à aucun site brut — les retirer : "
        f"{perimees}"
    )


def test_every_exemption_carries_a_reason():
    """Une exemption sans motif est une dérogation, pas une décision."""
    muettes = [k for k, v in EXEMPTES.items() if len(v.strip()) < 15]
    assert not muettes, f"exemptions sans raison écrite : {muettes}"
