"""Production entrypoint serving the API and compiled React app together."""
import os
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from main import app

frontend_dist = Path(os.getenv('FRONTEND_DIST', str(Path(__file__).resolve().parent.parent / 'frontend' / 'dist')))
if not (frontend_dist / 'index.html').is_file():
    raise RuntimeError('Frontend build missing. Run npm ci && npm run build in frontend first.')

# API routes are registered first, so /api requests reach FastAPI.
app.mount('/', StaticFiles(directory=str(frontend_dist), html=True), name='frontend')
