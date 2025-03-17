from flask import flash, redirect, url_for, render_template

def register_error_handlers(app):
    """Enregistre tous les handlers d'erreurs dans l'application Flask."""

    @app.errorhandler(404)
    def not_found_error(error):
        flash("Page non trouvée !", "warning")
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        flash("Erreur interne du serveur. Veuillez réessayer plus tard.", "danger")
        return render_template("errors/500.html"), 500

    @app.errorhandler(403)
    def forbidden_error(error):
        flash("Accès interdit ! Vous n'avez pas les droits nécessaires.", "error")
        return render_template("errors/403.html"), 403

    @app.errorhandler(405)
    def method_not_allowed_error(error):
        flash("Méthode non autorisée pour cette requête.", "error")
        return redirect(url_for("home"))
