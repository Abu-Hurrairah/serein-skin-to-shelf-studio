"""Serein API: stateless, private by default, no uploaded-face persistence."""
from __future__ import annotations

import io
import os
import logging

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image, ImageOps, UnidentifiedImageError

from .youcam import YouCamClient, YouCamError, TASK_ID_RE

load_dotenv()
logger = logging.getLogger('serein')
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAX_UPLOAD = 9 * 1024 * 1024
MAX_PIXELS = 16_000_000
Image.MAX_IMAGE_PIXELS = MAX_PIXELS
app = FastAPI(title='Serein Skin-to-Shelf Studio', version='1.0.0', docs_url='/api/docs', redoc_url=None)
app.mount('/static', StaticFiles(directory=os.path.join(BASE, 'static')), name='static')


def key() -> str:
    return os.getenv('YOUCAM_API_KEY', '').strip()


@app.get('/api/health')
async def health():
    return {'ok': True, 'service': 'serein'}


@app.get('/api/config')
async def config():
    return {'mode': 'live' if key() else 'demo', 'provider': 'YouCam Skin Analysis v2.1', 'requires_consent': True}


def prepare_image(blob: bytes) -> bytes:
    if len(blob) > MAX_UPLOAD:
        raise HTTPException(413, 'Photo must be smaller than 9 MB.')
    try:
        image = Image.open(io.BytesIO(blob))
        if image.format not in ('JPEG', 'PNG'):
            raise HTTPException(415, 'Use a JPG or PNG photo.')
        image = ImageOps.exif_transpose(image)
        w, h = image.size
        if w * h > MAX_PIXELS:
            raise HTTPException(413, 'Please resize your photo below 16 megapixels.')
        if min(w, h) < 480:
            raise HTTPException(422, 'Photo must be at least 480 pixels on its shorter side.')
        image.load()
        if image.mode != 'RGB':
            background = Image.new('RGB', image.size, '#ffffff')
            if 'A' in image.getbands():
                background.paste(image, mask=image.getchannel('A'))
            else:
                background.paste(image)
            image = background
        out = io.BytesIO()
        image.save(out, 'JPEG', quality=90, optimize=True)
        rendered = out.getvalue()
        if len(rendered) > MAX_UPLOAD:
            raise HTTPException(413, 'Processed photo too large. Resize and retry.')
        return rendered
    except HTTPException:
        raise
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError) as exc:
        raise HTTPException(422, 'Could not read photo. Please use a valid JPG or PNG.') from exc


@app.post('/api/scan')
async def scan(file: UploadFile = File(...), consent: bool = False):
    if not key():
        raise HTTPException(503, 'Live API is not configured. Use the clearly labelled sample experience.')
    if not consent:
        raise HTTPException(400, 'Consent is required before uploading to YouCam.')
    if file.content_type not in ('image/jpeg', 'image/png'):
        raise HTTPException(415, 'Use a JPG or PNG photo.')
    data = await file.read(MAX_UPLOAD + 1)
    await file.close()
    processed = prepare_image(data)
    try:
        task_id = await YouCamClient(key()).start(processed)
        return {'state': 'processing', 'source': 'youcam-live', 'task_id': task_id}
    except YouCamError as exc:
        raise HTTPException(502, str(exc)) from exc


@app.get('/api/scan/{task_id:path}')
async def scan_status(task_id: str):
    if not key():
        raise HTTPException(503, 'Live API is not configured.')
    if not TASK_ID_RE.fullmatch(task_id):
        raise HTTPException(400, 'Invalid task ID.')
    try:
        return await YouCamClient(key()).status(task_id)
    except YouCamError as exc:
        raise HTTPException(502, str(exc)) from exc


@app.get('/')
async def index():
    return FileResponse(os.path.join(BASE, 'static', 'index.html'))
