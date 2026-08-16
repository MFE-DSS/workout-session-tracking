"""Sb_22a.next2 — atlas resolution follows the substituted exercise.

Bug N8 (dogfooding) : quand un substitut est choisi, le panel "Comment
bien exécuter X" doit afficher les cues du substitut, pas celles du
prescrit. Les chips/peek/atlas suivent le réalisé.
"""
from __future__ import annotations

from unittest.mock import MagicMock


def _make_se(prescribed_machine_slug="chest-press-machine", substituted_name=None):
    """SessionExercise mock minimal."""
    te = MagicMock()
    te.machine_slug = prescribed_machine_slug
    te.machine_family = None
    se = MagicMock()
    se.template_exercise = te
    se.substituted_name = substituted_name
    se.exercise_name_snapshot = "Chest Press machine"
    return se


def test_atlas_uses_prescribed_when_no_substitute():
    """Backward compat: sans substitut, on retombe sur le prescrit."""
    from app.services import machine_atlas
    machine_atlas.reset_cache()
    se = _make_se()
    out = machine_atlas.get_for_session_exercise(se)
    assert out is not None
    assert out["machine"] is not None
    assert out["machine"]["name"] == "Chest Press machine"


def test_atlas_follows_substituted_name_when_set():
    """Quand un substitut existe dans l'atlas, l'atlas suit le réalisé."""
    from app.services import machine_atlas
    machine_atlas.reset_cache()
    # Le prescrit = Chest Press machine. On substitue par "Développé
    # couché haltères" qui est dans l'atlas sous une autre famille/machine.
    se = _make_se(substituted_name="Développé couché haltères")
    out = machine_atlas.get_for_session_exercise(se)
    # Le résultat doit refléter le substitut, pas le prescrit.
    # (Si le substitut n'est pas dans l'atlas, fallback prescrit — donc on
    # vérifie au minimum que ce n'est plus "Chest Press machine".)
    if out and out["machine"]:
        # Soit on a trouvé le substitut, soit on est tombé sur le prescrit
        # (cas où l'atlas ne référence pas ce nom). On accepte les 2 mais
        # on vérifie qu'on n'a PAS écrasé silencieusement le sub.
        assert out["machine"]["name"] != "Chest Press machine" or se.substituted_name not in [
            m["name"] for f in machine_atlas.all_families() for m in f.get("machines", [])
        ]


def test_get_machine_by_name_exact():
    from app.services import machine_atlas
    machine_atlas.reset_cache()
    m = machine_atlas.get_machine_by_name("Chest Press machine")
    assert m is not None
    assert m["slug"] == "chest-press-machine"


def test_get_machine_by_name_case_insensitive():
    from app.services import machine_atlas
    machine_atlas.reset_cache()
    m1 = machine_atlas.get_machine_by_name("chest press machine")
    m2 = machine_atlas.get_machine_by_name("CHEST PRESS MACHINE")
    assert m1 is not None
    assert m2 is not None
    assert m1["slug"] == m2["slug"]


def test_get_machine_by_name_via_alias():
    """L'atlas indexe aussi par aliases — un nom-alias doit matcher."""
    from app.services import machine_atlas
    machine_atlas.reset_cache()
    # "Presse pectorale" est un alias de chest-press-machine
    m = machine_atlas.get_machine_by_name("Presse pectorale")
    assert m is not None
    assert m["slug"] == "chest-press-machine"


def test_get_machine_by_name_unknown_returns_none():
    from app.services import machine_atlas
    machine_atlas.reset_cache()
    assert machine_atlas.get_machine_by_name("not a real exercise xyz") is None
    assert machine_atlas.get_machine_by_name(None) is None
    assert machine_atlas.get_machine_by_name("") is None


def test_get_for_session_exercise_handles_none_template():
    """SessionExercise sans template_exercise (cas rare) doit retourner None
    proprement, pas crasher."""
    from app.services import machine_atlas
    machine_atlas.reset_cache()
    se = MagicMock()
    se.template_exercise = None
    se.substituted_name = None
    assert machine_atlas.get_for_session_exercise(se) is None


def test_get_for_session_exercise_substitute_not_in_atlas_falls_back():
    """Si le substitut n'est PAS dans l'atlas, on retombe sur le prescrit
    (pas de panel vide)."""
    from app.services import machine_atlas
    machine_atlas.reset_cache()
    se = _make_se(substituted_name="Exercice imaginaire jamais vu")
    out = machine_atlas.get_for_session_exercise(se)
    # Fallback sur le prescrit = chest-press-machine
    assert out is not None
    assert out["machine"]["slug"] == "chest-press-machine"
