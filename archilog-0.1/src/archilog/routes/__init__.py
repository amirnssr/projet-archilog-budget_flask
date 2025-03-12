from flask import Flask
from dotenv import load_dotenv
import os

# Charger les variables d'environnement
load_dotenv()

def create_app():
    """Factory pour créer l'application Flask."""
    app = Flask(__name__)

    # Importer et enregistrer les Blueprints
    from archilog.routes.web_ui import web_ui_bp

    app.register_blueprint(web_ui_bp, url_prefix="/ui")  # Ajout d'un prefixe

    return app
