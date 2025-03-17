from flask_sqlalchemy import SQLAlchemy
import uuid


db = SQLAlchemy()  # Initialisation de db avec SQLAlchemy

def init_db(app):
    """Fonction pour initialiser la base de données et créer les tables"""
    with app.app_context():
        db.create_all()  # Crée les tables dans la base de données si elles n'existent pas encore

class Entry(db.Model):
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))  # Génération automatique de l'ID
    name = db.Column(db.String, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String, nullable=True)

    def __init__(self, name, amount, category=None):
        self.name = name
        self.amount = amount
        self.category = category
# Fonction pour créer une entrée
def create_entry(name: str, amount: float, category: str | None = None) -> None:
    new_entry = Entry(name=name, amount=amount, category=category)
    db.session.add(new_entry)
    db.session.commit()

# Fonction pour obtenir une entrée par ID
def get_entry(id: uuid.UUID) -> Entry:
    entry = Entry.query.get(str(id))  # Recherche par ID
    if entry:
        return entry
    else:
        raise Exception("Entry not found")

# Fonction pour obtenir toutes les entrées
def get_all_entries() -> list[Entry]:
    return Entry.query.all()  # Récupérer toutes les entrées

# Fonction pour mettre à jour une entrée
def update_entry(id: uuid.UUID, name: str, amount: float, category: str | None) -> None:
    entry = Entry.query.get(str(id))
    if entry:
        entry.name = name
        entry.amount = amount
        entry.category = category
        db.session.commit()
    else:
        raise Exception("Entry not found")

# Fonction pour supprimer une entrée
def delete_entry(id: uuid.UUID) -> None:
    entry = Entry.query.get(str(id))
    if entry:
        db.session.delete(entry)
        db.session.commit()
    else:
        raise Exception("Entry not found")


