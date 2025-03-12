import uuid
import click
from flask import Blueprint, render_template, request, redirect, url_for, Response
import archilog.models as models
import archilog.services as services

# Définition du Blueprint
web_ui_bp = Blueprint("web_ui", __name__, template_folder="../../templates")

### ROUTES FLASK ###

@web_ui_bp.route("/")
def index():
    return render_template("index.html")

@web_ui_bp.route("/home")
def home():
    return render_template("home.html")

@web_ui_bp.route("/add_entry", methods=["GET", "POST"])
def add_entry():
    if request.method == "POST":
        name = request.form["name"]
        amount = float(request.form["amount"])
        category = request.form.get("category", None)

        models.create_entry(name, amount, category)
        click.echo(f"Entrée ajoutée : {name}, {amount}, {category}")
        return redirect(url_for("web_ui.index"))

    return render_template("home.html")

@web_ui_bp.route("/delete", methods=["GET", "POST"])
def delete():
    if request.method == "POST":
        entry_id = request.form.get("entry_id")
        if entry_id:
            try:
                models.delete_entry(uuid.UUID(entry_id))
                click.echo(f"Entrée supprimée : {entry_id}")
            except Exception as e:
                click.echo(f"Erreur lors de la suppression : {str(e)}")
                return f"Erreur : {str(e)}", 400
        return redirect(url_for("web_ui.index"))

    return render_template("delete.html")

@web_ui_bp.route("/update", methods=["GET", "POST"])
def update():
    if request.method == "POST":
        entry_id = request.form.get("entry_id")
        name = request.form.get("name")
        amount = request.form.get("amount")
        category = request.form.get("category")

        if entry_id:
            try:
                entry = models.get_entry(uuid.UUID(entry_id))

                updated_name = name if name else entry.name
                updated_amount = float(amount) if amount else entry.amount
                updated_category = category if category else entry.category

                models.update_entry(uuid.UUID(entry_id), updated_name, updated_amount, updated_category)
                click.echo(f"Entrée mise à jour : {entry_id}")
                return redirect(url_for("web_ui.index"))

            except Exception as e:
                click.echo(f"Erreur lors de la mise à jour : {str(e)}")
                return f"Erreur : {str(e)}", 400

    return render_template("update.html")

@web_ui_bp.route("/export_csv")
def export_csv():
    try:
        csv_output = services.export_to_csv()
        click.echo("Exportation réussie")
        return Response(
            csv_output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=exported_data.csv"}
        )
    except Exception as e:
        click.echo(f"Erreur lors de l'exportation : {str(e)}")
        return f"Erreur lors de l'exportation : {str(e)}", 500

@web_ui_bp.route("/import_csv", methods=["GET", "POST"])
def import_csv():
    message = None  # Variable pour stocker le message de retour

    if request.method == "POST":
        if "file" not in request.files:
            message = "Erreur : Aucun fichier sélectionné"
            click.echo(message)
        else:
            file = request.files["file"]

            if file.filename == "":
                message = "Erreur : Aucun fichier sélectionné"
                click.echo(message)
            else:
                try:
                    import io
                    stream = io.StringIO(file.stream.read().decode("utf-8"))
                    services.import_from_csv(stream)
                    message = "Importation réussie"
                    click.echo(message)
                except Exception as e:
                    message = f"Erreur lors de l'importation : {str(e)}"
                    click.echo(message)

    return render_template("import_csv.html", message=message)
