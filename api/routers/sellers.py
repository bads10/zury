import os
import shutil
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.auth import create_access_token, get_current_seller, hash_password, verify_password
from api.database import get_db
from api.models.garment import Garment
from api.models.seller import Seller

MEDIA_DIR = "/app/media"

router = APIRouter(prefix="/api/v1/sellers", tags=["sellers"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class SellerRegisterIn(BaseModel):
    email: str
    password: str
    name: str
    slug: str
    location: str | None = None


class SellerOut(BaseModel):
    id: str
    email: str
    slug: str
    name: str
    location: str | None

    model_config = {"from_attributes": True}


class GarmentIn(BaseModel):
    name: str
    description: str | None = None
    category: str | None = None
    image_url: str | None = None
    meta: dict | None = None


# ── Auth ──────────────────────────────────────────────────────────────────────

@router.post("/register", status_code=201, response_model=SellerOut)
def register(body: SellerRegisterIn, db: Session = Depends(get_db)):
    if db.query(Seller).filter(Seller.email == body.email).first():
        raise HTTPException(status_code=409, detail="Email déjà utilisé")
    if db.query(Seller).filter(Seller.slug == body.slug).first():
        raise HTTPException(status_code=409, detail="Slug déjà utilisé")
    seller = Seller(
        email=body.email,
        hashed_password=hash_password(body.password),
        name=body.name,
        slug=body.slug,
        location=body.location,
    )
    db.add(seller)
    db.commit()
    db.refresh(seller)
    return seller


@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    seller = db.query(Seller).filter(Seller.email == form.username).first()
    if not seller or not verify_password(form.password, seller.hashed_password):
        raise HTTPException(status_code=401, detail="Identifiants invalides")
    return {"access_token": create_access_token(seller.id), "token_type": "bearer"}


@router.get("/me", response_model=SellerOut)
def me(seller: Seller = Depends(get_current_seller)):
    return seller


# ── Garment image upload ──────────────────────────────────────────────────────

@router.post("/me/garments/image")
async def upload_garment_image(
    file: UploadFile = File(...),
    _: Seller = Depends(get_current_seller),
):
    ext = os.path.splitext(file.filename or "img.jpg")[1] or ".jpg"
    filename = f"{uuid.uuid4()}{ext}"
    dest = os.path.join(MEDIA_DIR, filename)
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"image_url": f"/api/v1/media/{filename}"}


# ── Garments CRUD ─────────────────────────────────────────────────────────────

@router.post("/me/garments", status_code=201)
def create_garment(
    body: GarmentIn,
    seller: Seller = Depends(get_current_seller),
    db: Session = Depends(get_db),
):
    garment = Garment(
        seller_id=seller.id,
        seller_slug=seller.slug,
        name=body.name,
        description=body.description,
        category=body.category,
        image_url=body.image_url,
        meta=body.meta,
    )
    db.add(garment)
    db.commit()
    db.refresh(garment)
    return {"id": garment.id, "seller_slug": garment.seller_slug, "name": garment.name}


@router.put("/me/garments/{garment_id}")
def update_garment(
    garment_id: str,
    body: GarmentIn,
    seller: Seller = Depends(get_current_seller),
    db: Session = Depends(get_db),
):
    garment = db.query(Garment).filter(
        Garment.id == garment_id, Garment.seller_id == seller.id
    ).first()
    if not garment:
        raise HTTPException(status_code=404, detail="Vêtement introuvable")
    garment.name        = body.name
    garment.description = body.description
    garment.category    = body.category
    garment.meta        = body.meta
    if body.image_url is not None:
        garment.image_url = body.image_url
    db.commit()
    db.refresh(garment)
    return {
        "id": garment.id, "name": garment.name,
        "category": garment.category, "image_url": garment.image_url,
    }


@router.delete("/me/garments/{garment_id}", status_code=200)
def delete_garment(
    garment_id: str,
    seller: Seller = Depends(get_current_seller),
    db: Session = Depends(get_db),
):
    garment = db.query(Garment).filter(
        Garment.id == garment_id, Garment.seller_id == seller.id
    ).first()
    if not garment:
        raise HTTPException(status_code=404, detail="Vêtement introuvable")
    db.delete(garment)
    db.commit()
    return {"deleted": garment_id}


# ── Public catalogue ──────────────────────────────────────────────────────────

@router.get("/{slug}/garments")
def list_garments(slug: str, db: Session = Depends(get_db)):
    garments = db.query(Garment).filter(Garment.seller_slug == slug).all()
    return [
        {"id": g.id, "name": g.name, "category": g.category, "image_url": g.image_url}
        for g in garments
    ]


@router.get("/{slug}/garment/{garment_id}")
def get_garment(slug: str, garment_id: str, db: Session = Depends(get_db)):
    garment = (
        db.query(Garment)
        .filter(Garment.seller_slug == slug, Garment.id == garment_id)
        .first()
    )
    if not garment:
        raise HTTPException(status_code=404, detail="Garment not found")
    return {
        "id":          garment.id,
        "seller_id":   garment.seller_id,
        "seller_slug": garment.seller_slug,
        "name":        garment.name,
        "description": garment.description,
        "category":    garment.category,
        "image_url":   garment.image_url,
        "meta":        garment.meta,
    }
