"""Admission successor boundaries, using synthetic facts but no positive authority."""

from copy import deepcopy

import pytest

from tests.science_calibration_samples import (
    calibrated_episode,
    episode,
    event,
    time_components,
    time_session,
)
from tools.science_initial_policy.admission_calibration import calibrate_for_admission
from tools.science_initial_policy.admission_time import assess_time_for_admission


def test_old_history_is_not_an_active_calibration():
    raw = calibrated_episode()
    raw['started_at'] = '2026-11-06T11:10:00Z'
    before = deepcopy(raw)
    result = calibrate_for_admission(raw, min_reps=8, max_reps=12)
    assert result['state'] == 'NEEDS_CALIBRATION'
    assert result['load_kg'] is None
    assert raw == before


def test_old_attempt_recorded_today_does_not_start_current_episode():
    raw = calibrated_episode()
    raw['started_at'] = '2026-11-06T11:10:00Z'
    raw['events'] = [raw['events'][2]]
    raw['events'][0]['provenance']['recorded_at'] = '2026-11-06T11:11:00Z'
    assert calibrate_for_admission(raw, min_reps=8, max_reps=12)['state'] == 'NEEDS_CALIBRATION'


def test_current_familiarization_starts_episode():
    result = calibrate_for_admission(
        episode([event('FAMILIARIZATION_STARTED', 1)]), min_reps=8, max_reps=12
    )
    assert result['state'] == 'CALIBRATION_IN_PROGRESS'
    assert result['load_kg'] is None


def test_historical_concern_is_not_cleared_by_new_episode():
    raw = episode([event('CONCERN_REPORTED', 1)], started_at='2026-11-06T11:10:00Z')
    result = calibrate_for_admission(raw, min_reps=8, max_reps=12)
    assert result['state'] == 'CALIBRATION_IN_PROGRESS'
    assert 'EPISODE_REVIEW_REQUIRED' in result['reasons']
    assert result['automatic_next_action'] == 'NONE'


def test_observed_setting_is_preserved_without_inventing_rir():
    result = calibrate_for_admission(calibrated_episode(), min_reps=8, max_reps=12)
    assert result['state'] == 'CALIBRATED'
    assert result['load_kg'] == 40.0
    assert result['reported_rir'] is None
    assert result['effort_sufficiency'] == 'UNKNOWN'


def _partial_time(**changes):
    session = time_session()
    rows = time_components(session)
    work = next(r for r in rows if r['coverage_key'] == 'press/work/1')
    work.update(lower_seconds=80.0, upper_seconds=None, **changes)
    return session, rows


def test_partial_high_retains_safe_disjoint_lower_bound_for_refutation():
    session, rows = _partial_time()
    result = assess_time_for_admission(
        session, budget_minutes=2, components=rows, layout='DISJOINT_SEQUENTIAL'
    )
    # 0 prep + 10 prep + 80 work + 60 rest + 10 work + 10 operations.
    assert result['lower_seconds'] == 170.0
    assert result['upper_seconds'] is None
    assert result['ordinal'] == 'LIKELY_EXCEEDS'
    assert result['duration']['state'] == 'UNKNOWN'
    assert result['runtime_availability'] == 'NOT_SERVED'


def test_incomplete_coverage_can_only_supply_proven_disjoint_lower_bound():
    session, rows = _partial_time()
    rows = [r for r in rows if r['coverage_key'] == 'press/work/1']
    result = assess_time_for_admission(
        session, budget_minutes=3, components=rows, layout='DISJOINT_SEQUENTIAL'
    )
    assert result['lower_seconds'] == 80.0
    assert result['upper_seconds'] is None
    assert result['ordinal'] == 'UNKNOWN'
    assert 'COVERAGE_INCOMPLETE' in result['uncertainty']


@pytest.mark.parametrize('invalid', ['source', 'scope', 'history', 'unilateral', 'clock', 'overlap'])
def test_unjustified_component_does_not_raise_the_lower_bound(invalid):
    session, rows = _partial_time()
    rows = [r for r in rows if r['coverage_key'] == 'press/work/1']
    layout = 'DISJOINT_SEQUENTIAL'
    if invalid == 'source':
        rows[0]['provenance']['source_ref'] = None
    elif invalid == 'scope':
        rows[0]['scope_fingerprint'] = 'wrong-scope'
    elif invalid == 'history':
        rows[0]['basis_kind'] = 'OBSERVED_HISTORY'
    elif invalid == 'unilateral':
        session['slots'][0]['unilateral'] = True
    elif invalid == 'clock':
        rows[0]['clock_ref'] = 'clock:test'
    else:
        layout = 'UNSPECIFIED'
    result = assess_time_for_admission(session, budget_minutes=3, components=rows, layout=layout)
    assert result['lower_seconds'] == (None if invalid == 'unilateral' else 60)
    assert result['ordinal'] == 'UNKNOWN'
    assert result['duration']['state'] == 'UNKNOWN'


def _v2_case(name='returning'):
    import json
    from pathlib import Path

    cases = json.loads((Path(__file__).resolve().parents[1] /
        'docs/science/sci-p02-initial-policy/calibration-time-01/producer-fixtures.json').read_text())
    return deepcopy(next(c for c in cases if c['scenario'] == name))


@pytest.mark.parametrize('edit', ['bool_to_int', 'int_to_float'])
def test_strict_verification_rejects_python_numeric_equivalence(edit):
    from tools.science_initial_policy.admission_system import verify_evaluation_strict
    from tools.science_initial_policy.v2_registry import load_v2_registry

    case = _v2_case()
    if edit == 'bool_to_int':
        case['result']['draft']['executable'] = 0
    else:
        case['result']['draft']['physical_work_sets_total'] = 28.0
    with pytest.raises(ValueError):
        verify_evaluation_strict(case['request'], case['result'], load_v2_registry())


def test_real_admission_evaluator_has_no_binding_and_consumes_corrected_diagnostics():
    from tools.science_initial_policy.admission_registry import load_admission_registry
    from tools.science_initial_policy.admission_system import evaluate_admission
    from tools.science_initial_policy.v2_registry import load_v2_registry

    case = _v2_case()
    # All accepted observations predate this episode, while the frozen v2
    # returned IN_PROGRESS. The successor must actually consume its correction.
    for ep in case['request']['episodes']:
        ep['started_at'] = '2026-11-06T11:10:00Z'
    from tools.science_initial_policy.v2_producer import produce_v2
    bundle = load_v2_registry()
    old = produce_v2(case['request'], bundle)
    result = evaluate_admission(case['request'], old, bundle, load_admission_registry())
    assert result['verdict'] == 'NOT_ADMITTED'
    assert {g['gate'] for g in result['gates']} == {'C1', 'C2', 'C3', 'C4', 'C5', 'C6'}
    assert all(g['state'] == 'NOT_ADMITTED' for g in result['gates'])
    assert all(c['state'] == 'NEEDS_CALIBRATION' for c in result['calibration_by_context'].values())
    assert result['runtime_availability'] == 'NOT_SERVED'
    assert 'candidate_plan' not in result


def test_empty_registry_cannot_be_promoted_by_dataclass_edit():
    from dataclasses import replace

    from tools.science_initial_policy.admission_registry import (
        assert_trusted_admission_registry,
        load_admission_registry,
    )

    registry = load_admission_registry()
    with pytest.raises(ValueError):
        assert_trusted_admission_registry(replace(registry, registry_digest='0' * 64))


@pytest.mark.parametrize('value', [float('nan'), float('inf'), -float('inf'), True])
def test_strict_verifier_rejects_nonfinite_or_boolean_set_counts(value):
    from tools.science_initial_policy.admission_system import verify_evaluation_strict
    from tools.science_initial_policy.v2_registry import load_v2_registry

    case = _v2_case()
    case['result']['draft']['physical_work_sets_total'] = value
    with pytest.raises(ValueError):
        verify_evaluation_strict(case['request'], case['result'], load_v2_registry())


def test_unchecked_result_model_edit_is_revalidated_as_raw_json_types():
    from tools.science_initial_policy.admission_system import verify_evaluation_strict
    from tools.science_initial_policy.v2_producer import EvaluationResult
    from tools.science_initial_policy.v2_registry import load_v2_registry

    case = _v2_case()
    model = EvaluationResult.model_validate(case['result'])
    model.draft['executable'] = 0
    with pytest.raises(ValueError):
        verify_evaluation_strict(case['request'], model, load_v2_registry())


def test_old_result_cannot_bind_changed_observation_or_subject():
    from tools.science_initial_policy.admission_system import verify_evaluation_strict
    from tools.science_initial_policy.v2_registry import load_v2_registry

    case = _v2_case('novice')
    original_fingerprint = case['result']['request_fingerprint']
    case['request']['subject_ref'] = 'subject:other'
    with pytest.raises(ValueError):
        verify_evaluation_strict(case['request'], case['result'], load_v2_registry())
    assert case['result']['request_fingerprint'] == original_fingerprint


def test_successor_time_is_consumed_without_a_duration_or_ready():
    from tools.science_initial_policy.admission_registry import load_admission_registry
    from tools.science_initial_policy.admission_system import evaluate_admission
    from tools.science_initial_policy.v2_producer import produce_v2
    from tools.science_initial_policy.v2_registry import load_v2_registry

    case = _v2_case()
    rows = case['request']['timing_inputs'][0]['components']
    work = next(c for c in rows if c['kind'] == 'WORK')
    work.update(lower_seconds=5000.0, upper_seconds=None)
    bundle = load_v2_registry()
    historical = produce_v2(case['request'], bundle)
    result = evaluate_admission(case['request'], historical, bundle, load_admission_registry())
    timing = result['time_by_session'][0]
    assert timing['lower_seconds'] > 5000.0
    assert timing['upper_seconds'] is None
    assert timing['ordinal'] == 'LIKELY_EXCEEDS'
    assert timing['duration']['state'] == 'UNKNOWN'
    assert result['verdict'] == 'NOT_ADMITTED'


@pytest.mark.parametrize('case_name,status', [
    ('novice', 'POLICY_UNAVAILABLE'),
    ('unknown_equipment', 'POLICY_UNAVAILABLE'),
    ('missing_inputs', 'INSUFFICIENT_DATA'),
    ('conflicting_inputs', 'CONFLICTING_DATA'),
])
def test_policy_refusal_does_not_mask_historical_input_assessment(case_name, status):
    from tools.science_initial_policy.admission_registry import load_admission_registry
    from tools.science_initial_policy.admission_system import evaluate_admission
    from tools.science_initial_policy.v2_registry import load_v2_registry

    case = _v2_case(case_name)
    before = deepcopy(case)
    result = evaluate_admission(case['request'], case['result'], load_v2_registry(), load_admission_registry())
    assert result['historical_status'] == status
    assert result['verdict'] == 'NOT_ADMITTED'
    assert case == before


def test_permuting_semantically_ordered_facts_keeps_full_admission_fingerprint():
    from tools.science_initial_policy.admission_registry import load_admission_registry
    from tools.science_initial_policy.admission_system import evaluate_admission
    from tools.science_initial_policy.v2_registry import load_v2_registry

    case = _v2_case()
    bundle, registry = load_v2_registry(), load_admission_registry()
    result = evaluate_admission(case['request'], case['result'], bundle, registry)
    case['request']['episodes'].reverse()
    for ep in case['request']['episodes']:
        ep['events'].reverse()
    case['request']['timing_inputs'].reverse()
    for timing in case['request']['timing_inputs']:
        timing['components'].reverse()
    assert evaluate_admission(case['request'], case['result'], bundle, registry) == result


def _copy_pinned_files(tmp_path):
    import json
    import shutil
    from pathlib import Path

    from tools.science_initial_policy.admission_registry import DIRECTORY

    root = Path(__file__).resolve().parents[1]
    sources = json.loads((root / DIRECTORY / 'registry-manifest.v1.json').read_text())['sha256']
    for name in [*sources, f'{DIRECTORY}/registry.v1.json', f'{DIRECTORY}/registry-manifest.v1.json']:
        dest = tmp_path / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / name, dest)
    return tmp_path


@pytest.mark.parametrize('tamper', ['registry', 'manifest', 'source', 'binding', 'escape'])
def test_registry_rejects_disk_drift_and_unadmitted_bindings(tmp_path, tamper):
    import json

    from tools.science_initial_policy.admission_registry import DIRECTORY, load_admission_registry

    root = _copy_pinned_files(tmp_path)
    if tamper == 'registry':
        target = root / DIRECTORY / 'registry.v1.json'
        target.write_bytes(target.read_bytes() + b' ')
    elif tamper == 'manifest':
        target = root / DIRECTORY / 'registry-manifest.v1.json'
        target.write_bytes(target.read_bytes() + b' ')
    elif tamper == 'source':
        target = root / 'tools/science_initial_policy/admission_time.py'
        target.write_text('pass\n')
    elif tamper == 'binding':
        target = root / DIRECTORY / 'registry.v1.json'
        value = json.loads(target.read_text())
        value['bindings'] = [{'state': 'APPROVED', 'reviewer': 'fake'}]
        target.write_text(json.dumps(value))
    else:
        target = root / 'tools/science_initial_policy/admission_time.py'
        outside = tmp_path.parent / 'outside-source.py'
        outside.write_bytes(target.read_bytes())
        target.unlink()
        target.symlink_to(outside)
    with pytest.raises(ValueError):
        load_admission_registry(root)


def test_admission_fixture_artifacts_match_real_producer_without_serving_ready():
    from pathlib import Path

    from tools.science_initial_policy.admission_system_fixtures import artifacts, generated_cases

    root = Path(__file__).resolve().parents[1]
    directory = root / 'docs/science/sci-p02-initial-policy/admission-system-01'
    cases = generated_cases()
    assert len(cases) == 18
    assert len({c['scenario'] for c in cases}) == 18
    assert {c['result']['historical_status'] for c in cases if 'result' in c} >= {
        'POLICY_UNAVAILABLE', 'INSUFFICIENT_DATA', 'CONFLICTING_DATA',
    }
    for case in cases:
        assert case['fixture_kind'] == 'SYNTHETIC_INPUT_REAL_ADMISSION_EVALUATOR_NOT_SERVED'
        if 'result' in case:
            assert case['result']['verdict'] == 'NOT_ADMITTED'
            assert case['result']['runtime_availability'] == 'NOT_SERVED'
            assert 'candidate_plan' not in case['result']
        else:
            assert case['rejection']['code'] == 'INVALID_EVALUATION'
    for name, content in artifacts().items():
        assert (directory / name).read_bytes() == content


def test_imported_old_confirmations_and_acceptance_do_not_reconfirm_today():
    raw = calibrated_episode()
    raw['started_at'] = '2026-11-06T11:10:00Z'
    for index, e in enumerate(raw['events'], 1):
        e['provenance']['measured_at'] = f'2026-11-06T11:0{index}:00Z'
        e['provenance']['recorded_at'] = f'2026-11-06T11:{10 + index}:00Z'
    result = calibrate_for_admission(raw, min_reps=8, max_reps=12)
    assert result['state'] == 'NEEDS_CALIBRATION'
    assert result['load_kg'] is None
    assert result['reference_event_id'] is None


def test_old_trial_with_genuine_current_reconfirmation_remains_usable():
    raw = calibrated_episode()
    context_event, familiar, trial, acceptance = raw['events']
    trial['sequence'] = 1
    for e, index in ((context_event, 2), (familiar, 3), (acceptance, 4)):
        e['sequence'] = index
        e['provenance']['recorded_at'] = f'2026-11-06T11:{10 + index}:00Z'
    raw.update(started_at='2026-11-06T11:10:00Z', events=[trial, context_event, familiar, acceptance])
    result = calibrate_for_admission(raw, min_reps=8, max_reps=12)
    assert result['state'] == 'CALIBRATED'
    assert result['reference_event_id'] == 'e3'
    assert result['load_kg'] == 40.0
    assert result['reported_rir'] is None


def test_evaluator_cannot_accept_imported_old_confirmations():
    from tools.science_initial_policy.admission_registry import load_admission_registry
    from tools.science_initial_policy.admission_system import evaluate_admission
    from tools.science_initial_policy.v2_producer import produce_v2
    from tools.science_initial_policy.v2_registry import load_v2_registry

    case = _v2_case()
    for ep in case['request']['episodes']:
        ep['started_at'] = '2026-11-06T11:10:00Z'
        for index, e in enumerate(ep['events'], 1):
            e['provenance']['measured_at'] = f'2026-11-06T11:0{index}:00Z'
            e['provenance']['recorded_at'] = f'2026-11-06T11:{10 + index}:00Z'
    bundle = load_v2_registry()
    result = evaluate_admission(case['request'], produce_v2(case['request'], bundle), bundle,
                                load_admission_registry())
    assert all(c['state'] == 'NEEDS_CALIBRATION' for c in result['calibration_by_context'].values())
    assert result['verdict'] == 'NOT_ADMITTED'
