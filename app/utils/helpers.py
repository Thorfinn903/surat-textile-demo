import json
import os
from pathlib import Path
from PIL import Image
from .constants import DEFAULT_SETTINGS, SETTINGS_PATH


def load_settings() -> dict:
    if not SETTINGS_PATH.exists():
        SETTINGS_PATH.write_text(json.dumps(DEFAULT_SETTINGS, indent=2), encoding='utf-8')
        return DEFAULT_SETTINGS.copy()

    try:
        file_settings = json.loads(SETTINGS_PATH.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, OSError):
        return DEFAULT_SETTINGS.copy()

    merged = DEFAULT_SETTINGS.copy()
    for key in DEFAULT_SETTINGS:
        if key in file_settings and str(file_settings[key]).strip():
            merged[key] = str(file_settings[key]).strip()
    return merged

def normalize_whatsapp_number(contact_number: str) -> str:
    return ''.join(ch for ch in contact_number if ch.isdigit())
