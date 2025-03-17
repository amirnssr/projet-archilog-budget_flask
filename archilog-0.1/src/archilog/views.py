import uuid
import click
from flask import Flask, Response, render_template, request, redirect, url_for
import archilog.models as models
import archilog.services as services
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from archilog.forms import *  


app = Flask(__name__)

# Initialisation de la base de donnees
with app.app_context():
    models.init_db()


### ROUTES FLASK ###

@app.route("/")
def index():
    
    return render_template("index.html")


@app.route("/home")
def home():
    form = EntryForm()
    return render_template("home.html", form=form)

@app.route("/add_entry", methods=["GET", "POST"])
def add_entry():
    if request.method == "POST":
        name = request.form["name"]
        amount = float(request.form["amount"])
        category = request.form.get("category", None)

        models.create_entry(name, amount, category)
        click.echo(f"Entree ajoutee : {name}, {amount}, {category}")
        return redirect("/")


    return render_template("home.html")


@app.route("/delete", methods=["GET", "POST"])
def delete():
    form=DeleteForm()
    if request.method == "POST":
        entry_id = request.form.get("entry_id")
        if entry_id:
            try:
                models.delete_entry(uuid.UUID(entry_id))
                click.echo(f"Entree supprimee : {entry_id}")
            except Exception as e:
                click.echo(f"Erreur lors de la suppression : {str(e)}")
                return f"Erreur : {str(e)}", 400
        return redirect(url_for("index"))

    return render_template("delete.html", form=form)


@app.route("/update", methods=["GET", "POST"])
def update():
    form=UpdateForm()
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
                click.echo(f"Entree mise a jour : {entry_id}")
                return redirect(url_for("index"))

            except Exception as e:
                click.echo(f"Erreur lors de la mise a jour : {str(e)}")
                return f"Erreur : {str(e)}", 400

    return render_template("update.html", form=form)


@app.route("/export_csv")
def export_csv():
    try:
        csv_output = services.export_to_csv()
        click.echo("Exportation reussie")
        return Response(
            csv_output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=exported_data.csv"}
        )
    except Exception as e:
        click.echo(f"Erreur lors de l'exportation : {str(e)}")
        return f"Erreur lors de l'exportation : {str(e)}", 500


@app.route("/import_csv", methods=["GET", "POST"])
def import_csv():
    form=ImportCSVForm()
    message = None  # Variable pour stocker le message de retour

    if request.method == "POST":
        if "file" not in request.files:
            message = "Erreur : Aucun fichier sélectionne"
            click.echo(message)
        else:
            file = request.files["file"]

            if file.filename == "":
                message = "Erreur : Aucun fichier sélectionne"
                click.echo(message)
            else:
                try:
                    import io
                    stream = io.StringIO(file.stream.read().decode("utf-8"))
                    services.import_from_csv(stream)
                    message = "Importation reussie"
                    click.echo(message)
                except Exception as e:
                    message = f"Erreur lors de l'importation : {str(e)}"
                    click.echo(message)

    return render_template("import_csv.html", message=message, form=form)


if __name__ == "__main__":
    app.run(debug=True)



@click.group()
def cli():
    pass

@cli.command()
def init_db():
    models.init_db()

@cli.command()
@click.option("-n", "--name", prompt="Nom :", required=True)
@click.option("-a", "--amount", type=float, prompt="Montant :", required=True)
@click.option("-c", "--category", prompt="Categorie :", required=True)
def create(name: str, amount: float, category: str):
    models.create_entry(name, amount, category)
    click.echo(f"Entree creee : {name}, {amount}, {category}")

@cli.command(name="delete")
@click.option("--id", "entry_id", required=True, type=str, help="ID de l'utilisateur a supprimer")
def delete_cli(entry_id: str):
    try:
        entry_uuid = uuid.UUID(entry_id)
        models.delete_entry(entry_uuid)
        click.echo(f"Entree avec l'ID {entry_uuid} supprimee")
    except ValueError:
        click.echo(f"Erreur : L'ID fourni ({entry_id}) n'est pas un UUID valide.")
    except Exception as e:
        click.echo(f"Erreur lors de la suppression : {str(e)}")

@cli.command(name="update")
@click.option("--id", "entry_id", required=True, type=str, help="ID de l'utilisateur a mettre a jour")
@click.option("--name", type=str, help="Nouveau nom")
@click.option("--amount", type=float, help="Nouveau montant")
@click.option("--category", type=str, help="Nouvelle categorie")
def update_cli(entry_id: str, name: str, amount: float, category: str):
    try:
        entry_uuid = uuid.UUID(entry_id)
        entry = models.get_entry(entry_uuid)
        if not entry:
            click.echo(f"Erreur : Aucun utilisateur trouve avec l'ID {entry_id}.")
            return

        new_name = name if name else entry.name
        new_amount = amount if amount else entry.amount
        new_category = category if category else entry.category

        models.update_entry(entry_uuid, new_name, new_amount, new_category)
        click.echo(f"Entree avec l'ID {entry_uuid} mise a jour")

    except ValueError:
        click.echo(f"Erreur : L'ID fourni ({entry_id}) n'est pas un UUID valide.")
    except Exception as e:
        click.echo(f"Erreur lors de la mise a jour : {str(e)}")
        
@cli.command(name="export-csv")
@click.option("--output", type=click.Path(), default="exported_data.csv", help="Nom du fichier CSV a generer")
def export_csv_cli(output):
    """
    Commande CLI pour exporter les entrées de la base de donnees en CSV.
    """
    import archilog.services as services  # Ajout de l'import dans la fonction

    try:
        csv_output = services.export_to_csv()
        with open(output, "w", encoding="utf-8") as f:
            f.write(csv_output.getvalue())
        click.echo(f"Donnees exportees dans '{output}'")
    except Exception as e:
        click.echo(f"Erreur lors de l'exportation CSV : {str(e)}")


@cli.command(name="import-csv")
@click.argument("csv_file", type=click.File("r"))
def import_csv_cli(csv_file):
    """
    Commande CLI pour importer des entrees depuis un fichier CSV.
    """
    import archilog.services as services  # Ajout de l'import dans la fonction

    try:
        services.import_from_csv(csv_file)
        click.echo("Importation du fichier CSV reussie")
    except Exception as e:
        click.echo(f"Erreur lors de l'importation : {str(e)}")


if __name__ == "__main__":
    cli()
 