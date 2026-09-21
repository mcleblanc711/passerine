"""Small display projection of a source-validated ForecastRecord (WJ 9e9fcfe).

The source read_forecast_record checks the stored hash, schema and scalar identity.
Never send record_json, model inputs, research or raw API responses to the browser.
"""
from datetime import timezone


def project_question(record):
    question = record.question
    prediction = record.forecast.final_prediction
    if record.question_type == 'binary':
        rows = [dict(label='Yes', value=prediction.probability_yes),
                dict(label='No', value=1 - prediction.probability_yes)]
    elif record.question_type == 'multiple_choice':
        probabilities = {item.option: item.probability for item in prediction.options}
        # Preserve the question's option order, not model output order.
        rows = [dict(label=option, value=probabilities[option]) for option in question.options]
    elif record.question_type in ('numeric', 'discrete'):
        rows = [dict(label=f'{point.percentile * 100:g}th percentile', value=point.value)
                for point in sorted(prediction.percentiles, key=lambda p: p.percentile)]
    else:
        raise ValueError('Unsupported recorded forecast type')
    return dict(
        title=question.title,
        group_title=question.group_parent_title,
        question_details=dict(background=question.background_info,
                              resolution_criteria=question.resolution_criteria,
                              fine_print=question.fine_print),
        forecast=dict(
            version=record.forecast_version,
            generated_at=record.generated_at_utc.astimezone(timezone.utc).isoformat(),
            as_of=record.forecast.as_of_utc.astimezone(timezone.utc).isoformat(),
            kind=record.question_type,
            unit=question.unit_of_measure,
            rows=rows,
        ),
        community=dict(status='unavailable', observed_at=None,
                       reason='Community predictions are not available in the saved forecast record. No live community lookup is configured.'),
    )
