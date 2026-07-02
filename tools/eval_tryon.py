"""Éval comparative try-on : 12 vêtements × 2 selfies × 2 modèles.

Réutilise les adaptateurs TRYON_MODELS du worker (api/workers/tasks.py) pour
tester exactement ce que la prod exécuterait. Séquentiel : le compte Replicate
est limité à 6 prédictions/min (< 5 $ de crédit). Reprise possible : les runs
déjà présents dans results/ sont sautés.

Usage : python tools/eval_tryon.py
Sortie : .tmp/eval/results/<model>__<slot>__<selfie>.png + results.json
"""
from __future__ import annotations

import glob
import io
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

# tasks.py crée MEDIA_DIR à l'import — pointer hors de /app (read-only ici)
os.environ.setdefault("MEDIA_DIR", os.path.join(ROOT, ".tmp", "eval", "media"))
os.environ.setdefault("UPLOAD_DIR", os.path.join(ROOT, ".tmp", "eval", "uploads"))

# Charge REPLICATE_API_TOKEN depuis ~/zury/.env avant l'import replicate
for line in open(os.path.expanduser("~/zury/.env")):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

import replicate  # noqa: E402
from replicate.exceptions import ReplicateError  # noqa: E402

from api.workers.tasks import TRYON_MODELS  # noqa: E402

EVAL = os.path.join(ROOT, ".tmp", "eval")
RESULTS = os.path.join(EVAL, "results")
os.makedirs(RESULTS, exist_ok=True)

# Description passée à garment_des (idm-vton) et injectée dans le prompt (nano)
GARMENT_DES = {
    "ouest_ajuste_robe-wax": "fitted African wax print maxi dress with cowrie pattern",
    "ouest_ample_boubou":    "loose flowing West African boubou robe, white with blue embroidery",
    "ouest_coiffe_gele":     "Nigerian gele head-tie, structured silver fabric headwrap",
    "nord_ajuste_caftan":    "Moroccan kaftan, gold brocade, long sleeves",
    "nord_ample_djellaba":   "loose Moroccan djellaba robe, cream with embroidery",
    "nord_drape_melhfa":     "Sahrawi melhfa, dark red draped veil garment covering body and head",
    "est_ajuste_kitenge":    "fitted East African kitenge print dress",
    "est_ample_habesha":     "Ethiopian habesha kemis, loose grey dress with woven border",
    "est_drape_kanga":       "East African kanga, bright red wrapped cloth garment",
    "sud_ajuste_herero":     "Herero long dress, fitted bodice, red and green paisley print",
    "sud_ample_umbhaco":     "Xhosa umbhaco skirt, orange with black braid trim",
    "sud_drape_basotho":     "Basotho heritage blanket worn draped over shoulders, red black pattern",
}

MODELS = ["idm-vton", "nano-banana"]


def _buf(path: str) -> io.BytesIO:
    with open(path, "rb") as f:
        b = io.BytesIO(f.read())
    b.name = os.path.basename(path)
    return b


def run_one(model_key: str, garm_path: str, selfie_path: str, des: str) -> tuple[bytes, float]:
    model = TRYON_MODELS[model_key]
    attempts = 0
    while True:
        attempts += 1
        try:
            t0 = time.time()
            out = replicate.run(
                model["ref"],
                input=model["input"](_buf(selfie_path), _buf(garm_path), des),
            )
            dt = time.time() - t0
            item = out[0] if isinstance(out, list) else out
            if hasattr(item, "read"):
                return item.read(), dt
            import httpx
            url = getattr(item, "url", str(item))
            r = httpx.get(url, follow_redirects=True, timeout=120)
            r.raise_for_status()
            return r.content, dt
        except ReplicateError as e:
            if e.status == 429 and attempts <= 5:
                time.sleep(15 * attempts)
                continue
            raise


def main() -> None:
    garments = sorted(
        p for p in glob.glob(os.path.join(EVAL, "garments", "*"))
        if not p.endswith(".json")
    )
    selfies = sorted(glob.glob(os.path.join(EVAL, "selfies", "*.jpg")))
    assert garments and selfies, "set d'éval incomplet"

    results_path = os.path.join(EVAL, "results.json")
    results = json.load(open(results_path)) if os.path.exists(results_path) else {}

    todo = [
        (m, g, s)
        for m in MODELS
        for g in garments
        for s in selfies
    ]
    print(f"{len(todo)} runs ({len(garments)} vêtements × {len(selfies)} selfies × {len(MODELS)} modèles)")

    for i, (model_key, garm, selfie) in enumerate(todo, 1):
        slot = os.path.splitext(os.path.basename(garm))[0]
        sname = os.path.splitext(os.path.basename(selfie))[0]
        key = f"{model_key}__{slot}__{sname}"
        out_path = os.path.join(RESULTS, f"{key}.png")

        if os.path.exists(out_path):
            print(f"[{i}/{len(todo)}] {key} — déjà fait, skip")
            continue

        try:
            content, dt = run_one(model_key, garm, selfie, GARMENT_DES[slot])
            with open(out_path, "wb") as f:
                f.write(content)
            results[key] = {"ok": True, "seconds": round(dt, 1)}
            print(f"[{i}/{len(todo)}] {key} — ok en {dt:.0f}s")
        except Exception as e:
            results[key] = {"ok": False, "error": str(e)[:300]}
            print(f"[{i}/{len(todo)}] {key} — ÉCHEC : {str(e)[:120]}")

        json.dump(results, open(results_path, "w"), indent=2)
        time.sleep(3)  # marge rate-limit

    ok = sum(1 for r in results.values() if r.get("ok"))
    print(f"terminé : {ok}/{len(results)} réussis")


if __name__ == "__main__":
    main()
