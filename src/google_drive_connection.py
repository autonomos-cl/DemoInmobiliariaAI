from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import os.path
import pickle
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/drive.metadata.readonly'
]

def get_google_drive_service():
    creds = None
    credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
    
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # Si no hay credenciales válidas disponibles, el usuario debe iniciar sesión
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_file, SCOPES)
            creds = flow.run_local_server(port=8080)
        
        # Guarda las credenciales para la próxima ejecución
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    # Construye el servicio
    service = build('drive', 'v3', credentials=creds)
    return service 