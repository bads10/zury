import io
import os
import time
from datetime import datetime, timezone

import httpx
import replicate
from celery import Celery
from PIL import Image, ImageDraw

BROKER_URL     = os.getenv("CELERY_BROKER_URL",    "redis://localhost:6379/0")
RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

MEDIA_DIR = os.getenv("MEDIA_DIR", "/app/media")

celery_app = Celery("zury", broker=BROKER_URL, backend=RESULT_BACKEND)
os.makedirs(MEDIA_DIR, exist_ok=True)


# ── Modèles try-on disponibles ────────────────────────────────────────────────
# Sélection via TRYON_MODEL (env). Chaque entrée : ref Replicate + builder
# d'inputs, car les schémas d'entrée diffèrent d'un modèle à l'autre.

def _idm_vton_input(human_buf: io.BytesIO, garm_buf: io.BytesIO, garment_des: str) -> dict:
    return {
        "human_img":   human_buf,
        "garm_img":    garm_buf,
        "garment_des": garment_des,
        "crop":        False,
        "steps":       30,
        "seed":        42,
    }


def _nano_banana_input(human_buf: io.BytesIO, garm_buf: io.BytesIO, garment_des: str) -> dict:
    return {
        "prompt": (
            "Make the person in the first image wear the garment from the second image. "
            "Keep the person's face, body shape, skin tone and pose exactly as they are. "
            "Reproduce the garment's pattern, colors, trim and texture faithfully — do not "
            f"reinterpret or simplify the print. Photorealistic. Garment: {garment_des}"
        ),
        "image_input":   [human_buf, garm_buf],
        "output_format": "png",
    }


TRYON_MODELS = {
    "idm-vton": {
        "ref":   "cuuupid/idm-vton:0513734a452173b8173e907e3a59d19a36266e55b48528559432bd21c7d7e985",
        "input": _idm_vton_input,
    },
    "nano-banana": {
        "ref":   "google/nano-banana",
        "input": _nano_banana_input,
    },
}

TRYON_MODEL = os.getenv("TRYON_MODEL", "nano-banana")

# nano-banana échoue parfois de façon stochastique : renvoie le selfie inchangé
# (no-op) ou compose un diptyque au lieu d'éditer. Seuils calibrés sur l'éval
# du 2026-07-03 : no-op diff ≤ 7,6 vs ≥ 9,5 pour les vrais résultats ;
# diptyque ratio 1,76 vs ≤ 1,21 pour les vrais résultats.
NOOP_DIFF_THRESHOLD = 8.5
DIPTYCH_AR_THRESHOLD = 1.45
MAX_GENERATION_TRIES = 2


def _detect_anomaly(result_bytes: bytes, selfie_path: str) -> str | None:
    """Retourne "no-op", "diptyque" ou None si le résultat semble valide."""
    res = Image.open(io.BytesIO(result_bytes)).convert("L")
    ref = Image.open(selfie_path).convert("L")

    ar_ratio = (res.width / res.height) / (ref.width / ref.height)
    if ar_ratio > DIPTYCH_AR_THRESHOLD:
        return "diptyque"

    a = list(res.resize((64, 64)).getdata())
    b = list(ref.resize((64, 64)).getdata())
    mean_a, mean_b = sum(a) / len(a), sum(b) / len(b)
    # diff moyenne recentrée : insensible à un simple décalage de luminosité
    diff = sum(abs((x - mean_a) - (y - mean_b)) for x, y in zip(a, b)) / len(a)
    if diff < NOOP_DIFF_THRESHOLD:
        return "no-op"
    return None


# ── DB helper ─────────────────────────────────────────────────────────────────

def _update_job(job_id: str, **fields) -> None:
    from api.database import SessionLocal
    from api.models.job import Job

    db = SessionLocal()
    try:
        job = db.get(Job, job_id)
        if job:
            for k, v in fields.items():
                setattr(job, k, v)
            job.updated_at = datetime.now(timezone.utc)
            db.commit()
    finally:
        db.close()


# ── Image helpers ─────────────────────────────────────────────────────────────

def _file_to_bytesio(path: str) -> io.BytesIO:
    with open(path, "rb") as f:
        buf = io.BytesIO(f.read())
    buf.name = os.path.basename(path)
    return buf


def _garment_data(garment_id: str) -> tuple[io.BytesIO, str]:
    """Return (image BytesIO, garment_name)."""
    from api.database import SessionLocal
    from api.models.garment import Garment

    db = SessionLocal()
    try:
        g = db.get(Garment, garment_id)
        if not g:
            raise ValueError(f"Garment {garment_id} not found")
        name      = g.name or "garment"
        image_url = g.image_url or ""
    finally:
        db.close()

    if image_url.startswith("/api/v1/media/"):
        filename = image_url.removeprefix("/api/v1/media/")
        buf = _file_to_bytesio(os.path.join(MEDIA_DIR, filename))
        return buf, name

    if image_url:
        r = httpx.get(image_url, follow_redirects=True, timeout=30)
        r.raise_for_status()
        ext = image_url.rsplit(".", 1)[-1].split("?")[0].lower() or "jpg"
        buf = io.BytesIO(r.content)
        buf.name = f"garment.{ext}"
        return buf, name

    raise ValueError(f"Garment {garment_id} has no image")


# ── Celery task ───────────────────────────────────────────────────────────────

@celery_app.task(name="generate_tryon")
def generate_tryon(job_id: str, selfie_path: str, garment_id: str, fitzpatrick: int) -> dict:
    from api.models.job import JobStatus

    _update_job(job_id, status=JobStatus.processing, progress=10)

    if not os.getenv("REPLICATE_API_TOKEN"):
        return _placeholder(job_id, garment_id, fitzpatrick)

    model_key = TRYON_MODEL
    model = TRYON_MODELS.get(model_key)
    if model is None:
        _update_job(
            job_id, status=JobStatus.failed, progress=0,
            error=f"TRYON_MODEL inconnu : {model_key!r} (disponibles : {sorted(TRYON_MODELS)})",
        )
        raise ValueError(f"Unknown TRYON_MODEL {model_key!r}")

    _update_job(job_id, model=model_key)

    try:
        garm_bytes, garment_des = None, None
        anomaly = None
        content = b""

        for attempt in range(1, MAX_GENERATION_TRIES + 1):
            # Upload images as file objects — replicate SDK auto-uploads to its
            # file storage so Replicate's inference servers can fetch them.
            # Buffers reconstruits à chaque tentative (consommés par l'upload).
            human_buf = _file_to_bytesio(selfie_path)
            if garm_bytes is None:
                garm_buf, garment_des = _garment_data(garment_id)
                garm_bytes, garm_name = garm_buf.getvalue(), garm_buf.name
            else:
                garm_buf = io.BytesIO(garm_bytes)
                garm_buf.name = garm_name
            _update_job(job_id, progress=20)

            output = replicate.run(model["ref"], input=model["input"](human_buf, garm_buf, garment_des))
            _update_job(job_id, progress=80)

            # output is a list of FileOutput objects or plain URL strings
            output_item = output[0] if isinstance(output, list) else output
            url_str = getattr(output_item, "url", str(output_item))

            r = httpx.get(url_str, follow_redirects=True, timeout=60)
            r.raise_for_status()
            content = r.content

            anomaly = _detect_anomaly(content, selfie_path)
            if anomaly is None:
                break

        if anomaly is not None:
            _update_job(
                job_id, status=JobStatus.failed, progress=0,
                error=f"résultat invalide ({anomaly}) après {MAX_GENERATION_TRIES} tentatives",
            )
            raise ValueError(
                f"résultat invalide ({anomaly}) après {MAX_GENERATION_TRIES} tentatives"
            )

        _update_job(job_id, progress=95)
        out_path = os.path.join(MEDIA_DIR, f"{job_id}_result.png")
        with open(out_path, "wb") as f:
            f.write(content)

        result_url = f"/api/v1/media/{job_id}_result.png"
        _update_job(job_id, status=JobStatus.done, progress=100, result_url=result_url)
        return {"result_url": result_url, "job_id": job_id}

    except Exception as exc:
        _update_job(job_id, status=JobStatus.failed, progress=0, error=str(exc)[:500])
        raise


# ── Placeholder (no token) ────────────────────────────────────────────────────

def _placeholder(job_id: str, garment_id: str, fitzpatrick: int) -> dict:
    from api.models.job import JobStatus

    _update_job(job_id, model="placeholder")
    time.sleep(2)
    _update_job(job_id, progress=50)
    time.sleep(2)
    _update_job(job_id, progress=90)

    img  = Image.new("RGB", (512, 768), color=(18, 18, 18))
    draw = ImageDraw.Draw(img)
    draw.rectangle([12, 12, 500, 756], outline=(55, 55, 55), width=2)
    draw.text((24, 360), "SET REPLICATE_API_TOKEN",         fill=(170, 170, 170))
    draw.text((24, 382), "to enable real try-ons",          fill=(100, 100, 100))
    draw.text((24, 410), f"garment    : {garment_id[:22]}", fill=(80, 80, 80))
    draw.text((24, 428), f"fitzpatrick: {fitzpatrick}",     fill=(80, 80, 80))

    out_path   = os.path.join(MEDIA_DIR, f"{job_id}.png")
    img.save(out_path, format="PNG")

    result_url = f"/api/v1/media/{job_id}.png"
    _update_job(job_id, status=JobStatus.done, progress=100, result_url=result_url)
    return {"result_url": result_url, "job_id": job_id}
