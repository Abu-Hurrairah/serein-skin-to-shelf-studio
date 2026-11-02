import io
import pytest
import httpx
from PIL import Image
from app.main import prepare_image
from app.youcam import YouCamClient, YouCamError, normalize_result, _is_signed_upload_url


def test_image_reencode_and_orientation():
    img = Image.new('RGB', (600, 700), 'pink')
    blob = io.BytesIO()
    img.save(blob, 'PNG')
    out = prepare_image(blob.getvalue())
    assert out[:2] == b'\xff\xd8'
    assert Image.open(io.BytesIO(out)).size == (600, 700)


def test_reject_non_image():
    with pytest.raises(Exception):
        prepare_image(b'no image here')


def test_normalize_success_and_missing_metrics():
    result = normalize_result({'status': 200, 'data': {'task_status': 'success', 'results': {'output': [
        {'type': 'texture', 'ui_score': 78, 'raw_score': 66.7},
        {'type': 'other', 'ui_score': 30},
        {'type': 'pore', 'ui_score': None}
    ]}}})
    assert result['source'] == 'youcam-live'
    assert result['metrics'] == [{'id': 'texture', 'score': 78, 'raw_score': 66.7, 'mask_url': None}]


def test_pending_and_failed():
    assert normalize_result({'data': {'task_status': 'running'}})['state'] == 'processing'
    with pytest.raises(YouCamError):
        normalize_result({'data': {'task_status': 'error'}})


def test_safe_upload_destinations():
    assert _is_signed_upload_url('https://yce-us.s3-accelerate.amazonaws.com/a?sig=123')
    assert not _is_signed_upload_url('http://127.0.0.1/private')
    assert not _is_signed_upload_url('https://amazonaws.com.evil.org/path')


@pytest.mark.asyncio
async def test_complete_youcam_workflow():
    calls = []
    def responder(request: httpx.Request):
        calls.append((request.method, str(request.url)))
        if request.method == 'POST' and request.url.path == '/s2s/v2.0/file':
            return httpx.Response(200, json={'status': 200, 'data': {'files': [{
                'file_id': 'file_123456789',
                'requests': [{'method': 'PUT', 'url': 'https://yce-us.s3-accelerate.amazonaws.com/image?sig=x', 'headers': {'Content-Type':'image/jpeg', 'Content-Length':'10'}}]
            }]}})
        if request.method == 'PUT':
            assert request.content == b'fake-image'
            assert request.headers['Content-Type'] == 'image/jpeg'
            assert request.headers['Content-Length'] == '10'
            assert 'Authorization' not in request.headers
            return httpx.Response(200, text='ok')
        if request.method == 'POST':
            assert __import__('json').loads(request.content)['format'] == 'json'
            return httpx.Response(200, json={'status': 200, 'data': {'task_id': 'task_123456789'}})
        return httpx.Response(200, json={'status': 200, 'data': {'task_status': 'success', 'results': {'output': [
            {'type': 'acne', 'ui_score': 89}, {'type': 'radiance', 'ui_score': 64}]}}})
    async with httpx.AsyncClient(transport=httpx.MockTransport(responder)) as http:
        api = YouCamClient('test-secret', client=http)
        task = await api.start(b'fake-image')
        assert task == 'task_123456789'
        out = await api.status(task)
        assert [m['id'] for m in out['metrics']] == ['acne', 'radiance']
        assert len(calls) == 4
