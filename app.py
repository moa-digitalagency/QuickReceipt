import os
from flask import Flask

from security import get_secret_key
from routes import register_routes
from utils.i18n import t, get_locale

app = Flask(__name__)
app.secret_key = get_secret_key()

os.makedirs('data', exist_ok=True)
os.makedirs('static/uploads', exist_ok=True)

register_routes(app)

@app.context_processor
def inject_globals():
    locale = get_locale()
    return {
        't': t,
        'locale': locale,
        'is_rtl': locale == 'ar'
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
