from flask import Flask
from archilog.routes.web_ui import web_ui_bp
from archilog.routes.error_handlers import register_error_handlers
from archilog.models import init_db
from archilog.__init__ import config  # Assure-toi d'importer la bonne config

def create_app():
    # Création de l'instance de l'application Flask
    app = Flask(__name__)
    app.config['SECRET_KEY'] = config.SECRET_KEY 

    # 🔹 Enregistrer les handlers d'erreur
    register_error_handlers(app)  
    
    # Initialisation de la base de données
    init_db()

    # Enregistrement des blueprints
    app.register_blueprint(web_ui_bp)

    return app
