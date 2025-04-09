import uuid
from flask import Blueprint, render_template, request, redirect, url_for, Response, flash
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import archilog.models as models
import archilog.services as services
from archilog.services import import_from_csv
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SubmitField, FileField
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from flask_wtf.file import FileRequired, FileAllowed

# Configuration de l'authentification HTTP
auth = HTTPBasicAuth()

# Utilisateurs et mots de passe hachés
users = {
    "admin": generate_password_hash("adminpassword"),  # Admin
    "user": generate_password_hash("userpassword")     # Utilisateur normal
}

# Rôles des utilisateurs
roles = {
    "admin": "admin",  # Admin a accès à tout
    "user": "user"     # Utilisateur normal a un accès limité
}

# Vérification du mot de passe
@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username

# Récupération des rôles pour chaque utilisateur
@auth.get_user_roles
def get_user_roles(username):
    return roles.get(username, "user")  # Par défaut, le rôle est "user" si non spécifié

# Initialisation du Blueprint
web_ui_bp = Blueprint("web_ui", __name__, url_prefix='/', template_folder="../templates")

@web_ui_bp.route("/")
@auth.login_required
def index():
    return render_template("index.html")


@web_ui_bp.route("/add_entry", methods=["GET", "POST"])
@auth.login_required(role="admin")  # Cette route est réservée aux admins
def add_entry():
    form = EntryForm()

    if form.validate_on_submit():
        name = form.name.data
        amount = form.amount.data
        category = form.category.data

        try:
            models.create_entry(name, amount, category)  # Appel à la méthode add_entry du modèle
            flash("Entrée ajoutée avec succès !", "success")
            return redirect(url_for("web_ui.index"))
        except ValueError:
            flash("Erreur : Valeur du montant invalide", "danger")

    return render_template("home.html", form=form)


@web_ui_bp.route("/delete", methods=["GET", "POST"])
@auth.login_required(role="admin")  # Cette route est réservée aux admins
def delete():
    form = DeleteForm()
    if form.validate_on_submit():
        entry_id = form.entry_id.data
        try:
            models.delete_entry(uuid.UUID(entry_id))
            flash("Entrée supprimée avec succès !", "success")
        except Exception as e:
            flash(f"Erreur lors de la suppression : {str(e)}", "danger")
        return redirect(url_for("web_ui.index"))

    return render_template("delete.html", form=form)


@web_ui_bp.route("/update", methods=["GET", "POST"])
@auth.login_required(role="admin")  # Cette route est réservée aux admins
def update():
    form = UpdateForm()
    if form.validate_on_submit():
        entry_id = form.entry_id.data
        name = form.name.data
        amount = form.amount.data
        category = form.category.data

        try:
            entry = models.get_entry(uuid.UUID(entry_id))
            updated_name = name if name else entry.name
            updated_amount = float(amount) if amount else entry.amount
            updated_category = category if category else entry.category

            models.update_entry(uuid.UUID(entry_id), updated_name, updated_amount, updated_category)
            flash("Entrée mise à jour avec succès !", "success")
            return redirect(url_for("web_ui.index"))
        except Exception as e:
            flash(f"Erreur lors de la mise à jour : {str(e)}", "danger")

    return render_template("update.html", form=form)


@web_ui_bp.route("/import_csv", methods=["GET", "POST"])
@auth.login_required(role="admin")  # Cette route est réservée aux admins
def import_csv():
    form = ImportCSVForm()

    if form.validate_on_submit():
        file = request.files["file"]

        if file.filename == "":
            flash("Erreur : Aucun fichier sélectionné", "danger")
        else:
            try:
                import io
                # Convertir le fichier téléchargé en un flux utilisable par la fonction import_from_csv
                stream = io.BytesIO(file.read())
                import_from_csv(stream)
                flash("Importation réussie", "success")
                return redirect(url_for('web_ui.index'))
            except Exception as e:
                flash(f"Erreur lors de l'importation : {str(e)}", "danger")

    return render_template("import_csv.html", form=form)


@web_ui_bp.route("/export_csv")
@auth.login_required(role=["user", "admin"])  # Autoriser l'accès aux utilisateurs et aux admins
def export_csv():
    try:
        csv_output = services.export_to_csv()  # Appelle la fonction d'exportation
        return Response(
            csv_output.getvalue(),  # Retourne les données CSV
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=exported_data.csv"}  # Force le téléchargement
        )
    except Exception as e:
        return f"Erreur lors de l'exportation : {str(e)}", 500




class EntryForm(FlaskForm):
    class Meta:
        csrf = False  

    name = StringField("Nom", validators=[DataRequired(), Length(min=2, max=50)])
    amount = FloatField("Montant", validators=[DataRequired(), NumberRange(min=0)])
    category = StringField("Catégorie (optionnel)", validators=[Optional(), Length(max=50)])
    submit = SubmitField("Ajouter")

class DeleteForm(FlaskForm):
    class Meta:
        csrf = False 

    entry_id = StringField("ID de l'entrée", validators=[DataRequired()])
    submit = SubmitField("Supprimer")

class UpdateForm(FlaskForm):
    class Meta:
        csrf = False  

    entry_id = StringField("ID de l'entrée", validators=[DataRequired()])
    name = StringField("Nouveau Nom", validators=[Optional(), Length(min=2, max=50)])
    amount = FloatField("Nouveau Montant", validators=[Optional(), NumberRange(min=0)])
    category = StringField("Nouvelle Catégorie (optionnel)", validators=[Optional(), Length(max=50)])
    submit = SubmitField("Mettre à jour")

class ImportCSVForm(FlaskForm):
    file = FileField('Import CSV', validators=[FileRequired(), FileAllowed(['csv'], 'CSV files only!')])
    submit = SubmitField('Importer')
    
    
def register_error_handlers(app):
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('404.html'), 404
