"""Tests du détecteur d'anomalies try-on (no-op / diptyque).

Reproduit les modes d'échec observés à l'éval du 2026-07-03 :
- no-op : nano-banana renvoie le selfie (ré-encodé) au lieu de l'éditer
- diptyque : deux panneaux côte à côte au lieu d'une édition in-place
"""
from __future__ import annotations

import io
import os

import pytest
from PIL import Image, ImageDraw

from api.workers.tasks import _detect_anomaly


@pytest.fixture
def selfie_path(tmp_path):
    """Portrait 3:4 avec un dégradé + silhouette, assez structuré pour être réaliste."""
    im = Image.new("RGB", (600, 800))
    d = ImageDraw.Draw(im)
    for y in range(800):
        d.line([(0, y), (600, y)], fill=(200 - y // 8, 180 - y // 10, 160 - y // 12))
    d.ellipse([200, 80, 400, 280], fill=(120, 80, 60))       # tête
    d.rectangle([180, 300, 420, 700], fill=(90, 90, 140))    # torse
    path = tmp_path / "selfie.jpg"
    im.save(path, quality=90)
    return str(path)


def _bytes(im: Image.Image) -> bytes:
    buf = io.BytesIO()
    im.save(buf, format="PNG")
    return buf.getvalue()


def test_noop_detected(selfie_path):
    # Ré-encodage JPEG léger + petit décalage de luminosité, comme observé
    im = Image.open(selfie_path).point(lambda p: min(255, p + 4))
    assert _detect_anomaly(_bytes(im), selfie_path) == "no-op"


def test_diptych_detected(selfie_path):
    im = Image.open(selfie_path)
    dip = Image.new("RGB", (im.width * 2, im.height))
    dip.paste(im, (0, 0))
    dip.paste(im.transpose(Image.FLIP_LEFT_RIGHT), (im.width, 0))
    assert _detect_anomaly(_bytes(dip), selfie_path) == "diptyque"


def test_real_edit_passes(selfie_path):
    # Vraie édition : le vêtement (torse) change complètement de texture
    im = Image.open(selfie_path)
    d = ImageDraw.Draw(im)
    for y in range(300, 700, 20):
        d.rectangle([180, y, 420, y + 10], fill=(220, 170, 60))
        d.rectangle([180, y + 10, 420, y + 20], fill=(160, 40, 40))
    assert _detect_anomaly(_bytes(im), selfie_path) is None


def test_resized_result_still_noop(selfie_path):
    # Le no-op peut revenir dans une résolution différente
    im = Image.open(selfie_path).resize((450, 600))
    assert _detect_anomaly(_bytes(im), selfie_path) == "no-op"
