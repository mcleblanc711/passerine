"""Pure selection of current evidence; dates and lifecycle never imply outcomes."""
def current_resolution(resolutions, scores):
    latest = max(resolutions, key=lambda r: (r.observed_at_utc, r.event_id), default=None)
    current = [s for s in scores if latest and latest.scorable and latest.kind == 'resolved' and s.resolution_event_id == latest.event_id]
    return latest, current
