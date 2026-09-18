import os, secrets, hashlib, time, json
from pathlib import Path
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from app import store

@asynccontextmanager
async def lifespan(app):
    if len(os.environ.get('PASSERINE_PASSWORD', '')) < 12:
        raise RuntimeError('Set PASSERINE_PASSWORD to at least 12 characters')
    store.init()
    yield

app = FastAPI(title='Passerine', version='1.0', lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)
login_attempts = {}

@app.middleware('http')
async def headers(request, call_next):
    response = await call_next(request)
    response.headers['Cache-Control'] = 'no-store' if request.url.path.startswith('/api') else 'no-cache'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'no-referrer'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
    return response

def origin(request):
    expected = os.environ.get('PASSERINE_ORIGIN', 'http://127.0.0.1:8000')
    if request.headers.get('origin') != expected: raise HTTPException(403,'Origin rejected')

def session(request: Request):
    token = hashlib.sha256(request.cookies.get('passerine','').encode()).hexdigest()
    with store.db() as c:
        row = c.execute('SELECT * FROM sessions WHERE token=? AND expires>?', (token,time.time())).fetchone()
    if not row: raise HTTPException(401,'Sign in required')
    if request.method != 'GET':
        origin(request)
        if not secrets.compare_digest(request.headers.get('x-csrf-token',''), row['csrf']): raise HTTPException(403,'CSRF rejected')
    return dict(row)

class Login(BaseModel): password: str

@app.post('/api/login')
def login(body: Login, request: Request, response: Response):
    origin(request)
    key = request.client.host
    tries = [t for t in login_attempts.get(key,[]) if t > time.time()-300]
    if len(tries)>=10: raise HTTPException(429,'Try again in five minutes')
    login_attempts[key] = tries + [time.time()]
    if not secrets.compare_digest(body.password,os.environ['PASSERINE_PASSWORD']): raise HTTPException(401,'Incorrect password')
    token, csrf = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
    with store.db() as c:
        c.execute('DELETE FROM sessions WHERE expires<?',(time.time(),))
        c.execute('INSERT INTO sessions VALUES (?,?,?)',(hashlib.sha256(token.encode()).hexdigest(),csrf,time.time()+43200))
    response.set_cookie('passerine',token,httponly=True,secure=os.environ.get('PASSERINE_SECURE_COOKIE')=='1',samesite='strict',max_age=43200)
    return {'csrf':csrf}

@app.get('/api/session')
def get_session(s=Depends(session)): return {'csrf':s['csrf']}

@app.post('/api/logout')
def logout(response: Response, s=Depends(session)):
    with store.db() as c: c.execute('DELETE FROM sessions WHERE token=?',(s['token'],))
    response.delete_cookie('passerine')
    return {'ok':True}

@app.get('/api/overview')
def overview(s=Depends(session)):
    with store.db() as c:
        sources = []
        for row in c.execute('SELECT * FROM sources'):
            item = dict(row)
            item['observation'] = json.loads(item.pop('payload')) if row['payload'] else None
            item['connection'] = 'failed' if row['error'] else 'connected' if row['payload'] else 'not configured'
            item['cache_stale'] = not row['collected_at'] or (datetime.now(timezone.utc)-datetime.fromisoformat(row['collected_at'])).total_seconds()>180
            sources.append(item)
        heartbeat = c.execute("SELECT value FROM meta WHERE key='worker_heartbeat'").fetchone()
        beat = heartbeat[0] if heartbeat else None
        alive = beat is not None and (datetime.now(timezone.utc)-datetime.fromisoformat(beat)).total_seconds()<120
        return dict(version=1,sources=sources,events=[dict(r) for r in c.execute('SELECT * FROM events ORDER BY at DESC LIMIT 150')],incidents=[dict(r) for r in c.execute('SELECT * FROM incidents ORDER BY opened_at DESC LIMIT 100')],outbox=[dict(r) for r in c.execute('SELECT * FROM outbox ORDER BY created_at DESC LIMIT 50')],worker=dict(alive=alive,heartbeat=beat),timezone='America/Edmonton')

@app.post('/api/ack/{identity:path}')
def ack(identity: str, s=Depends(session)):
    with store.db() as c:
        result=c.execute('UPDATE incidents SET acknowledged_at=? WHERE id=?',(store.now(),identity))
        if not result.rowcount: raise HTTPException(404,'Incident not found')
    return {'ok':True}

@app.post('/api/refresh')
def refresh(s=Depends(session)):
    # Worker remains sole collector; deliberately respect persisted source cooldowns.
    with store.db() as c:
        c.execute('INSERT OR REPLACE INTO meta VALUES (?,?)', ('refresh_requested_at',store.now()))
    return {'message':'Refresh noted. Collection runs automatically. The next scheduled check respects source cooldowns.'}

frontend = Path(__file__).resolve().parents[2] / 'frontend/dist'
if frontend.exists(): app.mount('/',StaticFiles(directory=frontend,html=True),name='frontend')
