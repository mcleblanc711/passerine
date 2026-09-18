"""Explicit unavailable boundary, not a guessed Quire schema or fake connection."""
def collect():
    raise RuntimeError('Quire requires OAuth registration, selected project scope, and a validated paginated task reader')
