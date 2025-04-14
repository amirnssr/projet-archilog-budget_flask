import csv
import io

from archilog.models import Entry, create_entry, get_all_entries


def import_from_csv(csv_file: io.BytesIO) -> None:
    try:
       
        csv_reader = csv.DictReader(io.TextIOWrapper(csv_file, encoding='utf-8'))
        
        for row in csv_reader:
            name = row.get("name")
            amount = row.get("amount")
            category = row.get("category")
            
            if name and amount: 
                try:
                    amount = float(amount)  
                    create_entry(name, amount, category)  
                except ValueError:
                    print(f"Erreur : Montant invalide pour {row}")
            else:
                print(f"Erreur : Ligne invalide dans le CSV {row}")
    except Exception as e:
        print(f"Erreur lors de l'importation du CSV : {str(e)}")
        
        
        
        
      
def export_to_csv() -> io.StringIO:
    output = io.StringIO()
    csv_writer = csv.DictWriter(
        output, fieldnames=["name", "amount", "category"]
    )
    csv_writer.writeheader()

    entries = get_all_entries()
    for entry in entries:
        if isinstance(entry, Entry):
            entry_dict = {
                "name": entry.name,
                "amount": entry.amount,
                "category": entry.category
            }
            csv_writer.writerow(entry_dict)
    
    return output