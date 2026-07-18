from datetime import datetime
from src.utils import normalize_date

def test_normalize_date_none():
    today = datetime.now().strftime("%Y-%m-%d")
    assert normalize_date(None) == today
    assert normalize_date("") == today

def test_normalize_date_standard_format():
    assert normalize_date("2026-07-18") == "2026-07-18"

def test_normalize_date_slash_format():
    assert normalize_date("2026/07/18") == "2026-07-18"

def test_normalize_date_iso_format():
    assert normalize_date("2026-05-15T14:30:00") == "2026-05-15"

def test_normalize_date_invalid_fallback():
    assert normalize_date("invalid-date-string") == "invalid-date-string"
