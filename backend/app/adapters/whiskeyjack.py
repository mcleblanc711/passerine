import os, subprocess, json, hashlib
from pathlib import Path
from app.models import Observation

def collect():
    root = Path(os.environ['PASSERINE_WJ_ROOT']).resolve()
    python = os.environ.get('PASSERINE_WJ_PYTHON', str(root / '.venv/bin/python'))
    reader = Path(__file__).resolve().parents[3] / 'scripts/read_whiskeyjack.py'
    env = dict(os.environ, PYTHONPATH=str(root / 'src'), PYTHONDONTWRITEBYTECODE='1')
    result = subprocess.run([python, str(reader), os.environ['PASSERINE_WJ_DB']], env=env, capture_output=True, timeout=45)
    if result.returncode:
        raise ValueError('Whiskey Jack reader incompatible or unavailable')
    data = json.loads(result.stdout)
    return Observation(source_id='whiskeyjack', instance_id='minibench:' + hashlib.sha256(str(Path(os.environ['PASSERINE_WJ_DB']).resolve()).encode()).hexdigest()[:16], origin='real', source_observed_at=data.pop('source_observed_at'), provenance='Matching checkout connect_readonly + assemble_show; MiniBench namespace', coverage='Full recorded MiniBench history; official platform scores unavailable. Resolution ingestion scheduled every six hours. Cup excluded (withdrawn).', events=data.pop('events'), data=data)
