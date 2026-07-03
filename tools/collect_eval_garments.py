"""Collecte les images de vêtements pour l'éval try-on depuis Wikimedia Commons.

Pour chaque slot (région × silhouette), interroge l'API Commons et télécharge
les N meilleurs candidats en ~800px dans .tmp/eval/candidates/<slot>/ pour
revue visuelle. La sélection finale est copiée à la main dans
.tmp/eval/garments/<slot>.jpg.

Usage : python tools/collect_eval_garments.py
"""
from __future__ import annotations

import json
import os
import sys
import time

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, ".tmp", "eval", "candidates")

API = "https://commons.wikimedia.org/w/api.php"
HEADERS = {"User-Agent": "ZuryEval/0.1 (eval interne try-on; contact: badaouisalah90@gmail.com)"}

N_CANDIDATES = 4

# slot -> requêtes Commons (essayées dans l'ordre jusqu'à avoir N candidats)
SLOTS = {
    # ── Ouest ──
    "ouest_ajuste_robe-wax":   ["ankara dress fashion", "african print dress woman"],
    "ouest_ample_boubou":      ["grand boubou", "agbada"],
    "ouest_coiffe_gele":       ["gele headtie", "nigerian headtie"],
    # ── Nord ──
    "nord_ajuste_caftan":      ["moroccan kaftan", "takchita", "caftan"],
    "nord_ample_djellaba":     ["djellaba", "moroccan djellaba", "gandoura"],
    "nord_drape_melhfa":       ["melhfa", "sahrawi woman", "haik garment"],
    # ── Est ──
    "est_ajuste_kitenge":      ["kitenge dress", "kitenge", "african print dress kenya"],
    "est_ample_habesha":       ["habesha kemis", "ethiopian traditional dress", "eritrean dress"],
    "est_drape_kanga":         ["kanga Zanzibar woman", "khanga tanzania", "kitenge wrap"],
    # ── Sud ──
    "sud_ajuste_herero":       ["herero dress", "herero woman traditional", "ohorokova"],
    "sud_ample_umbhaco":       ["umbhaco", "xhosa traditional attire", "xhosa dress"],
    "sud_drape_basotho":       ["basotho blanket", "seanamarena", "ndebele traditional dress"],
}


def search_images(query: str, limit: int) -> list[dict]:
    time.sleep(1)  # politesse API Commons — évite le rate-limiting en batch
    r = requests.get(API, headers=HEADERS, timeout=30, params={
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": 6,
        "gsrlimit": limit,
        "prop": "imageinfo",
        "iiprop": "url|extmetadata",
        "iiurlwidth": 800,
    })
    r.raise_for_status()
    pages = (r.json().get("query") or {}).get("pages") or {}
    out = []
    for p in sorted(pages.values(), key=lambda p: p.get("index", 99)):
        info = (p.get("imageinfo") or [{}])[0]
        url = info.get("thumburl") or info.get("url")
        if not url:
            continue
        meta = info.get("extmetadata") or {}
        out.append({
            "title": p.get("title", ""),
            "url": url,
            "license": (meta.get("LicenseShortName") or {}).get("value", "?"),
        })
    return out


def main() -> None:
    manifest = {}
    for slot, queries in SLOTS.items():
        slot_dir = os.path.join(OUT, slot)
        os.makedirs(slot_dir, exist_ok=True)
        picked = []
        for q in queries:
            if len(picked) >= N_CANDIDATES:
                break
            try:
                for c in search_images(q, N_CANDIDATES * 2):
                    if len(picked) >= N_CANDIDATES:
                        break
                    if any(c["url"] == p["url"] for p in picked):
                        continue
                    try:
                        img = requests.get(c["url"], headers=HEADERS, timeout=30)
                        img.raise_for_status()
                    except Exception:
                        continue
                    ext = os.path.splitext(c["url"].split("?")[0])[1] or ".jpg"
                    path = os.path.join(slot_dir, f"{len(picked)}{ext}")
                    with open(path, "wb") as f:
                        f.write(img.content)
                    picked.append({**c, "file": path})
            except Exception as e:
                print(f"  ! {slot} / {q!r}: {e}", file=sys.stderr)
        manifest[slot] = picked
        print(f"{slot}: {len(picked)} candidats")

    with open(os.path.join(OUT, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
