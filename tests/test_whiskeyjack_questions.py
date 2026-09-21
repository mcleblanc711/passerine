"""Selected-field fixtures mirror validated WJ ForecastRecord attributes at 9e9fcfe."""
from datetime import datetime, timezone, timedelta
from types import SimpleNamespace as Row

import pytest

from app.adapters.whiskeyjack_questions import project_question


def record(kind, prediction, **question_fields):
    return Row(
        question_type=kind, forecast_version=2,
        generated_at_utc=datetime(2026, 9, 18, 4, tzinfo=timezone(timedelta(hours=-6))),
        question=Row(title='Will the synthetic mission launch?', group_parent_title='Synthetic launch schedule',
                     background_info='<script>not executable</script>', resolution_criteria='Official launch report.',
                     fine_print=None, unit_of_measure=None, **question_fields),
        forecast=Row(final_prediction=prediction, as_of_utc=datetime(2026, 9, 17, tzinfo=timezone.utc),
                     rationale_summary='PRIVATE RATIONALE'),
        community_prediction=Row(snapshot=None, snapshot_at_utc=None, used_as_model_input=False),
        model_settings='PRIVATE MODEL SETTINGS', sources='PRIVATE RESEARCH',
    )


@pytest.mark.parametrize('probability', [0, 0.725, 1])
def test_binary_keeps_probabilities_and_forecast_time_separate(probability):
    source = record('binary', Row(probability_yes=probability))
    result = project_question(source)
    assert result['forecast']['rows'] == [dict(label='Yes', value=probability), dict(label='No', value=1-probability)]
    assert result['forecast']['generated_at'] == '2026-09-18T10:00:00+00:00'
    assert result['forecast']['as_of'] == '2026-09-17T00:00:00+00:00'
    assert result['forecast']['version'] == 2
    assert result['community']['status'] == 'unavailable'
    assert result['community']['observed_at'] is None
    assert 'PRIVATE' not in str(result)
    assert 'status' not in result['forecast']  # Generated data is not submission evidence.
    assert result['group_title'] == 'Synthetic launch schedule'
    assert result['question_details']['background'] == '<script>not executable</script>'


def test_multiple_choice_matches_labels_in_question_order():
    source = record('multiple_choice', Row(options=[Row(option='B', probability=.8), Row(option='A', probability=.2)]), options=['A', 'B'])
    assert project_question(source)['forecast']['rows'] == [dict(label='A', value=.2), dict(label='B', value=.8)]


@pytest.mark.parametrize('kind', ['numeric', 'discrete'])
def test_percentiles_are_values_not_probabilities_or_invented_medians(kind):
    source = record(kind, Row(percentiles=[Row(percentile=.9, value=120), Row(percentile=.1, value=-5)]))
    source.question.unit_of_measure = 'units'
    result = project_question(source)
    assert result['forecast']['kind'] == kind
    assert result['forecast']['unit'] == 'units'
    assert result['forecast']['rows'] == [dict(label='10th percentile', value=-5), dict(label='90th percentile', value=120)]


def test_unsupported_type_fails_instead_of_inventing_display():
    with pytest.raises(ValueError, match='Unsupported recorded forecast type'):
        project_question(record('unknown', Row()))
