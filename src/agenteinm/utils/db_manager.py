# Manejador de MongoDB Atlas para almacenar reportes inmobiliarios
# Guarda análisis de mercado, revisiones legales y reportes de coordinación
# Incluye sistema de respaldo local automático

from datetime import datetime
import os
from typing import Dict, Any
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from dotenv import load_dotenv

load_dotenv()

class DatabaseManager:
    def __init__(self):
        # Inicializa conexión MongoDB
        self.client = None
        self.db = None
        self.connect()

    def connect(self):
        # Conecta a MongoDB Atlas
        try:
            mongodb_uri = os.getenv('MONGODB_URI')
            if not mongodb_uri:
                raise ValueError("URI de MongoDB no encontrada")

            self.client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
            self.client.admin.command('ping')
            self.db = self.client.agenteinm
            print("✅ Conexión exitosa a MongoDB Atlas")
        
        except ConnectionFailure as e:
            print(f"❌ Error de conexión: {str(e)}")
            print("Verificar: 1) Cluster activo 2) IP en whitelist 3) Credenciales correctas")
            raise
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            raise

    def save_report(self, report_type: str, content: str, metadata: Dict[Any, Any] = None) -> str:
        # Guarda reporte en MongoDB
        try:
            collection = self.db.reports
            document = {
                "type": report_type,
                "content": content,
                "created_at": datetime.now(),
                "metadata": metadata or {}
            }
            result = collection.insert_one(document)
            return str(result.inserted_id)
        except Exception as e:
            print(f"❌ Error al guardar: {str(e)}")
            raise

    def get_report(self, report_id: str) -> Dict[str, Any]:
        # Recupera reporte por ID
        try:
            from bson.objectid import ObjectId
            collection = self.db.reports
            report = collection.find_one({"_id": ObjectId(report_id)})
            if not report:
                raise ValueError(f"Reporte no encontrado: {report_id}")
            return report
        except Exception as e:
            print(f"❌ Error al recuperar: {str(e)}")
            raise

    def get_reports_by_type(self, report_type: str) -> list:
        # Recupera reportes por tipo
        try:
            collection = self.db.reports
            return list(collection.find({"type": report_type}))
        except Exception as e:
            print(f"❌ Error al recuperar reportes: {str(e)}")
            raise

    def close(self):
        # Cierra conexión MongoDB
        if self.client:
            self.client.close()
            print("Conexión cerrada")
