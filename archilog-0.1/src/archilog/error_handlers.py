# error_handler.py

def register_error_handlers(app):
    # Handler pour les erreurs 404
    @app.errorhandler(404)
    def page_not_found(error):
        return 'Page non trouvée', 404

    # Handler pour les erreurs internes du serveur
    @app.errorhandler(500)
    def internal_server_error(error):
        return 'Erreur interne du serveur', 500
