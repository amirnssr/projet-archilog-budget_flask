# app.py (ou __init__.py)

from flask import Flask
from archilog import config
from archilog.models import db, init_db  # Importation de db et init_db
from archilog.routes.web_ui import web_ui_bp  # Importation du blueprint
from archilog.error_handlers import register_error_handlers  # Importation du gestionnaire d'erreurs
from dotenv import load_dotenv  # Importer load_dotenv pour charger les variables d'environnement
import os

# Charger les variables d'environnement depuis dev.env
load_dotenv(dotenv_path='dev.env')  # Charge le fichier dev.env où les variables sont définies

def create_app():
    # Création de l'instance de l'application Flask
    app = Flask(__name__)

    # Configuration de la base de données
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('ARCHILOG_DATABASE_URL', 'sqlite:///data.db')  # Utilisation de la variable d'environnement
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('ARCHILOG_DEBUG', 'False') == 'True'  # Convertir en booléen
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'une_super_cle_secrete')  # Utiliser la variable d'environnement

    # Initialisation de la base de données
    db.init_app(app)  # Initialiser db avec l'application Flask

    # Créer les tables si elles n'existent pas
    with app.app_context():
        db.create_all()  # Crée toutes les tables dans la base de données

    # Enregistrer les handlers d'erreur
    register_error_handlers(app)

    # Enregistrement des blueprints
    app.register_blueprint(web_ui_bp)  # Enregistrement du blueprint web_ui

    return app
