from flask import flash, redirect, url_for, abort, render_template

def register_error_handlers(app):
    @app.errorhandler(500)
    def handle_internal_error(error):
        flash("Erreur interne du serveur", "error")
        return redirect(url_for("web_ui.show", page="home"))

    @app.get("/users/create")
    def users_create_form():
        abort(500)
        return render_template("users_create_form.html")
