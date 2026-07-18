from datetime import datetime

def normalize_date(date_input: str = None) -> str:
    """
    Normalizes a date input string (YYYY-MM-DD, YYYY/MM/DD, ISO string) into standard YYYY-MM-DD format.
    Defaults to today's date if date_input is None or empty.
    """
    if not date_input:
        return datetime.now().strftime("%Y-%m-%d")

    date_str = date_input.strip()
    if len(date_str) >= 10 and date_str[4] in ('-', '/') and date_str[7] in ('-', '/'):
        return date_str[:10].replace('/', '-')
    try:
        return datetime.fromisoformat(date_str).strftime("%Y-%m-%d")
    except Exception:
        return date_str
