"""TRAIN 3 / `A2` étape B — la substitution se compare par IDENTITÉ.

LE DÉFAUT, PROUVÉ AVANT D'ÊTRE CORRIGÉ
---------------------------------------
Deux endroits du produit décident si deux séances portent sur le même
mouvement, et tous deux le faisaient par **égalité de chaîne exacte** :
`overload_inputs._matches_substitution_policy` et
`stats._matches_current_substitution`.

`Curl marteau câble (corde)` et `Curl marteau câble corde` sont **toutes deux
présentes dans les données du dépôt** — le catalogue écrit la première, l'EKB
la seconde — et désignent le même mouvement : leur forme normalisée est
identique, et `Sb_EKB_ORTHOGRAPHIC_ALIAS_01` avait déjà tranché qu'il s'agit
d'un défaut de construction, pas d'un désaccord de données.

Appelée avec ces deux écritures, la politique rendait `False`. **Le même
mouvement ne partageait pas son historique de charges, sans le moindre signal
à l'écran** — un utilisateur voyait « aucune référence » là où il avait
soulevé la semaine précédente.

CE QUE CES GARDES FERMENT
--------------------------
  1. LA COMPARAISON REDEVIENT ORTHOGRAPHIQUE — un `==` sur les noms suffit.
  2. L'APPARIEMENT S'ÉLARGIT TROP — deux mouvements DIFFÉRENTS partagent un
     historique. Ce serait pire que le défaut corrigé : une charge fausse
     plutôt qu'une charge absente.
  3. UN NOM INCONNU DEVIENT COMPARABLE À TOUT — un exercice qu'aucune identité
     ne reconnaît doit se comparer à son égal, jamais à n'importe quoi.
  4. LA FRONTIÈRE PRESCRIT / SUBSTITUÉ BOUGE — elle est antérieure à cette
     tranche et n'a aucune raison de changer.
"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.services.exercise_identity import (
    KEY_IDENTITY,
    KEY_RAW,
    identity_key,
    normalize,
)
from app.services.stats import last_time_by_exercise_code

#: Les deux écritures réelles, relevées dans les données du dépôt.
SPELLING_A = "Curl marteau câble (corde)"
SPELLING_B = "Curl marteau câble corde"
#: Un mouvement franchement différent — témoin d'élargissement excessif.
OTHER = "Presse à cuisses"
#: `python:S1192` mord à trois occurrences.
IN_PROGRESS = "in_progress"


def _ctx(client):
    from app.database import SessionLocal
    from app.models.user import User

    db = SessionLocal()
    uid = db.query(User).first().id
    return db, uid, datetime(2026, 5, 1, 12, 0, tzinfo=UTC)


def _mk_session(db, user_id, *, started_at, status="completed", code="E1",
                substituted_name=None, weight=None, reps=None):
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    s = WorkoutSession(
        user_id=user_id, template_slug_snapshot="push-a",
        template_name_snapshot="Push A", started_at=started_at, status=status,
    )
    se = SessionExercise(
        exercise_code_snapshot=code, exercise_name_snapshot="Exercice prescrit",
        substituted_name=substituted_name, position=1,
    )
    if weight is not None or reps is not None:
        se.set_logs.append(SetLog(kind="work", set_index=1, weight_kg=weight,
                                  reps=reps, completed=True))
    s.session_exercises.append(se)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


# ═════════ LA PRÉMISSE EST VRAIE ═════════


def test_the_two_spellings_really_are_two_distinct_strings():
    """Sans quoi tout ce fichier ne prouverait rien. La garde tient la
    prémisse du défaut : deux chaînes différentes, une seule forme
    normalisée."""
    assert SPELLING_A != SPELLING_B
    assert normalize(SPELLING_A) == normalize(SPELLING_B)


def test_both_spellings_are_known_to_the_identity_referential(client):
    """`Sb_EXERCISE_IDENTITY_01` les reconnaît toutes deux — c'est ce qui rend
    la correction possible sans rien inventer."""
    db, _, _ = _ctx(client)
    try:
        key_a, key_b = identity_key(db, SPELLING_A), identity_key(db, SPELLING_B)
        assert key_a is not None, SPELLING_A
        assert key_a.startswith(KEY_IDENTITY), key_a
        assert key_a == key_b
    finally:
        db.close()


# ═════════ LA CLÉ D'IDENTITÉ ═════════


def test_an_empty_substitution_is_the_prescribed_case(client):
    """`None` n'est pas « inconnu » : c'est « rien n'a été substitué »."""
    db, _, _ = _ctx(client)
    try:
        assert identity_key(db, None) is None
        assert identity_key(db, "") is None
        assert identity_key(db, "   ") is None
    finally:
        db.close()


def test_an_unknown_name_still_gets_a_key_of_its_own(client):
    """Un mouvement qu'aucune identité ne reconnaît ne disparaît pas de la
    comparaison : il se compare **à son égal**. Rendre `None` l'aurait confondu
    avec le prescrit — un exercice inconnu serait devenu l'exercice prescrit."""
    db, _, _ = _ctx(client)
    try:
        key = identity_key(db, "Mouvement que personne ne connaît")
        assert key is not None
        assert key.startswith(KEY_RAW)
        assert key != identity_key(db, "Un autre mouvement inconnu")
    finally:
        db.close()


def test_two_spellings_of_an_unknown_name_share_their_key(client):
    """La même règle vaut hors référentiel : c'est la forme normalisée qui
    décide, pas la ponctuation."""
    db, _, _ = _ctx(client)
    try:
        assert (identity_key(db, "Machin bidule (variante)")
                == identity_key(db, "Machin bidule variante"))
    finally:
        db.close()


def test_a_known_key_can_never_collide_with_an_unknown_one(client):
    """Les deux familles de clés portent un préfixe distinct. Sans lui, un slug
    et une forme normalisée pourraient coïncider au gré d'un changement de
    slugification — une collision silencieuse entre un exercice du référentiel
    et un inconnu."""
    db, _, _ = _ctx(client)
    try:
        known = identity_key(db, SPELLING_A)
        unknown = identity_key(db, "Mouvement inconnu quelconque")
        assert known.startswith(KEY_IDENTITY)
        assert unknown.startswith(KEY_RAW)
        assert KEY_IDENTITY != KEY_RAW
    finally:
        db.close()


def test_two_different_movements_never_share_a_key(client):
    """LA GARDE QUI COMPTE LE PLUS. Élargir trop serait pire que le défaut
    corrigé : une charge FAUSSE plutôt qu'une charge absente."""
    db, _, _ = _ctx(client)
    try:
        assert identity_key(db, SPELLING_A) != identity_key(db, OTHER)
    finally:
        db.close()


# ═════════ LE DÉFAUT EST FERMÉ, BOUT EN BOUT ═════════


def test_the_two_spellings_now_share_their_load_history(client):
    """LE DÉFAUT. Séance passée écrite d'une façon, séance courante de
    l'autre : la référence de charge doit apparaître."""
    db, uid, now = _ctx(client)
    try:
        _mk_session(db, uid, started_at=now - timedelta(days=5),
                    substituted_name=SPELLING_A, weight=32.5, reps=10)
        current = _mk_session(db, uid, started_at=now, status=IN_PROGRESS,
                              substituted_name=SPELLING_B)
        lt = last_time_by_exercise_code(db, current, now)
    finally:
        db.close()
    assert "E1" in lt, "le même mouvement ne retrouve pas son historique"
    assert lt["E1"]["has_data"] is True
    assert "32" in lt["E1"]["weights_str"]


def test_a_different_movement_still_surfaces_nothing(client):
    """Le pendant, et la vraie mesure de la correction : le silence reste."""
    db, uid, now = _ctx(client)
    try:
        _mk_session(db, uid, started_at=now - timedelta(days=5),
                    substituted_name=OTHER, weight=120.0, reps=8)
        current = _mk_session(db, uid, started_at=now, status=IN_PROGRESS,
                              substituted_name=SPELLING_A)
        lt = last_time_by_exercise_code(db, current, now)
    finally:
        db.close()
    assert "E1" not in lt, "une charge d'un AUTRE mouvement a été remontée"


def test_a_substitution_never_borrows_the_prescribed_history(client):
    """Frontière antérieure à cette tranche : elle ne bouge pas."""
    db, uid, now = _ctx(client)
    try:
        _mk_session(db, uid, started_at=now - timedelta(days=5),
                    substituted_name=None, weight=80.0, reps=10)
        current = _mk_session(db, uid, started_at=now, status=IN_PROGRESS,
                              substituted_name=SPELLING_A)
        lt = last_time_by_exercise_code(db, current, now)
    finally:
        db.close()
    assert "E1" not in lt


def test_the_prescribed_case_never_borrows_a_substitution(client):
    db, uid, now = _ctx(client)
    try:
        _mk_session(db, uid, started_at=now - timedelta(days=5),
                    substituted_name=SPELLING_A, weight=32.5, reps=10)
        current = _mk_session(db, uid, started_at=now, status=IN_PROGRESS,
                              substituted_name=None)
        lt = last_time_by_exercise_code(db, current, now)
    finally:
        db.close()
    assert "E1" not in lt


# ═════════ L'OVERLOAD APPLIQUE LA MÊME RÈGLE ═════════


def test_the_overload_history_follows_the_same_identity_rule(client):
    """Les deux sites partagent désormais UNE règle. Les laisser diverger
    ferait apparaître une référence de charge sur une surface et pas sur
    l'autre, pour la même séance."""
    from app.services.overload_inputs import _matches_substitution_policy

    db, _, _ = _ctx(client)
    try:
        from app.models.session import SessionExercise

        past = SessionExercise(exercise_code_snapshot="E1",
                               exercise_name_snapshot="x",
                               substituted_name=SPELLING_A, position=1)
        current_key = identity_key(db, SPELLING_B)
        assert _matches_substitution_policy(
            past, current_is_substituted=True, current_key=current_key, db=db)

        other_key = identity_key(db, OTHER)
        assert not _matches_substitution_policy(
            past, current_is_substituted=True, current_key=other_key, db=db)

        assert not _matches_substitution_policy(
            past, current_is_substituted=False, current_key=None, db=db)
    finally:
        db.close()


def test_a_substitution_without_a_usable_name_consumes_nothing(client):
    """Le cas conservateur, et le seul que mes premières plantations ne
    touchaient pas : la séance courante est déclarée SUBSTITUÉE mais son nom
    ne donne aucune clé (vide, blancs). Rendre `True` la laisserait consommer
    n'importe quel historique, prescrit compris. Le silence est la seule
    réponse honnête — on ne sait pas ce qui a été exécuté."""
    from app.models.session import SessionExercise
    from app.services.overload_inputs import _matches_substitution_policy

    db, _, _ = _ctx(client)
    try:
        assert identity_key(db, "   ") is None, "prémisse de la garde"
        for past_sub in (None, SPELLING_A, OTHER):
            past = SessionExercise(exercise_code_snapshot="E1",
                                   exercise_name_snapshot="x",
                                   substituted_name=past_sub, position=1)
            assert not _matches_substitution_policy(
                past, current_is_substituted=True, current_key=None, db=db), (
                f"historique consommé pour {past_sub!r} sans clé courante"
            )
    finally:
        db.close()


def test_neither_comparison_site_compares_raw_names_any_more():
    """Garde STRUCTURELLE. Une comparaison de chaînes réintroduite ailleurs
    rouvrirait le défaut sans faire échouer les gardes de comportement
    ci-dessus, qui ne connaissent que deux orthographes."""
    import pathlib
    import re

    root = pathlib.Path(__file__).resolve().parent.parent
    for module, forbidden in (
        ("app/services/overload_inputs.py",
         r"past_sub\s*==\s*current_substituted_name"),
        ("app/services/stats.py", r"_normalize_sub\(\s*[a-z_]+\.substituted"),
    ):
        src = (root / module).read_text(encoding="utf-8")
        body = re.sub(r'"""[\s\S]*?"""', " ", src)
        assert not re.search(forbidden, body), (
            f"{module} compare de nouveau des noms bruts"
        )
