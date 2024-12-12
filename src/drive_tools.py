from google_drive_connection import get_google_drive_service
from googleapiclient.http import MediaFileUpload
import os
from datetime import datetime
import time

class DriveTools:
    def __init__(self):
        self.service = get_google_drive_service()
        self.ROOT_FOLDER_ID = '1XKhfXJneRpXzca9xk0pNF0Drd4QUUnkE'  # ID de la carpeta 'demo larryin'
        
    def list_all_files_recursive(self, folder_id=None):
        """Lista todos los archivos y carpetas recursivamente"""
        if folder_id is None:
            folder_id = self.ROOT_FOLDER_ID
            
        try:
            print(f"Intentando acceder a la carpeta: {folder_id}")
            # Primero verificamos si tenemos acceso a la carpeta
            try:
                folder = self.service.files().get(
                    fileId=folder_id,
                    fields="name, id",
                    supportsAllDrives=True
                ).execute()
                print(f"Accediendo a carpeta: {folder.get('name', 'Unknown')}")
            except Exception as e:
                print(f"Error al acceder a la carpeta {folder_id}: {str(e)}")
                return []

            all_items = []
            page_token = None
            
            while True:
                try:
                    # Modificamos la consulta para incluir carpetas compartidas
                    results = self.service.files().list(
                        q=f"'{folder_id}' in parents",
                        fields="nextPageToken, files(id, name, mimeType, createdTime, modifiedTime, size, parents)",
                        pageToken=page_token,
                        pageSize=1000,
                        supportsAllDrives=True,
                        includeItemsFromAllDrives=True,
                        corpora='allDrives'  # Incluye unidades compartidas
                    ).execute()
                    
                    items = results.get('files', [])
                    print(f"Encontrados {len(items)} elementos en {folder_id}")
                    
                    for item in items:
                        all_items.append(item)
                        if item['mimeType'] == 'application/vnd.google-apps.folder':
                            print(f"Explorando subcarpeta: {item['name']}")
                            sub_items = self.list_all_files_recursive(item['id'])
                            all_items.extend(sub_items)
                    
                    page_token = results.get('nextPageToken')
                    if not page_token:
                        break
                    
                except Exception as e:
                    print(f"Error al listar contenido: {str(e)}")
                    break
                
            return all_items
        except Exception as e:
            print(f"Error general al listar archivos recursivamente: {str(e)}")
            return []

    def get_detailed_structure(self, folder_id=None, level=0):
        """Obtiene la estructura detallada con información adicional"""
        if folder_id is None:
            folder_id = self.ROOT_FOLDER_ID
            
        try:
            results = self.service.files().list(
                q=f"'{folder_id}' in parents",
                fields="files(id, name, mimeType)"
            ).execute()
            
            structure = []
            for item in results.get('files', []):
                indent = "  " * level
                if item['mimeType'] == 'application/vnd.google-apps.folder':
                    structure.append(f"{indent}📁 {item['name']}")
                    # Recursivamente obtiene el contenido de las subcarpetas
                    sub_structure = self.get_detailed_structure(item['id'], level + 1)
                    structure.extend(sub_structure)
                else:
                    structure.append(f"{indent}📄 {item['name']}")
            
            return structure
        except Exception as e:
            print(f"Error al obtener estructura: {str(e)}")
            return []

    def _format_size(self, size_bytes):
        """Formatea el tamaño de bytes a una forma legible"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f} TB"

    def upload_file(self, file_path, folder_id=None):
        """Sube un archivo a la carpeta especificada"""
        if folder_id is None:
            folder_id = self.ROOT_FOLDER_ID
            
        try:
            file_metadata = {
                'name': os.path.basename(file_path),
                'parents': [folder_id]
            }
            
            mime_type = 'application/octet-stream'
            media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink, size, createdTime'
            ).execute()
            
            size = int(file.get('size', 0))
            created_time = datetime.fromisoformat(file['createdTime'].replace('Z', '+00:00'))
            
            return {
                'id': file.get('id'),
                'name': file.get('name'),
                'link': file.get('webViewLink'),
                'size': self._format_size(size),
                'created': created_time.strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            print(f"Error al subir archivo: {str(e)}")
            return None

    def monitor_folder_recursive(self, callback=None, interval=60):
        """Monitorea recursivamente toda la estructura de carpetas"""
        known_files = set()
        
        # Obtiene la lista inicial de todos los archivos
        initial_files = self.list_all_files_recursive()
        for file in initial_files:
            known_files.add(file['id'])
        
        while True:
            try:
                current_files = self.list_all_files_recursive()
                for file in current_files:
                    if file['id'] not in known_files:
                        known_files.add(file['id'])
                        if callback:
                            callback(file)
                        else:
                            print(f"Nuevo archivo detectado: {file['name']}")
                            print(f"En carpeta: {file.get('parents', ['root'])[0]}")
                
                time.sleep(interval)
            except Exception as e:
                print(f"Error en monitoreo: {str(e)}")
                time.sleep(interval) 

    def get_folder_id(self, folder_name):
        """Obtiene el ID de una carpeta por su nombre"""
        try:
            results = self.service.files().list(
                q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'",
                fields="files(id, name)",
                spaces='drive'
            ).execute()
            
            items = results.get('files', [])
            if items:
                return items[0]['id']
            return None
        except Exception as e:
            print(f"Error al buscar carpeta: {str(e)}")
            return None 