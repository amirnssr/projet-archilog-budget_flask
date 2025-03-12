import uuid
import click
from flask import Blueprint, render_template, request, redirect, url_for, Response, flash
import archilog.models as models
import archilog.services as services
from archilog.forms import EntryForm, DeleteForm, UpdateForm, ImportCSVForm


web_ui_bp = Blueprint("web_ui", __name__, template_folder="../../templates")

### ROUTES FLASK ###

@web_ui_bp.route("/")
def index():
    return render_template("index.html")

@web_ui_bp.route("/home", methods=["GET", "POST"])
def home():
    form = EntryForm()
    if form.validate_on_submit():
        name = form.name.data
        amount = form.amount.data
        category = form.category.data if form.category.data else None  # Si vide, mettre None

        models.create_entry(name, amount, category)
        flash("Entrée ajoutée avec succès !", "success")
        return redirect(url_for("index.html"))

    return render_template("home.html", form=form)

@web_ui_bp.route("/delete", methods=["GET", "POST"])
def delete():
    form = DeleteForm()
    if form.validate_on_submit():
        entry_id = form.entry_id.data
        try:
            models.delete_entry(uuid.UUID(entry_id))
            flash("Entrée supprimée avec succès !", "success")
        except Exception as e:
            flash(f"Erreur lors de la suppression : {str(e)}", "danger")
        return redirect(url_for("index.html"))

    return render_template("delete.html", form=form)

@web_ui_bp.route("/update", methods=["GET", "POST"])
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
            return redirect(url_for("index.html"))
        except Exception as e:
            flash(f"Erreur lors de la mise à jour : {str(e)}", "danger")

    return render_template("update.html", form=form)

@web_ui_bp.route("/import_csv", methods=["GET", "POST"])
def import_csv():
    form = ImportCSVForm()

    if form.validate_on_submit():
        file = request.files["file"]

        if file.filename == "":
            flash("Erreur : Aucun fichier sélectionné", "danger")
        else:
            try:
                import io
                stream = io.StringIO(file.stream.read().decode("utf-8"))
                services.import_from_csv(stream)
                flash("Importation réussie", "success")
            except Exception as e:
                flash(f"Erreur lors de l'importation : {str(e)}", "danger")

    return render_template("import_csv.html", form=form)
