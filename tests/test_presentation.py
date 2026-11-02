"""Guard key brand details and the independent demo disclosure."""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def test_author_credit_is_on_all_screens():
    html=(ROOT/'static/index.html').read_text()
    assert 'Designed &amp; Developed by <strong>Abu Hurrairah</strong>' in html
    assert 'SEREIN 1.4' in html
    assert '<meta name="author" content="Abu Hurrairah">' in html

def test_atelier_styles_and_original_art_are_included():
    html=(ROOT/'static/index.html').read_text()
    js=(ROOT/'static/app.js').read_text()
    assert '/static/atelier.css' in html
    assert 'const PORTRAIT_ART =' in js
    assert (ROOT/'static/skin-study.svg').is_file()

def test_real_vs_sample_modes_are_distinguishable():
    js=(ROOT/'static/app.js').read_text()
    assert 'Demo mode · No API key' in js
    assert 'API key loaded · Scan to verify' in js
    assert 'YouCam scan verified' in js
    assert 'SAMPLE / NOT GENERATED FROM YOUR PHOTO' in js
    assert 'YouCam scan verified' in js
