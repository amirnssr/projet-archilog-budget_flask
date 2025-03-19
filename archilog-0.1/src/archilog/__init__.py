import os
from dataclasses import dataclass
from dotenv import load_dotenv
import logging

# Charger les variables d'environnement
load_dotenv()
@dataclass
class Config:
    DATABASE_URL: str
    DEBUG: bool
    SECRET_KEY: str  # ✅ Ajout de SECRET_KEY

config = Config(
    DATABASE_URL=os.getenv("ARCHILOG_DATABASE_URL", 'sqlite:////data.db'),
    DEBUG=os.getenv("ARCHILOG_DEBUG", "False") == "True",
    SECRET_KEY=os.getenv("SECRET_KEY", "dev-secret-key")  # ✅ Définition de SECRET_KEY
)


# Configurer le logging
logging.basicConfig(
    level=logging.DEBUG,  # Niveau de log global, tu peux le configurer à DEBUG ou INFO
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),  # Afficher les logs dans la console
        logging.FileHandler("app_config.log")  # Enregistrer les logs dans un fichier 'app_config.log'
    ]
)


# Log des variables d'environnement chargées
logging.debug(f"Chargement de la configuration - DATABASE_URL: {config.DATABASE_URL}, DEBUG: {config.DEBUG}")

# Convertir DEBUG en booléen
DEBUG = config.DEBUG == 'True'  # Si ARCHILOG_DEBUG est 'True', alors DEBUG sera True, sinon False

# Log de la conversion du DEBUG
logging.debug(f"Valeur de DEBUG après conversion : {DEBUG}")



# Log de la configuration finale
logging.info(f"Configuration chargée : {config}")

# Optionnel : Log de la base de données si elle est vide
if not config.DATABASE_URL:
    logging.warning("La variable d'environnement DATABASE_URL est vide ou manquante.")