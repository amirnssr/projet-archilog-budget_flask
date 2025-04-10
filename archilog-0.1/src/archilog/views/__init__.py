from flask import Flask

from archilog.__init__ import config
from archilog.views.api import api_views, register_spec
from archilog.views.web_ui import register_error_handlers, web_ui_bp


def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = config.SECRET_KEY 

    register_error_handlers(app)  
    register_spec(app)
   
    app.register_blueprint(web_ui_bp)
    app.register_blueprint(api_views) 

    return app
