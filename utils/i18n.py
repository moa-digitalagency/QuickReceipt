import json
import os
from flask import session

TRANSLATIONS_FILE = os.path.join('lang', 'translations.json')

_translations_cache = None

def get_translations():
    global _translations_cache
    if _translations_cache is None:
        with open(TRANSLATIONS_FILE, 'r', encoding='utf-8') as f:
            _translations_cache = json.load(f)
    return _translations_cache

def get_locale():
    return session.get('locale', 'fr')

def set_locale(locale):
    if locale in ['fr', 'en', 'ar']:
        session['locale'] = locale

def t(key):
    translations = get_translations()
    locale = get_locale()
    keys = key.split('.')
    value = translations.get(locale, translations['fr'])
    for k in keys:
        if isinstance(value, dict):
            value = value.get(k, key)
        else:
            return key
    return value if isinstance(value, str) else key
