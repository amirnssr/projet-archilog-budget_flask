import csv
import io
from archilog.models import Entry 
from archilog.models import create_entry
from archilog.models import get_all_entries

def import_from_csv(csv_file: io.BytesIO) -> None:
    """Importer des entrées depuis un fichier CSV"""
    try:
        csv_reader = csv.DictReader(io.TextIOWrapper(csv_file, encoding='utf-8'))
        
        for row in csv_reader:
            name = row.get("name")
            amount = row.get("amount")
            category = row.get("category")
            
            if name and amount:  # Assurez-vous que les valeurs sont valides
                try:
                    amount = float(amount)  # Convertir le montant en float
                    create_entry(name, amount, category)  # Appeler la fonction pour insérer dans la base
                except ValueError:
                    print(f"Erreur : Montant invalide pour {row}")
            else:
                print(f"Erreur : Ligne invalide dans le CSV {row}")
    except Exception as e:
        print(f"Erreur lors de l'importation du CSV : {str(e)}")

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