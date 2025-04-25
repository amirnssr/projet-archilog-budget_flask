import io
import uuid

from flask import (
    Blueprint,
    Response,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_httpauth import HTTPBasicAuth
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired
from werkzeug.security import check_password_hash, generate_password_hash
from wtforms import FileField, FloatField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

import archilog.models as models
import archilog.services as services
from archilog.services import import_from_csv

auth = HTTPBasicAuth()




users = {
    "admin": generate_password_hash("adminpassword"),  
    "user": generate_password_hash("userpassword")     
}



roles = {
    "admin": "admin",  
    "user": "user"    
}




@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username




@auth.get_user_roles
def get_user_roles(username):
    return roles.get(username, "user")  


web_ui_bp = Blueprint("web_ui", __name__, url_prefix='/', template_folder="../templates")




@web_ui_bp.route("/")
@auth.login_required
def index():
    return render_template("index.html")



@web_ui_bp.route("/all_entries", methods=["GET"])
@auth.login_required(role="admin")  
def all_entries():
    try:
        entries = models.get_all_entries()  
        return render_template("all_entries.html", entries=entries)  
    except Exception as e:
        flash(f"Erreur lors de la récupération des entrées : {str(e)}", "danger")
        return redirect(url_for('web_ui.index')) 




@web_ui_bp.route("/entry_specifique", methods=["GET", "POST"])
@auth.login_required(role="admin")
def entry_specifique():
    form = EntrySearchForm()

    entry = None
    if form.validate_on_submit():
        entry_id = form.entry_id.data
        try:
            entry = models.get_entry(uuid.UUID(entry_id)) 
        except Exception as e:
            flash(f"Erreur lors de la récupération de l'entrée : {str(e)}", "danger")

    return render_template("entry_specifique.html", form=form, entry=entry)





@web_ui_bp.route("/add_entry", methods=["GET", "POST"])
@auth.login_required(role="admin")  
def add_entry():
    form = EntryForm()

    if form.validate_on_submit():
        name = form.name.data
        amount = form.amount.data
        category = form.category.data

        try:
            models.create_entry(name, amount, category)  
            flash("Entrée ajoutée avec succès !", "success")
            return redirect(url_for("web_ui.index"))
        except ValueError:
            flash("Erreur : Valeur du montant invalide", "danger")

    return render_template("home.html", form=form)





@web_ui_bp.route("/delete", methods=["GET", "POST"])
@auth.login_required(role="admin")  
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
@auth.login_required(role="admin") 
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
@auth.login_required(role="admin")  
def import_csv():
    form = ImportCSVForm()

    if form.validate_on_submit():
        file = request.files["file"]

        if file.filename == "":
            flash("Erreur : Aucun fichier sélectionné", "danger")
        else:
            try:
    
                stream = io.BytesIO(file.read())
                import_from_csv(stream)
                flash("Importation réussie", "success")
                return redirect(url_for('web_ui.index'))
            except Exception as e:
                flash(f"Erreur lors de l'importation : {str(e)}", "danger")

    return render_template("import_csv.html", form=form)






@web_ui_bp.route("/export_csv")
@auth.login_required(role=["user", "admin"])  
def export_csv():
    try:
        csv_output = services.export_to_csv()  
        return Response(
            csv_output.getvalue(), 
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=exported_data.csv"}  
        )
    except Exception as e:
        return f"Erreur lors de l'exportation : {str(e)}", 500





class EntrySearchForm(FlaskForm):
    entry_id = StringField('ID de l\'Entrée', validators=[DataRequired(), Length(min=0, max=36)])  
    submit = SubmitField('Rechercher')



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

    @app.errorhandler(500)
    def internal_server_error(error):
        return render_template('500.html'), 500
