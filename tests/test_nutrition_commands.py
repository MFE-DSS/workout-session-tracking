"""Nutrition manual domain: no provider, recommendation, UI or real user data."""

import hashlib
import importlib.util
import json

import pytest


def command(values=None):
    return {
        "contract_version": "nutrition-command/1.0.0",
        "request_id": "nut-contract-vector-1",
        "expected_head_token": "0" * 64,
        "operation": "SET_FIELDS",
        "values": {"kcal_milli": 0} if values is None else values,
        "timezone": "Europe/Paris",
        "target_ref": None,
        "confirm_complete": None,
    }


def test_manual_nutrition_command_boundary_exists():
    assert importlib.util.find_spec("app.services.nutrition_commands") is not None


def test_wire_integer_values_preserve_zero_null_and_absence_without_inference():
    from app.services.nutrition_commands import validate_command

    body = command({"kcal_milli": 0, "protein_milli": None, "fat_milli": 1250})
    validated = validate_command("DAY", "2026-11-12", body)
    assert validated == body
    assert "carbohydrate_milli" not in validated["values"]
    assert body["values"] == {"kcal_milli": 0, "protein_milli": None, "fat_milli": 1250}


@pytest.mark.parametrize("bad", [True, False, -1, 1.0, 1.25, 1000000000, float("nan"), float("inf"), "1"])
def test_invalid_milli_values_are_rejected_without_coercion(bad):
    from app.services.nutrition_commands import NutritionError, validate_command

    with pytest.raises(NutritionError, match="invalid_command"):
        validate_command("DAY", "2026-11-12", command({"kcal_milli": bad}))


def test_canonical_bytes_are_fixed_and_shared_with_the_published_vector():
    from app.services.nutrition_commands import command_bytes, command_digest

    body = command()
    path = "/me/nutrition/days/2026-11-12/revisions"
    expected = 'NUT-CMD-1\n{"body":{"confirm_complete":null,"contract_version":"nutrition-command/1.0.0","expected_head_token":"' + "0" * 64 + '","operation":"SET_FIELDS","request_id":"nut-contract-vector-1","target_ref":null,"timezone":"Europe/Paris","values":{"kcal_milli":0}},"method":"POST","namespace":"DAY","path":"/me/nutrition/days/2026-11-12/revisions"}'
    assert command_bytes("DAY", path, body) == expected.encode()
    assert command_digest("DAY", path, body) == hashlib.sha256(expected.encode()).hexdigest()
    reordered = dict(reversed(list(body.items())))
    assert command_bytes("DAY", path, reordered) == expected.encode()
    assert command_digest("DAY", path, command({"fat_milli": 1250})) != command_digest(
        "DAY", path, command({"kcal_milli": None, "fat_milli": 1250})
    )


@pytest.mark.parametrize(
    "mutation",
    [
        {"unknown": 1},
        {"operation": "AUTO_RECOMMEND"},
        {"values": {"weight_kg": 80}},
        {"timezone": "Invalid/Zone"},
        {"expected_head_token": ""},
        {"request_id": "../other"},
        {"values": {}},
    ],
)
def test_closed_command_shape_and_intention(mutation):
    from app.services.nutrition_commands import NutritionError, validate_command

    with pytest.raises(NutritionError):
        validate_command("DAY", "2026-11-12", {**command(), **mutation})


@pytest.mark.parametrize("number", ["1.0", "1e0", "NaN", "Infinity"])
def test_raw_json_numbers_are_not_normalized_into_valid_commands(number):
    from app.services.nutrition_commands import NutritionError, decode_command

    raw = json.dumps(command()).replace('"kcal_milli": 0', '"kcal_milli": ' + number)
    with pytest.raises(NutritionError):
        decode_command(raw)


def test_raw_json_duplicate_keys_are_refused():
    from app.services.nutrition_commands import NutritionError, decode_command

    with pytest.raises(NutritionError):
        decode_command('{"request_id":"one","request_id":"two"}')
