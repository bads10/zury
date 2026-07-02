"""Construit le rapport HTML comparatif de l'éval try-on.

Grille : 1 ligne par vêtement × selfie, colonnes = vêtement | selfie |
idm-vton | nano-banana. Images embarquées en data-URI (thumbnails) pour que
le fichier soit autonome et publiable en Artifact.

Usage : python tools/build_eval_report.py
Sortie : .tmp/eval/report.html
"""
from __future__ import annotations

import base64
import glob
import io
import json
import os

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVAL = os.path.join(ROOT, ".tmp", "eval")
THUMB_H = 340

REGIONS = {"ouest": "Afrique de l'Ouest", "nord": "Afrique du Nord",
           "est": "Afrique de l'Est", "sud": "Afrique australe"}
SILHOUETTES = {"ajuste": "ajusté", "ample": "ample", "drape": "drapé", "coiffe": "coiffe"}


def data_uri(path: str) -> str:
    im = Image.open(path).convert("RGB")
    ratio = THUMB_H / im.height
    im = im.resize((max(1, int(im.width * ratio)), THUMB_H))
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=72)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def main() -> None:
    results = json.load(open(os.path.join(EVAL, "results.json")))
    selection = json.load(open(os.path.join(EVAL, "garments", "selection.json")))
    garments = sorted(
        p for p in glob.glob(os.path.join(EVAL, "garments", "*")) if not p.endswith(".json")
    )
    selfies = sorted(glob.glob(os.path.join(EVAL, "selfies", "*.jpg")))

    rows = []
    for garm in garments:
        slot = os.path.splitext(os.path.basename(garm))[0]
        region, silhouette, name = (slot.split("_", 2) + ["", ""])[:3]
        for selfie in selfies:
            sname = os.path.splitext(os.path.basename(selfie))[0]
            cells = [f'<td><img src="{data_uri(garm)}" loading="lazy"></td>',
                     f'<td><img src="{data_uri(selfie)}" loading="lazy"></td>']
            for model in ["idm-vton", "nano-banana"]:
                key = f"{model}__{slot}__{sname}"
                out = os.path.join(EVAL, "results", f"{key}.png")
                r = results.get(key, {})
                if r.get("ok") and os.path.exists(out):
                    sec = r.get("seconds", "?")
                    cells.append(
                        f'<td><img src="{data_uri(out)}" loading="lazy">'
                        f'<div class="meta">{sec}s</div></td>'
                    )
                else:
                    err = (r.get("error") or "absent").replace("<", "&lt;")[:160]
                    cells.append(f'<td class="fail">ÉCHEC<div class="meta">{err}</div></td>')
            label = (f'{REGIONS.get(region, region)}<br><b>{name.replace("-", " ")}</b>'
                     f'<br><span class="sil">{SILHOUETTES.get(silhouette, silhouette)}</span>'
                     f'<br><span class="src">{selection[slot]["license"]}</span>'
                     f'<br><span class="src">{sname}</span>')
            rows.append(f'<tr><th>{label}</th>{"".join(cells)}</tr>')

    html = f"""<meta charset="utf-8">
<title>Éval try-on Zury — idm-vton vs nano-banana</title>
<style>
  body {{ font-family: system-ui, sans-serif; background:#151210; color:#eee8dd; margin:24px; }}
  h1 {{ font-size: 22px; }} p {{ color:#b7ab9a; max-width: 900px; }}
  .wrap {{ overflow-x:auto; }}
  table {{ border-collapse: collapse; }}
  th, td {{ padding: 8px; border-bottom: 1px solid #2e2822; text-align:left;
            vertical-align: top; font-weight: normal; font-size: 13px; }}
  thead th {{ color:#d4a843; font-weight:600; position:sticky; top:0; background:#151210; }}
  img {{ height: {THUMB_H}px; border-radius: 8px; display:block; }}
  .meta {{ color:#8a7560; font-size:11px; margin-top:4px; }}
  .sil {{ color:#d4a843; }} .src {{ color:#6d6152; font-size:11px; }}
  .fail {{ color:#c4622d; font-weight:600; min-width:180px; }}
</style>
<h1>Éval try-on — idm-vton vs nano-banana</h1>
<p>12 vêtements (4 régions × silhouettes ajusté/ample/drapé) × 2 selfies synthétiques
(Fitzpatrick ~III et ~VI). Vêtements : Wikimedia Commons (licences indiquées).
Selfies : flux-dev, personnes fictives.</p>
<div class="wrap"><table>
<thead><tr><th>Vêtement</th><th>Image vêtement</th><th>Selfie</th>
<th>idm-vton</th><th>nano-banana</th></tr></thead>
<tbody>{"".join(rows)}</tbody>
</table></div>
"""
    out = os.path.join(EVAL, "report.html")
    with open(out, "w") as f:
        f.write(html)
    print(out, f"({os.path.getsize(out) // 1024} Ko)")


if __name__ == "__main__":
    main()
