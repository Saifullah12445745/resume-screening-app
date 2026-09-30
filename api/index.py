"""Vercel ASGI entrypoint; route /api/* here."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))
from main import app
