FROM node:22-slim AS frontend
WORKDIR /build
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir --require-hashes -r requirements.txt
COPY backend/ backend/
COPY scripts/read_whiskeyjack.py scripts/read_whiskeyjack.py
COPY --from=frontend /build/dist frontend/dist
ENV PYTHONPATH=/app/backend
RUN useradd --uid 10001 --create-home passerine && mkdir /app/runtime && chown passerine /app/runtime
USER passerine
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]
