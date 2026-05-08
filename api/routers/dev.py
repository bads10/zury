import os
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.auth import hash_password
from api.database import get_db
from api.models.garment import Garment
from api.models.seller import Seller

router = APIRouter(prefix="/dev", tags=["dev"])

_DEMO_SELLER = {
    "id":       "seller-demo-001",
    "email":    "demo@zury.africa",
    "password": "zury2025",
    "slug":     "maison-adjoua",
    "name":     "Maison Adjoua",
}

_DEMO_GARMENT = {
    "id":          "garment-demo-001",
    "seller_id":   "seller-demo-001",
    "seller_slug": "maison-adjoua",
    "name":        "Robe Safran",
    "description": "Robe mi-longue en wax imprimé, coupe évasée, manches 3/4",
    "category":    "robe",
    "image_url":   "https://picsum.photos/seed/robe-safran/480/720",
    "meta": {
        "order_url": "https://wa.me/33600000000?text=Je%20veux%20commander%20la%20Robe%20Safran"
    },
}


@router.post("/seed/seller", status_code=200)
def seed_demo_seller(db: Session = Depends(get_db)):
    s = db.get(Seller, _DEMO_SELLER["id"])
    if s is None:
        s = Seller(
            id=_DEMO_SELLER["id"],
            email=_DEMO_SELLER["email"],
            hashed_password=hash_password(_DEMO_SELLER["password"]),
            slug=_DEMO_SELLER["slug"],
            name=_DEMO_SELLER["name"],
            created_at=datetime.now(timezone.utc),
        )
        db.add(s)
    db.commit()
    db.refresh(s)
    return {
        "seeded": True,
        "seller_id": s.id,
        "slug": s.slug,
        "login_hint": {"email": _DEMO_SELLER["email"], "password": _DEMO_SELLER["password"]},
    }


def _ensure_demo_image() -> str:
    """Download demo image once into /app/media and return its local URL."""
    import requests as _req
    local_path = "/app/media/garment-demo-001.jpg"
    if not os.path.exists(local_path):
        try:
            r = _req.get(
                _DEMO_GARMENT["image_url"],
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=15,
                allow_redirects=True,
            )
            r.raise_for_status()
            with open(local_path, "wb") as f:
                f.write(r.content)
        except Exception:
            return _DEMO_GARMENT["image_url"]
    return "/api/v1/media/garment-demo-001.jpg"


@router.post("/seed", status_code=200)
def seed_demo(db: Session = Depends(get_db)):
    image_url = _ensure_demo_image()
    g = db.get(Garment, _DEMO_GARMENT["id"])
    if g is None:
        g = Garment(
            id=_DEMO_GARMENT["id"],
            seller_id=_DEMO_GARMENT["seller_id"],
            seller_slug=_DEMO_GARMENT["seller_slug"],
            name=_DEMO_GARMENT["name"],
            description=_DEMO_GARMENT["description"],
            category=_DEMO_GARMENT["category"],
            image_url=image_url,
            meta=_DEMO_GARMENT["meta"],
            created_at=datetime.now(timezone.utc),
        )
        db.add(g)
    else:
        g.seller_id   = _DEMO_GARMENT["seller_id"]
        g.seller_slug = _DEMO_GARMENT["seller_slug"]
        g.image_url   = image_url
        g.meta        = _DEMO_GARMENT["meta"]
    db.commit()
    db.refresh(g)
    return {
        "seeded": True,
        "garment_id": g.id,
        "image_url": g.image_url,
        "pwa_url": f"/?seller={g.seller_slug}&garment={g.id}",
    }
