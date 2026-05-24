"""Pytest fixtures for the Zury API.

Strategy:
- Set env vars (MEDIA_DIR, UPLOAD_DIR, DATABASE_URL, CELERY_TASK_ALWAYS_EAGER)
  BEFORE importing any api.* module, so module-level constants pick them up.
- SQLite tempfile DB per test session, schema via Base.metadata.create_all
  (we test alembic migrations separately in CI against real Postgres).
- Celery runs eagerly in-process, no broker needed.
- No REPLICATE_API_TOKEN => generate_tryon uses the placeholder branch.
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest


# ── Env setup BEFORE any api.* import ─────────────────────────────────────────

_TMP = Path(tempfile.mkdtemp(prefix="zury-tests-"))
(_TMP / "media").mkdir()
(_TMP / "uploads").mkdir()
_DB_PATH = _TMP / "test.db"

os.environ["MEDIA_DIR"] = str(_TMP / "media")
os.environ["UPLOAD_DIR"] = str(_TMP / "uploads")
os.environ["DATABASE_URL"] = f"sqlite:///{_DB_PATH}"
os.environ["CELERY_TASK_ALWAYS_EAGER"] = "true"
os.environ.pop("REPLICATE_API_TOKEN", None)
os.environ.setdefault("SECRET_KEY", "test-secret")


# ── Imports (after env setup) ─────────────────────────────────────────────────

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from api.database import Base, get_db  # noqa: E402
from api.main import app  # noqa: E402
from api.workers.tasks import celery_app  # noqa: E402

# Force Celery into eager mode for the test process.
celery_app.conf.task_always_eager = True
celery_app.conf.task_eager_propagates = True

# Single shared sqlite engine (file-backed so Celery worker sees the same DB).
_engine = create_engine(
    f"sqlite:///{_DB_PATH}", connect_args={"check_same_thread": False}
)
_TestingSessionLocal = sessionmaker(bind=_engine, autocommit=False, autoflush=False)


def _override_get_db():
    db = _TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _override_get_db

# Patch the SessionLocal used by Celery tasks to point at the same sqlite DB.
import api.database as _db_mod  # noqa: E402

_db_mod.SessionLocal = _TestingSessionLocal
_db_mod.engine = _engine


@pytest.fixture(scope="session", autouse=True)
def _create_schema():
    # Import all model modules so they register on Base.metadata.
    import api.models.garment  # noqa: F401
    import api.models.job  # noqa: F401
    import api.models.seller  # noqa: F401

    Base.metadata.create_all(bind=_engine)
    yield
    Base.metadata.drop_all(bind=_engine)


@pytest.fixture(autouse=True)
def _clean_tables():
    """Truncate all tables between tests so each test starts clean."""
    yield
    with _engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def registered_seller(client):
    """Register a fresh seller and return its login token + payload."""
    payload = {
        "email": "test@zury.test",
        "password": "hunter2hunter2",
        "name": "Test Boutique",
        "slug": "test-boutique",
        "location": "Abidjan",
    }
    r = client.post("/api/v1/sellers/register", json=payload)
    assert r.status_code == 201, r.text
    seller = r.json()

    r = client.post(
        "/api/v1/sellers/login",
        data={"username": payload["email"], "password": payload["password"]},
    )
    assert r.status_code == 200, r.text
    token = r.json()["access_token"]
    return {"seller": seller, "token": token, "auth": {"Authorization": f"Bearer {token}"}}
