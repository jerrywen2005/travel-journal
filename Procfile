proxy: caddy run
backend: alembic upgrade head && uvicorn backend.app.main:app --reload --port=1561
frontend: cd frontend && npm run start -- --port 1562