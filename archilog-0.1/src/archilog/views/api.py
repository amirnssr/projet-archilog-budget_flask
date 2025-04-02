import uuid
from flask import Blueprint, jsonify, request
from flask_httpauth import HTTPTokenAuth
from pydantic import BaseModel, Field
from spectree import SpecTree, SecurityScheme

import archilog.models as models
import archilog.services as services

# Création du Blueprint pour l'API
api_views = Blueprint("api_views", __name__, url_prefix="/api/users")

# Configuration de Spectree
spec = SpecTree(
    "flask", 
    title="ArchiLog API",
    version="1.0.0",
    security_schemes=[
        SecurityScheme(
            name="bearer_token",
            data={"type": "http", "scheme": "bearer"}
        )
    ],
    security=[{"bearer_token": []}]
)

# Authentification par token
token_auth = HTTPTokenAuth(scheme='Bearer')

# Simulation d'une base de tokens
valid_tokens = {
    "admin_token": "admin",
    "user_token": "user"
}

@token_auth.verify_token
def verify_token(token):
    """Vérification du token"""
    if token in valid_tokens:
        return valid_tokens[token]
    return None

# Modèles de validation Pydantic
class EntryModel(BaseModel):
    name: str = Field(min_length=2, max_length=100, description="Nom de l'entrée")
    amount: float = Field(gt=0, description="Montant de l'entrée")
    category: str | None = Field(default=None, description="Catégorie optionnelle")

class EntryResponse(EntryModel):
    id: str
    
# CRUD Operations avec validation Spectree
@api_views.route('/entries', methods=['GET'])
@spec.validate(tags=["entries"])
@token_auth.login_required
def get_entries():
    """Récupérer toutes les entrées"""
    entries = models.get_all_entries()
    return jsonify([
        {
            'id': entry.id.hex,
            'name': entry.name,
            'amount': entry.amount,
            'category': entry.category
        } for entry in entries
    ])

@api_views.route('/entries', methods=['POST'])
@spec.validate(json=EntryModel, tags=["entries"])
@token_auth.login_required
def create_entry(json: EntryModel):
    """Créer une nouvelle entrée"""
    entry = models.create_entry(json.name, json.amount, json.category)
    return jsonify({
        'id': entry.id.hex,
        'name': entry.name,
        'amount': entry.amount,
        'category': entry.category
    }), 201

@api_views.route('/entries/<uuid:id>', methods=['GET'])
@spec.validate(tags=["entries"])
@token_auth.login_required
def get_entry(id: uuid.UUID):
    """Récupérer une entrée par son ID"""
    entry = models.get_entry(id)
    return jsonify({
        'id': entry.id.hex,
        'name': entry.name,
        'amount': entry.amount,
        'category': entry.category
    })

@api_views.route('/entries/<uuid:id>', methods=['PUT'])
@spec.validate(json=EntryModel, tags=["entries"])
@token_auth.login_required
def update_entry(id: uuid.UUID, json: EntryModel):
    """Mettre à jour une entrée"""
    models.update_entry(id, json.name, json.amount, json.category)
    return jsonify({
        'id': id.hex,
        'name': json.name,
        'amount': json.amount,
        'category': json.category
    })

@api_views.route('/entries/<uuid:id>', methods=['DELETE'])
@spec.validate(tags=["entries"])
@token_auth.login_required
def delete_entry(id: uuid.UUID):
    """Supprimer une entrée"""
    models.delete_entry(id)
    return '', 204

# Routes pour l'import/export CSV
@api_views.route('/export', methods=['GET'])
@spec.validate(tags=["import-export"])
@token_auth.login_required
def export_csv():
    """Exporter les données en CSV"""
    csv_content = services.export_to_csv().getvalue()
    return csv_content, 200, {
        'Content-Type': 'text/csv',
        'Content-Disposition': 'attachment; filename=entries.csv'
    }

@api_views.route('/import', methods=['POST'])
@spec.validate(tags=["import-export"])
@token_auth.login_required
def import_csv():
    """Importer des données depuis un CSV"""
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    if file.filename == '' or not file.filename.endswith('.csv'):
        return jsonify({"error": "Invalid file"}), 400
    
    try:
        stream = io.StringIO(file.stream.read().decode("UTF-8"), newline=None)
        services.import_from_csv(stream)
        return jsonify({"message": "CSV importé avec succès"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Enregistrement du schéma Spectree
def register_spec(app):
    spec.register(app)