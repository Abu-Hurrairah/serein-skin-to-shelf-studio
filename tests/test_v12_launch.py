from pathlib import Path

def test_launcher_uses_new_port():
    root=Path(__file__).resolve().parents[1]
    launcher=(root/'START_WINDOWS.bat').read_text()
    assert '--port 8011' in launcher
    assert '127.0.0.1:8011' in launcher
