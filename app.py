from flask import Flask
import os
import sys

app = Flask(__name__)
app.secret_key = 'diameal_secret_key_2024'

# Tambahkan path ke sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, 'pages'))
sys.path.insert(0, os.path.join(BASE_DIR, 'modules'))

try:
    from flask_session import Session

    SESSION_DIR = os.path.join(BASE_DIR, 'flask_session')
    os.makedirs(SESSION_DIR, exist_ok=True)

    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_FILE_DIR'] = SESSION_DIR
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SESSION_FILE_THRESHOLD'] = 100  # Max 100 file session

    Session(app)
    print("Flask-Session aktif (filesystem mode)")

except ImportError:
    # Kalau flask-session belum di-install, pakai cookie biasa
    # Tapi mungkin error kalau data PSO terlalu besar
    print("Flask-Session belum terinstall, fallback ke cookie.")

# Import blueprints
from pages.home import home_bp
from pages.input import input_bp
from pages.metode import metode_bp
from pages.cbf_page import cbf_bp
from pages.pso_page import pso_bp
from pages.cbf_analisis import cbf_analisis_bp
from pages.pso_analisis import pso_analisis_bp

# Register blueprints
app.register_blueprint(home_bp)
app.register_blueprint(input_bp)
app.register_blueprint(metode_bp)
app.register_blueprint(cbf_bp)
app.register_blueprint(pso_bp)
app.register_blueprint(cbf_analisis_bp)
app.register_blueprint(pso_analisis_bp)

# Debug: Print registered routes
if __name__ == "__main__":
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.config['TEMPLATES_AUTO_RELOAD'] = True

    print("\n" + "="*50)
    print("REGISTERED ROUTES:")
    print("="*50)
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint:30s} {rule.rule}")
    print("="*50 + "\n")

    app.run(debug=True, host='127.0.0.1', port=5000)