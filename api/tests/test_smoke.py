"""Smoke tests for the Zury API golden path.

Covers: health, seller register/login/me, garment CRUD, public catalogue,
try-on submission + polling. With no REPLICATE_API_TOKEN set, the worker
runs the placeholder branch synchronously (CELERY_TASK_ALWAYS_EAGER=true),
so a polled job reaches `done` before the request returns.
"""
from __future__ import annotations

import io

from PIL import Image


def _png_bytes() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (32, 32), (200, 100, 50)).save(buf, format="PNG")
    return buf.getvalue()


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_register_then_login(client):
    payload = {
        "email": "alice@zury.test",
        "password": "longpasswordok",
        "name": "Alice Couture",
        "slug": "alice-couture",
    }
    r = client.post("/api/v1/sellers/register", json=payload)
    assert r.status_code == 201, r.text
    assert r.json()["slug"] == "alice-couture"

    r = client.post(
        "/api/v1/sellers/login",
        data={"username": payload["email"], "password": payload["password"]},
    )
    assert r.status_code == 200, r.text
    assert r.json()["token_type"] == "bearer"
    assert r.json()["access_token"]


def test_register_rejects_duplicate_email(client, registered_seller):
    r = client.post(
        "/api/v1/sellers/register",
        json={
            "email": registered_seller["seller"]["email"],
            "password": "anotherpassword",
            "name": "Other",
            "slug": "other-slug",
        },
    )
    assert r.status_code == 409


def test_login_rejects_bad_password(client, registered_seller):
    r = client.post(
        "/api/v1/sellers/login",
        data={"username": registered_seller["seller"]["email"], "password": "wrong"},
    )
    assert r.status_code == 401


def test_me_requires_auth(client):
    assert client.get("/api/v1/sellers/me").status_code == 401


def test_me_returns_seller(client, registered_seller):
    r = client.get("/api/v1/sellers/me", headers=registered_seller["auth"])
    assert r.status_code == 200
    assert r.json()["slug"] == registered_seller["seller"]["slug"]


def test_garment_crud_and_public_listing(client, registered_seller):
    auth = registered_seller["auth"]
    slug = registered_seller["seller"]["slug"]

    # Create
    r = client.post(
        "/api/v1/sellers/me/garments",
        json={"name": "Boubou doré", "category": "boubou", "image_url": "/x.jpg"},
        headers=auth,
    )
    assert r.status_code == 201, r.text
    garment_id = r.json()["id"]

    # Update
    r = client.put(
        f"/api/v1/sellers/me/garments/{garment_id}",
        json={"name": "Boubou doré v2", "category": "boubou"},
        headers=auth,
    )
    assert r.status_code == 200
    assert r.json()["name"] == "Boubou doré v2"
    # image_url not passed => preserved (PUT semantics from a26fb75)
    assert r.json()["image_url"] == "/x.jpg"

    # Public listing
    r = client.get(f"/api/v1/sellers/{slug}/garments")
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1
    assert items[0]["id"] == garment_id

    # Public single
    r = client.get(f"/api/v1/sellers/{slug}/garment/{garment_id}")
    assert r.status_code == 200
    assert r.json()["name"] == "Boubou doré v2"

    # Delete
    r = client.delete(f"/api/v1/sellers/me/garments/{garment_id}", headers=auth)
    assert r.status_code == 200

    r = client.get(f"/api/v1/sellers/{slug}/garments")
    assert r.json() == []


def test_garment_image_upload(client, registered_seller):
    r = client.post(
        "/api/v1/sellers/me/garments/image",
        files={"file": ("g.png", _png_bytes(), "image/png")},
        headers=registered_seller["auth"],
    )
    assert r.status_code == 200
    assert r.json()["image_url"].startswith("/api/v1/media/")


def test_tryon_flow_end_to_end(client, registered_seller):
    auth = registered_seller["auth"]
    seller_id = registered_seller["seller"]["id"]

    # Need a garment with a real image so the worker can read it.
    upload = client.post(
        "/api/v1/sellers/me/garments/image",
        files={"file": ("g.png", _png_bytes(), "image/png")},
        headers=auth,
    ).json()
    garment_id = client.post(
        "/api/v1/sellers/me/garments",
        json={"name": "Test", "image_url": upload["image_url"]},
        headers=auth,
    ).json()["id"]

    # Submit try-on. CELERY_TASK_ALWAYS_EAGER means the task runs inline.
    r = client.post(
        "/api/v1/tryon",
        files={"selfie": ("s.png", _png_bytes(), "image/png")},
        data={"garment_id": garment_id, "seller_id": seller_id, "fitzpatrick": "4"},
    )
    assert r.status_code == 202, r.text
    job_id = r.json()["job_id"]

    # Poll — placeholder finishes synchronously so this is already done.
    r = client.get(f"/api/v1/tryon/{job_id}")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "done"
    assert body["progress"] == 100
    assert body["result_url"].startswith("/api/v1/media/")


def test_tryon_unknown_job_returns_404(client):
    assert client.get("/api/v1/tryon/does-not-exist").status_code == 404


def test_tryon_records_consent_and_model(client, registered_seller):
    import api.database as db_mod
    from api.models.job import Job

    r = client.post(
        "/api/v1/tryon",
        files={"selfie": ("s.png", _png_bytes(), "image/png")},
        data={
            "garment_id": "any-garment",
            "seller_id": registered_seller["seller"]["id"],
            "fitzpatrick": "5",
            "consent": "true",
        },
    )
    assert r.status_code == 202, r.text
    job_id = r.json()["job_id"]

    db = db_mod.SessionLocal()
    try:
        job = db.get(Job, job_id)
        assert job.consent is True
        # Sans REPLICATE_API_TOKEN, la branche placeholder tague le modèle.
        assert job.model == "placeholder"
    finally:
        db.close()

    # Le polling expose le champ error (None quand tout va bien).
    body = client.get(f"/api/v1/tryon/{job_id}").json()
    assert body["error"] is None


def test_tryon_consent_defaults_to_false(client, registered_seller):
    import api.database as db_mod
    from api.models.job import Job

    r = client.post(
        "/api/v1/tryon",
        files={"selfie": ("s.png", _png_bytes(), "image/png")},
        data={
            "garment_id": "any-garment",
            "seller_id": registered_seller["seller"]["id"],
            "fitzpatrick": "4",
        },
    )
    assert r.status_code == 202, r.text

    db = db_mod.SessionLocal()
    try:
        job = db.get(Job, r.json()["job_id"])
        assert job.consent is False
    finally:
        db.close()


def test_tryon_rejects_invalid_fitzpatrick(client, registered_seller):
    r = client.post(
        "/api/v1/tryon",
        files={"selfie": ("s.png", _png_bytes(), "image/png")},
        data={
            "garment_id": "g",
            "seller_id": registered_seller["seller"]["id"],
            "fitzpatrick": "9",  # out of range 1..6
        },
    )
    assert r.status_code == 422
