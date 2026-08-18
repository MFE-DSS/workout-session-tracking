"""Sb_AUTH_PASSLIB_TO_BCRYPT_DIRECT_01 — hashing calls bcrypt, not passlib.

WHY THE MIGRATION HAPPENED
--------------------------
passlib 1.7.4 (unmaintained since 2020) cannot load bcrypt 5: its backend
self-test hashes a **255-byte** probe to detect the BSD wraparound bug, and
bcrypt 5 raises on anything past 72 bytes. Backend detection then fails and every
`hash`/`verify` call dies with `_stub_requires_backend`. Observed on the CI of
dependabot PR #7 (run `27494766766`).

That single dependency is what pinned this project to `bcrypt<5`.

WHAT DID NOT CHANGE
-------------------
The stored digests. Both layers write `$2b$` at cost 12, and each verifies the
other's output. No re-hash, no forced reset, no migration — proven here against
a hash that passlib actually produced.

BCRYPT 5 READINESS
------------------
These guards check the two conditions that make the bump safe: nothing imports
`passlib.hash` any more (the probe never runs), and no code path can hand bcrypt
a password past 72 bytes (the new `ValueError` is unreachable).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from helpers import TESTPASS_BCRYPT_HASH, TESTPASS_PLAIN

from app.services.auth import BCRYPT_ROUNDS, hash_password, verify_password
from app.services.password_policy import (
    BCRYPT_MAX_PASSWORD_BYTES,
    PasswordTooLongError,
)

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "app"
AUTH = APP / "services" / "auth.py"
REQUIREMENTS = ROOT / "requirements.txt"
LOCK = ROOT / "requirements-lock.txt"

OVER_72 = "a" * 72 + "TAIL-THAT-BCRYPT-WOULD-IGNORE"


# ───────────── A1 — passlib is out of the runtime path ─────────────

def test_a1_the_auth_module_imports_bcrypt_not_passlib():
    source = AUTH.read_text(encoding="utf-8")
    assert "import bcrypt" in source
    assert "from passlib" not in source


def test_a1_no_application_module_imports_passlib():
    offenders: list[str] = []
    for path in APP.rglob("*.py"):
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if re.match(r"\s*(from|import)\s+passlib", line):
                offenders.append(f"{path.relative_to(ROOT)}:{number}")
    assert offenders == [], f"passlib is still imported at runtime: {offenders}"


def test_a1_no_test_imports_passlib_either():
    """A test that loads `passlib.hash` would trigger the 255-byte backend probe
    and break the whole suite the day bcrypt 5 lands. The migration is only real
    if nothing at all pulls that import in."""
    offenders: list[str] = []
    for path in (ROOT / "tests").rglob("*.py"):
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if re.match(r"\s*(from|import)\s+passlib", line):
                offenders.append(f"{path.relative_to(ROOT)}:{number}")
    assert offenders == [], f"a test still imports passlib: {offenders}"


# ───────────── A2 — legacy digests still verify ─────────────

def test_a2_a_passlib_generated_hash_still_verifies():
    """`TESTPASS_BCRYPT_HASH` was produced by passlib and is committed verbatim.

    Using the pinned constant rather than generating one keeps this proof valid
    after bcrypt 5 lands, when importing passlib would itself fail.
    """
    assert verify_password(TESTPASS_PLAIN, TESTPASS_BCRYPT_HASH) is True


def test_a2_the_legacy_hash_has_the_format_we_keep_writing():
    assert TESTPASS_BCRYPT_HASH.startswith(f"$2b${BCRYPT_ROUNDS}$")


def test_a4_a_wrong_password_is_refused_against_a_legacy_hash():
    assert verify_password("not-the-password", TESTPASS_BCRYPT_HASH) is False


# ───────────── A3 — new digests are indistinguishable ─────────────

def test_a3_a_new_hash_verifies():
    hashed = hash_password("correcthorse1")
    assert verify_password("correcthorse1", hashed) is True


def test_a3_a_new_hash_keeps_the_passlib_era_format():
    """Same ident, same cost — a reader cannot tell which layer wrote it."""
    hashed = hash_password("correcthorse1")
    assert hashed.startswith(f"$2b${BCRYPT_ROUNDS}$")
    assert len(hashed) == len(TESTPASS_BCRYPT_HASH)


def test_a3_two_hashes_of_the_same_password_differ():
    """Salted, as bcrypt must be.

    Bound to two names rather than compared inline: Sonar reads two identical
    expressions either side of an operator as a typo (`python:S5863`) and raises
    it as a BUG, which fails the gate.
    """
    first = hash_password("correcthorse1")
    second = hash_password("correcthorse1")
    assert first != second


def test_a4_a_wrong_password_is_refused_against_a_new_hash():
    hashed = hash_password("correcthorse1")
    assert verify_password("wrong-password", hashed) is False


def test_a3_the_cost_matches_what_passlib_used():
    assert BCRYPT_ROUNDS == 12


# ───────────── A5 — nothing over 72 bytes reaches bcrypt ─────────────

def test_a5_hashing_over_72_bytes_raises_rather_than_truncating():
    with pytest.raises(PasswordTooLongError):
        hash_password(OVER_72)


def test_a5_verifying_over_72_bytes_returns_false_rather_than_raising():
    """Refusal is chosen, not swallowed: no such password could have produced a
    hash through this layer, and under bcrypt 5 `checkpw` would raise."""
    hashed = hash_password("a" * BCRYPT_MAX_PASSWORD_BYTES)
    assert verify_password(OVER_72, hashed) is False


def test_a5_exactly_72_bytes_is_still_allowed():
    at_ceiling = "a" * BCRYPT_MAX_PASSWORD_BYTES
    assert verify_password(at_ceiling, hash_password(at_ceiling)) is True


def test_a5_multibyte_passwords_are_measured_in_bytes():
    """36 accented characters are exactly 72 bytes; 37 are 74 and must be refused."""
    assert verify_password("é" * 36, hash_password("é" * 36)) is True
    with pytest.raises(PasswordTooLongError):
        hash_password("é" * 37)


# ───────────── A6 — bcrypt 5 readiness ─────────────

def test_a6_only_stable_bcrypt_apis_are_used():
    """`hashpw`, `checkpw` and `gensalt` all survive in bcrypt 5; the 5.0
    changelog changes only the >72-byte behaviour of `hashpw`."""
    source = AUTH.read_text(encoding="utf-8")
    used = set(re.findall(r"bcrypt\.(\w+)", source))
    assert used <= {"hashpw", "checkpw", "gensalt"}, f"unexpected bcrypt API: {used}"


def test_a6_the_only_bcrypt5_breaking_change_is_unreachable():
    """bcrypt 5 raises past 72 bytes. Both entry points stop short of it."""
    with pytest.raises(PasswordTooLongError):
        hash_password(OVER_72)
    assert verify_password(OVER_72, TESTPASS_BCRYPT_HASH) is False


# ───────────── A7 — the bump itself is NOT in this sprint ─────────────

def test_a7_the_bcrypt_ceiling_is_still_declared():
    assert "bcrypt>=4.0,<5" in REQUIREMENTS.read_text(encoding="utf-8")


def test_a7_the_lock_still_pins_bcrypt_4():
    pins = dict(re.findall(r"^([a-z0-9_.\-]+)==([^\s]+)$", LOCK.read_text(encoding="utf-8"), re.M))
    assert int(pins["bcrypt"].split(".")[0]) == 4
