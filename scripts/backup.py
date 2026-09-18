"""Back up only a Passerine database via SQLite's consistent backup API."""
import sqlite3, sys
from pathlib import Path
source, target = map(Path, sys.argv[1:])
if target.exists(): raise SystemExit('Destination already exists; choose a new backup path')
with sqlite3.connect(source.resolve().as_uri()+'?mode=ro',uri=True) as src:
    if not src.execute("SELECT 1 FROM sqlite_master WHERE name='sources'").fetchone():
        raise SystemExit('Not a Passerine database')
    with sqlite3.connect(target) as dst: src.backup(dst)
