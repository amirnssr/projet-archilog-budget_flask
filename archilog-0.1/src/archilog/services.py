import csv
import io
from archilog.models import Entry 
from archilog.models import create_entry
from archilog.models import get_all_entries

def import_from_csv(csv_file: io.BytesIO) -> None:
    """Importer des entrées depuis un fichier CSV"""
    # Ouvrir le fichier CSV et le lire ligne par ligne
    csv_reader = csv.DictReader(
        io.TextIOWrapper(csv_file, encoding='utf-8'),  # Utiliser TextIOWrapper pour lire le fichier en texte
        fieldnames=["name", "amount", "category"]
    )

    next(csv_reader)  # Ignorer la première ligne (les en-têtes)

    # Lire chaque ligne du fichier CSV et insérer dans la base de données
    for row in csv_reader:
        try:
            create_entry(
                name=row["name"],
                amount=float(row["amount"]),  # Convertir la chaîne en float
                category=row["category"]
            )
        except ValueError:
            # Si une erreur de format survient (par exemple, une valeur non convertible en float)
            print(f"Erreur de format dans la ligne: {row}")


def export_to_csv() -> io.StringIO:
    output = io.StringIO()
    # Exclure l'ID des champs à exporter
    csv_writer = csv.DictWriter(
        output, fieldnames=["name", "amount", "category"]
    )
    csv_writer.writeheader()
    
    entries = get_all_entries()
    for entry in entries:
        if isinstance(entry, Entry):
            # Créer un dictionnaire sans l'ID
            entry_dict = {
                "name": entry.name,
                "amount": entry.amount,
                "category": entry.category
            }
            csv_writer.writerow(entry_dict)
    
    with open('entries.csv', 'w', newline='', encoding='utf-8') as file:
        file.write(output.getvalue())
    
    return output