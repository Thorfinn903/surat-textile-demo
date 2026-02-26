from datetime import datetime

def format_datetime(value, format="%d %b %Y %H:%M"):
    if value is None:
        return ""
    return value.strftime(format)

def get_current_utc():
    return datetime.utcnow()
