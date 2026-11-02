import io
from fastapi.testclient import TestClient
from PIL import Image
from app.main import app

client = TestClient(app)


def test_web_app_and_api():
    assert client.get('/').status_code == 200
    assert 'serein' in client.get('/').text
    assert client.get('/static/app.js').status_code == 200
    assert client.get('/api/health').json()['ok']
    config = client.get('/api/config').json()
    assert config['provider'] == 'YouCam Skin Analysis v2.1'


def test_missing_api_key_rejected(monkeypatch):
    monkeypatch.delenv('YOUCAM_API_KEY', raising=False)
    img = Image.new('RGB', (600, 700))
    buf = io.BytesIO()
    img.save(buf, 'JPEG')
    r = client.post('/api/scan?consent=true', files={'file': ('selfie.jpg', buf.getvalue(), 'image/jpeg')})
    assert r.status_code == 503
    assert 'Live API is not configured' in r.json()['detail']


def test_malformed_task_id_rejected(monkeypatch):
    monkeypatch.setenv('YOUCAM_API_KEY', 'not-a-real-key')
    r = client.get('/api/scan/INVALID!')
    assert r.status_code == 400
