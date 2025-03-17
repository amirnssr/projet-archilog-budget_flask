
import dataclasses
from flask import Response
from archilog.models import create_entry, get_all_entries, Entry
from archilog.models import db, Entry
import csv
from io import StringIO





def import_from_csv(file_stream):
    try:
        reader = csv.DictReader(file_stream)  # Lire le fichier CSV
        for row in reader:
            new_entry = Entry(
                name=row['name'],  # Assurez-vous que les noms des colonnes correspondent
                amount=float(row['amount']),  # Conversion des montants en float
                category=row['category']
            )
            db.session.add(new_entry)  # Ajouter à la session de la base de données
        db.session.commit()  # Commit des données dans la base
    except Exception as e:
        raise Exception(f"Erreur d'importation CSV : {str(e)}")
    
    
def export_to_csv():
    entries = Entry.query.all()

    output = StringIO()
    writer = csv.writer(output)

    # Écrire les en-têtes
    writer.writerow(['ID', 'Nom', 'Montant', 'Catégorie'])

    # Écrire les données
    for entry in entries:
        writer.writerow([entry.id, entry.name, entry.amount, entry.category])

    output.seek(0)
    return output