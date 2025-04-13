import io
import uuid

import click

import archilog.models as models
from archilog.services import import_from_csv


@click.group()
def cli():
    pass




@cli.command()
def init_db():
    models.init_db()
    
    
    

@cli.command(name="get-entries")
def get_entries_cli():
    """Commande CLI pour récupérer toutes les entrées."""
    try:
        entries = models.get_all_entries()
        for entry in entries:
            click.echo(f"ID: {entry.id}, Name: {entry.name}, Amount: {entry.amount}, Category: {entry.category}")
    except Exception as e:
        click.echo(f"Erreur lors de la récupération des entrées : {str(e)}")
        
        
        

@cli.command(name="get-entry")
@click.option("--id", "entry_id", required=True, help="ID de l'entrée à récupérer")
def get_entry_cli(entry_id: str):
    """Commande CLI pour récupérer une entrée par ID."""
    try:
        entry = models.get_entry(uuid.UUID(entry_id))
        click.echo(f"ID: {entry.id}, Name: {entry.name}, Amount: {entry.amount}, Category: {entry.category}")
    except Exception as e:
        click.echo(f"Erreur lors de la récupération de l'entrée : {str(e)}")
        
        
        
        

@cli.command()
@click.option("-n", "--name", prompt="Nom :", required=True)
@click.option("-a", "--amount", type=float, prompt="Montant :", required=True)
@click.option("-c", "--category", default=None, help="Catégorie de l'entrée (optionnelle)")
def create(name: str, amount: float, category: str | None):
    """Créer une nouvelle entrée avec une catégorie optionnelle."""
    models.create_entry(name, amount, category)
    click.echo(f"Entrée créée : {name}, {amount}, {category or 'Aucune catégorie'}")



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
        csv_output = services.export_to_csv()  # Récupère les données CSV en mémoire
        with open(output, "w", encoding="utf-8") as f:
            f.write(csv_output.getvalue())  # Écrit uniquement dans le fichier
        click.echo(f"Donnees exportees dans '{output}'")
    except Exception as e:
        click.echo(f"Erreur lors de l'exportation CSV : {str(e)}")




@cli.command(name="import-csv")
@click.argument("csv_file", type=click.File("rb"))  # Mode binaire
def import_csv_cli(csv_file):
    """
    Commande CLI pour importer des entrées depuis un fichier CSV.
    """
    try:
        # Lire le contenu du fichier en mode binaire et passer le flux à la fonction import_from_csv
        import_from_csv(io.BytesIO(csv_file.read()))  # Utilisation du mode binaire
        click.echo("Importation du fichier CSV réussie")
    except Exception as e:
        click.echo(f"Erreur lors de l'importation : {str(e)}")
