"""Selective admission must not turn an editorial omission into scientific loss."""

import hashlib
import importlib
import json
from pathlib import Path

import pytest

from app.services.muscle_observed_load.limits import ReadLimits
from app.services.muscle_observed_load.provenance import SourceView
from app.services.muscle_observed_load.sqlite_source import bounded_json

ROOT = Path(__file__).resolve().parents[1]
CATALOGUE = "data/sci/exercise_catalogue.json"


def project(raw, expected=None, limits=ReadLimits()):
    try:
        module = importlib.import_module("app.services.muscle_observed_load.catalogue_source")
    except ModuleNotFoundError:
        pytest.fail("selective catalogue admission not implemented")
    return module.project_catalogue(raw, expected or hashlib.sha256(raw).hexdigest(), limits)


def encoded(doc):
    return json.dumps(doc, ensure_ascii=False, separators=(",", ":")).encode()


def specimen(note="synthetic", **extra):
    return {
        "catalogue_header": {"catalogue_version": "synthetic-only"},
        "records": [
            {
                "exercise_id": "synthetic-exercise",
                "exercise_operational": {"curation": {"notes": note}},
                "exercise_science": {"contributions": [{"zone": "pecs", "role": "PRIMARY"}]},
                **extra,
            }
        ],
    }


def test_actual_source_retains_every_non_editorial_field_and_full_digest():
    raw = (ROOT / CATALOGUE).read_bytes()
    before = hashlib.sha256(raw).hexdigest()
    actual = project(raw)
    expected = json.loads(raw)
    for row in expected["records"]:
        row["exercise_operational"]["curation"].pop("notes", None)
    assert actual.document == expected
    assert (
        actual.source_sha256 == "7d1ae5d3c05c4b76c540789e9e07d0c2c0d96c9a4aa03a28c0b4f964441981fd"
    )
    assert len(actual.omitted_paths) == 107
    assert "/records/75/exercise_operational/curation/notes" in actual.omitted_paths
    assert hashlib.sha256((ROOT / CATALOGUE).read_bytes()).hexdigest() == before
    with pytest.raises(ValueError, match="json_string_limit"):
        bounded_json(raw, ReadLimits())


def test_sourceview_exposes_projected_view_without_rehashing_projected_bytes():
    view = SourceView.local(ROOT)
    assert hasattr(view, "catalogue_view"), "selective SourceView not implemented"
    actual = view.catalogue_view()
    assert actual.source_sha256 == view.pins[CATALOGUE]
    assert view.budget.files == 1 and view.budget.total == 411788
    assert view.catalogue_view().document == actual.document
    assert view.budget.files == 1


@pytest.mark.parametrize("size,accepted", [(4096, True), (4097, False)])
def test_retained_string_ceiling_still_applies(size, accepted):
    raw = encoded(specimen("x" * 4302, description="s" * size))
    if accepted:
        assert project(raw).document["records"][0]["description"] == "s" * size
    else:
        with pytest.raises(ValueError, match="json_string_limit"):
            project(raw)


def test_same_named_note_outside_exact_editorial_path_is_not_exempt():
    doc = specimen("x" * 4302)
    doc["records"][0]["exercise_science"]["notes"] = "x" * 4302
    with pytest.raises(ValueError, match="json_string_limit"):
        project(encoded(doc))


def test_opaque_escaped_unicode_is_validated_without_losing_retained_values():
    raw = encoded(specimen("placeholder", label="é𐍈"))
    raw = raw.replace(b'"placeholder"', b'"' + b"\\u00e9" * 4302 + b'\\ud800\\udc00"')
    assert project(raw).document["records"][0]["label"] == "é𐍈"


@pytest.mark.parametrize(
    "fragment",
    [b'"\\q"', b'"\\ud800"', b'"\\udc00"', b'"bad\x01control"', b"{}", b"[]", b"null", b"1"],
)
def test_opaque_content_and_type_must_be_valid(fragment):
    raw = encoded(specimen("placeholder")).replace(b'"placeholder"', fragment)
    with pytest.raises(ValueError):
        project(raw)


@pytest.mark.parametrize(
    "raw",
    [
        b'{"catalogue_header":{},"records":[],"records":[]}',
        b'{"catalogue_header":{},"records":[{"exercise_operational":{"curation":{"notes":"x","notes":"y"}}}]}',
        b'{"catalogue_header":{},"records":[],"n":1e999}',
        b'{"catalogue_header":{},"records":[],"n":NaN}',
        b'{"catalogue_header":{},"records":[],"n":01}',
        b'{"catalogue_header":{},"records":[],"s":"\xff"}',
        b'{"catalogue_header":{},"records":[}',
        b'{"catalogue_header":{},"records":[]}{}',
        b'{"catalogue_header":{},"records":[]}false',
        b'{"catalogue_header":{},"records":[],}',
        b"[]",
        b'{"catalogue_header":[],"records":[]}',
        b'{"catalogue_header":{},"records":{}}',
        b'{"catalogue_header":{},"records":[1]}',
    ],
)
def test_entire_document_must_be_admitted(raw):
    with pytest.raises(ValueError):
        project(raw)


def test_wrong_digest_is_rejected_even_for_valid_json():
    with pytest.raises(ValueError, match="source_digest_mismatch"):
        project(encoded(specimen()), "0" * 64)


def test_source_total_depth_and_token_limits_are_not_relaxed():
    with pytest.raises(ValueError, match="source_byte_limit"):
        project(b" " * 65, limits=ReadLimits(source_total=64))
    with pytest.raises(ValueError, match="json_depth_limit"):
        project(b"[" * 17 + b"0" + b"]" * 17)
    with pytest.raises(ValueError, match="json_token_limit"):
        project(encoded(specimen()), limits=ReadLimits(max_tokens=5))


def test_aliases_and_scientific_roles_match_full_attested_catalogue():
    from types import MappingProxyType

    from app.services.sci_catalogue import SciCatalogue, _check_identities, _freeze, load_catalogue
    from app.services.sci_identity import SciIdentityResolver, build_name_index

    raw = (ROOT / CATALOGUE).read_bytes()
    projected = project(raw)
    records = tuple(_freeze(row) for row in projected.document["records"])
    index = MappingProxyType({row["exercise_id"]: row for row in records})
    _check_identities(index)
    selected = SciCatalogue(
        _freeze(projected.document["catalogue_header"]), records, projected.source_sha256, index
    )
    full = load_catalogue(ROOT / CATALOGUE)
    ekb = json.loads((ROOT / "data/exercise_knowledge_base.json").read_bytes())
    a = SciIdentityResolver(full, build_name_index(ekb, full))
    b = SciIdentityResolver(selected, build_name_index(ekb, selected))
    for name in [*ekb["exercises"], *ekb.get("_aliases", {})]:
        assert a.resolve_name(name) == b.resolve_name(name)
    for row in full.records:
        assert full.raw_roles(row["exercise_id"]) == selected.raw_roles(row["exercise_id"])
