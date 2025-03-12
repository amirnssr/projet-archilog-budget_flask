from flask import Flask
from dotenv import load_dotenv
import os

# Charger les variables d'environnement
load_dotenv()

def create_app():
    """Factory pour créer l'application Flask."""
    app = Flask(__name__)

    # Configuration centralisée
    app.config.from_prefixed_env(prefix="ARCHILOG_FLASK")

    # Importer et enregistrer les Blueprints
    from .routes.main import main_bp
    from .routes.web_ui import web_ui
    app.register_blueprint(main_bp)
    app.register_blueprint(web_ui)

    # Gestion des erreurs
    from .errors.handlers import register_error_handlers
    register_error_handlers(app)

    return app
