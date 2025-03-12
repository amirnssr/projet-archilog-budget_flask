
import csv
import io
import dataclasses
from flask import Response
from archilog.models import create_entry, get_all_entries, Entry

def export_to_csv() -> io.StringIO:
    """
    Exporte toutes les entrees de la base de donnees au format CSV.
    """
    output = io.StringIO()
    csv_writer = csv.DictWriter(
        output, fieldnames=[f.name for f in dataclasses.fields(Entry)]
    )
    
    csv_writer.writeheader()  # Ecriture des noms de colonnes

    for entry in get_all_entries():
        csv_writer.writerow(dataclasses.asdict(entry))  # Convertit l'objet en dictionnaire

    output.seek(0)  # Remet le curseur au debut du fichier CSV
    return output

def import_from_csv(csv_file: io.StringIO) -> None:
    csv_reader = csv.DictReader(
        csv_file, fieldnames=[f.name for f in dataclasses.fields(Entry)]
    )
    next(csv_reader)
    for row in csv_reader:
        create_entry(
            name=row["name"],
            amount=float(row["amount"]),
            category=row["category"],
        )
