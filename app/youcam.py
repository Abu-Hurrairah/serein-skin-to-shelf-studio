"""YouCam Skin Analysis V2.1: create file -> upload binary -> task -> poll.

Official API reference: https://docs.perfectcorp.com/reference/ai_skin_analysis/v2.1
"""
from __future__ import annotations

import re
from urllib.parse import urlsplit
from typing import Any

import httpx

API_BASE = "https://yce-api-01.makeupar.com"
SKIN_PATH = "/s2s/v2.1/task/skin-analysis"
FILE_PATH = "/s2s/v2.0/file"
ACTIONS = ["acne", "pore", "texture", "redness", "moisture", "radiance"]
TASK_ID_RE = re.compile(r"^[A-Za-z0-9_+\-/=]{8,256}$")

class YouCamError(Exception):
    """Safe error message for upstream failures."""


def _payload(response: httpx.Response) -> dict[str, Any]:
    try:
        value = response.json()
    except ValueError as exc:
        raise YouCamError("YouCam returned an invalid response. Please retry.") from exc
    if not 200 <= response.status_code < 300:
        code = value.get('error_code') if isinstance(value, dict) else None
        raise YouCamError(f"YouCam request failed ({response.status_code}{', ' + str(code) if code else ''}).")
    if not isinstance(value, dict):
        raise YouCamError("YouCam returned an unexpected response.")
    if value.get('error') or (isinstance(value.get('status'), int) and value['status'] >= 400):
        raise YouCamError(f"YouCam rejected the request ({value.get('error_code') or 'API error'}).")
    return value


def _is_signed_upload_url(url: str) -> bool:
    """Reject SSRF: PUT URL must be HTTPS and point to known object storage."""
    try:
        p = urlsplit(url)
    except ValueError:
        return False
    host = (p.hostname or '').lower()
    return (p.scheme == 'https' and p.username is None and p.password is None
            and p.port in (None, 443)
            and (host.endswith('.amazonaws.com') or host == 'storage.googleapis.com'))


def normalize_result(document: dict[str, Any]) -> dict[str, Any]:
    """Read only metric values actually returned by the YouCam JSON result.

    The provider uses UI scores as motivational indicators, not clinical scores.
    We don't fabricate missing metrics and never report medical diagnoses.
    """
    data = document.get('data', document)
    if not isinstance(data, dict):
        raise YouCamError('Unexpected YouCam task status response.')
    status = str(data.get('task_status', data.get('status', 'processing'))).lower()
    if status in {'error', 'failed', 'failure'}:
        raise YouCamError('YouCam could not analyze this photo. Try another well-lit selfie.')
    if status not in {'success', 'completed'}:
        return {'state': 'processing'}
    results = data.get('results', {})
    output = results.get('output', []) if isinstance(results, dict) else []
    if not isinstance(output, list):
        output = []
    metrics = []
    allowed = set(ACTIONS)
    for item in output:
        if not isinstance(item, dict):
            continue
        name = item.get('type', item.get('name', ''))
        if name not in allowed:
            continue
        score = item.get('ui_score')
        if not isinstance(score, (int, float)) or isinstance(score, bool) or not 0 <= score <= 100:
            continue
        images = item.get('mask_urls', [])
        if not isinstance(images, list):
            images = []
        metrics.append({
            'id': name,
            'score': round(float(score)),
            'raw_score': item.get('raw_score') if isinstance(item.get('raw_score'), (int, float)) else None,
            'mask_url': next((u for u in images if isinstance(u, str) and u.startswith('https://')), None),
        })
    if not metrics:
        raise YouCamError('Analysis finished, but no readable skin scores were returned. Please try again.')
    return {'state': 'success', 'source': 'youcam-live', 'metrics': metrics}


class YouCamClient:
    def __init__(self, api_key: str, client: httpx.AsyncClient | None = None):
        self.api_key = api_key
        self._client = client

    async def _call(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        try:
            if self._client is not None:
                return await self._client.request(method, url, timeout=30, **kwargs)
            async with httpx.AsyncClient(timeout=30, follow_redirects=False) as client:
                return await client.request(method, url, **kwargs)
        except (httpx.TimeoutException, httpx.NetworkError) as exc:
            raise YouCamError('YouCam is temporarily unreachable. Check your internet connection.') from exc

    @property
    def headers(self) -> dict[str, str]:
        return {'Authorization': f'Bearer {self.api_key}', 'Content-Type': 'application/json'}

    async def start(self, image_bytes: bytes) -> str:
        registration = _payload(await self._call('POST', API_BASE + FILE_PATH,
            headers=self.headers,
            json={'files': [{'content_type': 'image/jpeg', 'file_name': 'serein-capture.jpg', 'file_size': len(image_bytes)}]}
        ))
        group = registration.get('data', registration)
        files = group.get('files', []) if isinstance(group, dict) else []
        if not files or not isinstance(files[0], dict):
            raise YouCamError('YouCam did not return an image upload slot.')
        target = files[0]
        file_id = target.get('file_id')
        requests = target.get('requests', [])
        if not file_id or not requests:
            raise YouCamError('YouCam did not return upload instructions.')
        req = requests[0]
        signed_url = req.get('url', '')
        if not _is_signed_upload_url(signed_url) or req.get('method', 'PUT').upper() != 'PUT':
            raise YouCamError('YouCam returned an unrecognized upload destination.')
        # The pre-signed URL signature can depend on the exact provider-supplied headers.
        # Use a narrow, explicit allow-list; never forward the Bearer token to object storage.
        signed_headers = req.get('headers') if isinstance(req.get('headers'), dict) else {}
        upload_headers = {k: str(v) for k, v in signed_headers.items()
                          if k.lower() in ('content-type', 'content-length')}
        upload_headers.setdefault('Content-Type', 'image/jpeg')
        upload = await self._call('PUT', signed_url, content=image_bytes, headers=upload_headers)
        if not 200 <= upload.status_code < 300:
            raise YouCamError(f'Image upload failed ({upload.status_code}).')
        task = _payload(await self._call('POST', API_BASE + SKIN_PATH,
            headers=self.headers,
            json={'src_file_id': file_id, 'dst_actions': ACTIONS, 'format': 'json'}
        ))
        data = task.get('data', task)
        task_id = data.get('task_id') if isinstance(data, dict) else None
        if not isinstance(task_id, str) or not TASK_ID_RE.fullmatch(task_id):
            raise YouCamError('YouCam did not return a valid task ID.')
        return task_id

    async def status(self, task_id: str) -> dict[str, Any]:
        if not TASK_ID_RE.fullmatch(task_id):
            raise YouCamError('Invalid task ID.')
        response = _payload(await self._call('GET', API_BASE + SKIN_PATH + '/' + task_id, headers=self.headers))
        return normalize_result(response)
