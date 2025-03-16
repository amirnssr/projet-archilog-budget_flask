from flask import Flask
from dotenv import load_dotenv
import os
from flask import Flask
from archilog import config
# Charger les variables d'environnement
load_dotenv()

def create_app():
    app.config["WTF_CSRF_ENABLED"] = False

    """Factory pour créer l'application Flask."""
    app = Flask(__name__)

    app.config["SECRET_KEY"] = config.SECRET_KEY  # ✅ Vérifie que la clé est bien définie

    # ✅ Enregistrement du Blueprint après la création de `app`
    from archilog.routes.web_ui import web_ui_bp
    app.register_blueprint(web_ui_bp, url_prefix="/")

    return app


