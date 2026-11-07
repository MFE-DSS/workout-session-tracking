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
