"""Une durée de séance a une borne haute, et l'accueil l'a prouvé.

POURQUOI CETTE GARDE EXISTE
---------------------------
L'accueil affichait, sur une séance laissée ouverte 62 jours :

    En cours · depuis 1502 h 16

Le format était juste. Le nombre était exact. **Ce qu'il disait ne se lisait
pas.** Personne ne convertit 1502 heures en tête.

Le défaut n'était pas dans l'arithmétique mais dans la PORTÉE :
`format_duration_short` est écrite pour une durée de séance — quelques
dizaines de minutes — et rien ne l'empêchait d'être appelée hors de son
domaine. Un formateur sans borne finit toujours par en sortir.

Trouvé en REGARDANT l'écran, pas en lisant le code : aucune des 5 000 gardes
du dépôt ne compare une durée à ce qu'un humain peut lire.
"""

from __future__ import annotations

from datetime import timedelta

import pytest

from app.services.time_format import format_duration_short


@pytest.mark.parametrize(
    ("delta", "attendu"),
    [
        (timedelta(seconds=0), "0 min"),
        (timedelta(seconds=59), "0 min"),
        (timedelta(minutes=45), "45 min"),
        (timedelta(minutes=59), "59 min"),
        (timedelta(hours=1), "1 h 00"),
        (timedelta(hours=1, minutes=7), "1 h 07"),
        (timedelta(hours=23, minutes=59), "23 h 59"),
        # ── la borne : au-delà, on compte en jours
        (timedelta(hours=24), "1 j"),
        (timedelta(days=2, hours=5), "2 j"),
        (timedelta(days=62, hours=14), "62 j"),
    ],
)
def test_the_format_stays_readable_at_every_scale(delta, attendu):
    assert format_duration_short(delta) == attendu


def test_no_duration_is_ever_rendered_in_absurd_hours():
    """LE DÉFAUT D'ORIGINE, énoncé comme propriété.

    Épingler « 62 j » ne dirait rien du motif. Ce qui ne doit plus jamais
    arriver, c'est qu'une durée s'exprime en un nombre d'heures qu'aucun
    lecteur ne convertit.

    Le seuil est à 24 h : c'est la limite au-delà de laquelle une durée cesse
    de décrire un effort pour décrire un oubli.
    """
    for jours in (1, 2, 7, 31, 62, 400):
        rendu = format_duration_short(timedelta(days=jours, minutes=16))
        assert " h " not in rendu, (
            f"{jours} jours rendus « {rendu} » — un nombre d'heures que "
            "personne ne convertit de tête"
        )
        assert rendu.endswith(" j"), rendu


def test_a_negative_delta_never_leaks_a_minus_sign():
    """Une horloge qui recule — décalage serveur, base restaurée — ne doit
    pas produire « -3 min ». Le comportement existait ; il est épinglé parce
    que la borne neuve touche la même fonction."""
    assert format_duration_short(timedelta(seconds=-9000)) == "0 min"


def test_the_ceiling_is_named_and_not_a_magic_number():
    """Une borne écrite en dur dans une condition se déplace sans qu'on le
    remarque. Celle-ci porte un nom, donc une intention."""
    from app.services import time_format

    assert time_format._HOURS_CEILING == 24
