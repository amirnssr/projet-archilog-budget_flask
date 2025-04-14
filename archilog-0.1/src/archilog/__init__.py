import logging
import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()
@dataclass
class Config:
    DATABASE_URL: str
    DEBUG: bool
    SECRET_KEY: str 

config = Config(
    DATABASE_URL=os.getenv("ARCHILOG_DATABASE_URL", 'sqlite:///data.db'),
    DEBUG=os.getenv("ARCHILOG_DEBUG", "False") == "True",
    SECRET_KEY=os.getenv("SECRET_KEY", "dev-secret-key")  
)


logging.basicConfig(
    level=logging.DEBUG,  
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),  
        logging.FileHandler("app_config.log")  
    ]
)


logging.debug(f"Chargement de la configuration - DATABASE_URL: {config.DATABASE_URL}, DEBUG: {config.DEBUG}")

DEBUG = config.DEBUG == 'True' 

logging.debug(f"Valeur de DEBUG après conversion : {DEBUG}")



logging.info(f"Configuration chargée : {config}")

if not config.DATABASE_URL:
    logging.warning("La variable d'environnement DATABASE_URL est vide ou manquante.")