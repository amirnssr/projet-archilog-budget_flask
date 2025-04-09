import uuid

from flask import Blueprint, jsonify, request
from flask_httpauth import HTTPTokenAuth
from pydantic import BaseModel, Field
from spectree import BaseFile, SecurityScheme, SpecTree

import archilog.models as models
import archilog.services as services

# Création du Blueprint pour l'API
api_views = Blueprint("api_views", __name__, url_prefix="/api/users")

# Configuration de Spectree pour générer la documentation OpenAPI
spec = SpecTree(
    "flask",
    title="ArchiLog API",
    version="1.0.0",
    security_schemes=[SecurityScheme(
        name="bearer_token",
        data={"type": "http", "scheme": "bearer"}
    )],
    security=[{"bearer_token": []}]
)

# Authentification par token
token_auth = HTTPTokenAuth(scheme='Bearer')

# Simulation d'une base de tokens (admin, user, etc.)
valid_tokens = {
    "admin_token": "admin",  # admin
    "user_token": "user"     # user
}

@token_auth.verify_token
def verify_token(token):
    """Vérifie si le token fourni est valide."""
    if token in valid_tokens:
        return valid_tokens[token]  # Retourne "admin" ou "user"
    return None

# Modèles de validation Pydantic
class EntryModel(BaseModel):
    """Modèle pour valider le contenu JSON des entrées."""
    name: str = Field(min_length=2, max_length=100, description="Nom de l'entrée")
    amount: float = Field(gt=0, description="Montant de l'entrée")
    category: str | None = Field(default=None, description="Catégorie optionnelle")

class EntryResponse(EntryModel):
    """Modèle de réponse pour renvoyer une entrée avec son ID."""
    id: str


#
# Routes CRUD
#
@api_views.route('/entries', methods=['GET'])
@spec.validate(tags=["entries"])
@token_auth.login_required
def get_entries():
    """Récupérer toutes les entrées."""
    current_user = token_auth.current_user()  # Vérifie le rôle de l'utilisateur

    if current_user != "admin":
        return jsonify({"error": "Accès refusé. Vous devez être admin."}), 403

    entries = models.get_all_entries()
    return jsonify([
        {
            'id': entry.id.hex,
            'name': entry.name,
            'amount': entry.amount,
            'category': entry.category
        }
        for entry in entries
    ])

@api_views.route('/entries', methods=['POST'])
@spec.validate(json=EntryModel, tags=["entries"])
@token_auth.login_required
def create_entry(json: EntryModel):
    """Créer une nouvelle entrée (admin uniquement)."""
    current_user = token_auth.current_user()  # Vérifie le rôle de l'utilisateur

    if current_user != "admin":
        return jsonify({"error": "Accès refusé. Vous devez être admin."}), 403
    
    # Création de l'entrée dans la base de données et récupération des informations
    entry = models.create_entry(json.name, json.amount, json.category)
    
    # Retourner les informations de l'entrée créée
    return jsonify({
        'id': entry['id'],
        'name': entry['name'],
        'amount': entry['amount'],
        'category': entry['category']
    }), 201

@api_views.route('/entries/<id>', methods=['GET'])
@spec.validate(tags=["entries"])
@token_auth.login_required
def get_entry(id: str):
    current_user = token_auth.current_user()  # Vérifie le rôle de l'utilisateur

    if current_user != "admin":
        return jsonify({"error": "Accès refusé. Vous devez être admin."}), 403

    try:
        # Convertir l'ID sans tirets en un UUID valide
        uuid_id = uuid.UUID(id)
        entry = models.get_entry(uuid_id)
        if not entry:
            return jsonify({"error": "Entrée introuvable"}), 404
        return jsonify({
            'id': entry.id.hex,
            'name': entry.name,
            'amount': entry.amount,
            'category': entry.category
        }), 200
    except ValueError:
        return jsonify({"error": "ID invalide, le format UUID attendu"}), 400

@api_views.route('/entries/<id>', methods=['PUT'])
@spec.validate(json=EntryModel, tags=["entries"])
@token_auth.login_required
def update_entry(id: str, json: EntryModel):
    """Mettre à jour une entrée"""
    current_user = token_auth.current_user()  # Vérifie le rôle de l'utilisateur

    if current_user != "admin":
        return jsonify({"error": "Accès refusé. Vous devez être admin."}), 403

    try:
        # Convertir l'ID sans tirets en un UUID valide
        uuid_id = uuid.UUID(id)
        models.update_entry(uuid_id, json.name, json.amount, json.category)
        return jsonify({
            'id': uuid_id.hex,
            'name': json.name,
            'amount': json.amount,
            'category': json.category
        }), 200
    except ValueError:
        return jsonify({"error": "ID invalide, le format UUID attendu"}), 400

@api_views.route('/entries/<id>', methods=['DELETE'])
@spec.validate(tags=["entries"])
@token_auth.login_required
def delete_entry(id: str):
    """Supprimer une entrée en utilisant son ID"""
    current_user = token_auth.current_user()  # Vérifie le rôle de l'utilisateur

    if current_user != "admin":
        return jsonify({"error": "Accès refusé. Vous devez être admin."}), 403

    try:
        # Convertir l'ID sans tirets en un UUID valide
        uuid_id = uuid.UUID(id)
        models.delete_entry(uuid_id)
        return jsonify({"message": "Entrée supprimée avec succès"}), 204
    except ValueError:
        return jsonify({"error": "ID invalide, le format UUID attendu"}), 400



@api_views.route('/export', methods=['GET'])
@spec.validate(tags=["import-export"])
@token_auth.login_required
def export_csv():
    csv_content = services.export_to_csv().getvalue()
    return csv_content, 200, {
        'Content-Type': 'text/csv',
        'Content-Disposition': 'attachment; filename=entries.csv'
    }
    
    


# Modèle de validation pour l'importation de fichier CSV
class CSVFileUpload(BaseModel):
    file: BaseFile  # Remplace BaseFile() par str car c'est plus adapté pour l'upload de fichiers

# Route pour importer un fichier CSV
@api_views.route("/import_csv", methods=["POST"])
@spec.validate(form=CSVFileUpload, tags=["csv"])
def import_csv_api():
    try:
        # Récupération du fichier via request.files
        file = request.files.get("file")

        if not file:
            return jsonify({"error": "Fichier manquant"}), 400

        # Traitement du fichier CSV
        services.import_from_csv(file.stream)
        return jsonify({"message": "Import réussi"}), 200
    except Exception as e:
        return jsonify({"error": "Erreur lors de l'import"}), 500



def register_spec(app):
    spec.register(app)
