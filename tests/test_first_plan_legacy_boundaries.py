"""A scientific profile must not acquire legacy success or logging confidence."""
from types import SimpleNamespace as NS

import pytest


def profile():
    s=NS(template_slug_snapshot='science:v3:first-session',template=None,status='completed',
        session_exercises=[],scoring_version=1,concentration=None,global_state=None)
    se=NS(session=s,template_exercise=None,success_score=None,implicit_label=None,
        set_logs=[],exercise_code_snapshot='sci-v3-1')
    se.set_logs=[NS(session_exercise=se,kind='work',completed=True,set_index=i,
        reps=10,weight_kg=None) for i in range(1,4)]
    s.session_exercises=[se]
    return s,se


def test_no_default_success_confidence_or_implicit_label():
    from app.services.confidence import compute_confidence_score
    from app.services.feedback import compute_success_score
    from app.services.implicit_signal import detect_intra_set_label
    from app.services.quality_score import compute_session_quality
    from app.services.stats import summarise_current_exercise
    s,se=profile()
    assert compute_success_score(se,None) is None
    assert detect_intra_set_label(se.set_logs) is None
    assert compute_session_quality(s) is None
    assert compute_confidence_score(s) is None
    assert summarise_current_exercise(se) is None


def test_legacy_recap_refuses_inapplicable_profile_before_computing():
    from app.services.plan_v3.transactions import RuntimeFailure
    from app.services.session_recap import build_recap
    s,_=profile()
    with pytest.raises(RuntimeFailure,match='execution_profile_required'):
        build_recap(s)
