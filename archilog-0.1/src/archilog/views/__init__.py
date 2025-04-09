from flask import Flask

from archilog.__init__ import config
from archilog.views.api import api_views, register_spec
from archilog.views.web_ui import register_error_handlers, web_ui_bp


def create_app():
    # Création de l'instance de l'application Flask
    app = Flask(__name__)
    app.config['SECRET_KEY'] = config.SECRET_KEY 

    # 🔹 Enregistrer les handlers d'erreur
    register_error_handlers(app)  
    register_spec(app)
   
    # Enregistrement des blueprints
    app.register_blueprint(web_ui_bp)
     # Enregistrer le blueprint de l'API
    app.register_blueprint(api_views) 

    return app
