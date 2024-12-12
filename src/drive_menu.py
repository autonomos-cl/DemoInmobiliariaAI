from drive_tools import DriveTools
import os
import time
from datetime import datetime
from colorama import init, Fore, Style
from file_analyzer import FileAnalyzer
from dotenv import load_dotenv

# Cargar variables de entorno al inicio
load_dotenv()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_menu():
    clear_screen()
    print("\n=== MENÚ DE GOOGLE DRIVE ===")
    print("1. Analizar estructura de Drive")
    print("2. Subir archivo")
    print("3. Monitorear cambios")
    print("4. Salir")
    print("==========================")

def print_tree_structure(structure):
    """Imprime la estructura en formato árbol simplificado y amigable"""
    init()  # Inicializa colorama
    
    print("\nEstructura de carpetas y archivos:")
    print("==================================")
    
    last_level = -1
    last_items_by_level = {}  # Para rastrear si es el último item de cada nivel
    
    # Primero, identificar los últimos items de cada nivel
    for i, item in enumerate(structure):
        level = item.count('  ')
        next_level = structure[i+1].count('  ') if i < len(structure)-1 else -1
        
        if next_level <= level:  # Es el último item de este nivel
            last_items_by_level[level] = True
        else:
            last_items_by_level[level] = False
    
    for item in structure:
        if not item.strip():
            continue
        
        level = item.count('  ')
        
        # Construir el prefijo correcto
        if level == 0:
            prefix = "┌─"
        else:
            prefix = ""
            for l in range(level):
                if l == level - 1:
                    prefix += "└─" if last_items_by_level.get(level, False) else "├─"
                else:
                    prefix += "│  " if not last_items_by_level.get(l, False) else "   "
        
        if "📁" in item:
            # Es una carpeta
            name = item.split("📁")[1].strip()
            print(f"{prefix} {Fore.BLUE}📁 {name}{Style.RESET_ALL}")
        elif "📄" in item:
            # Es un archivo
            name = item.split("📄")[1].strip()
            print(f"{prefix} {Fore.GREEN}📄 {name}{Style.RESET_ALL}")

def analizar_estructura():
    clear_screen()
    print("\n=== ANÁLISIS DE ESTRUCTURA ===")
    drive = DriveTools()
    structure = drive.get_detailed_structure()
    
    if not structure:
        print("\nNo se encontraron archivos o carpetas.")
        input("\nPresione Enter para continuar...")
        return
        
    print_tree_structure(structure)
    
    # Mostrar resumen
    total_files = sum(1 for item in structure if "📄" in item)
    total_folders = sum(1 for item in structure if "📁" in item)
    
    print("\nResumen:")
    print(f"Total de carpetas: {total_folders}")
    print(f"Total de archivos: {total_files}")
    
    input("\nPresione Enter para continuar...")

def subir_archivo():
    clear_screen()
    print("\n=== SUBIR ARCHIVO ===")
    drive = DriveTools()
    
    print("\nInstrucciones:")
    print("1. El archivo debe estar en tu computadora")
    print("2. Puedes arrastrar el archivo a esta ventana")
    print("3. O puedes escribir la ruta completa (ejemplo: C:\\Users\\nombre\\Documents\\archivo.txt)")
    
    # Solicitar ruta del archivo
    file_path = input("\nArrastre el archivo aquí o ingrese la ruta completa: ").strip('"')
    if not os.path.exists(file_path):
        print("Error: El archivo no existe")
        print("Asegúrate de que la ruta sea correcta")
        input("\nPresione Enter para continuar...")
        return
    
    print("\nAnalizando contenido del archivo...")
    try:
        analyzer = FileAnalyzer()
        analysis = analyzer.analyze_file(file_path)
        
        print("\nResultado del análisis:")
        print(f"Carpeta sugerida: {analysis['carpeta']}")
        print(f"Nombre sugerido: {analysis['nombre']}")
        print(f"Razón: {analysis['razón']}")
        
        if input("\n¿Desea proceder con las sugerencias? (s/n): ").lower() == 's':
            # Obtener ID de la carpeta sugerida
            structure = drive.get_detailed_structure()
            folder_id = None
            
            # Buscar la carpeta en la estructura
            for item in structure:
                if "📁" in item and analysis['carpeta'] in item:
                    try:
                        # Extraer el ID de la carpeta
                        folder_info = item.split("📁")[1].strip()
                        folder_id = drive.get_folder_id(analysis['carpeta'])
                        break
                    except Exception as e:
                        print(f"Error al obtener ID de carpeta: {str(e)}")
                        continue
            
            if folder_id:
                # Renombrar archivo temporalmente
                temp_path = os.path.join(os.path.dirname(file_path), analysis['nombre'])
                try:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)  # Eliminar archivo temporal si existe
                    os.rename(file_path, temp_path)
                    
                    result = drive.upload_file(temp_path, folder_id)
                    if result:
                        print(f"\nArchivo subido exitosamente:")
                        print(f"Nombre: {result['name']}")
                        print(f"Tamaño: {result['size']}")
                        print(f"Link: {result['link']}")
                    else:
                        print("\nError al subir el archivo")
                finally:
                    # Restaurar nombre original
                    if os.path.exists(temp_path):
                        os.rename(temp_path, file_path)
            else:
                print(f"\nError: No se encontró la carpeta '{analysis['carpeta']}'")
                print("Asegúrese de que la carpeta exista en Drive")
        else:
            print("\nOperación cancelada")
    except Exception as e:
        print(f"\nError al procesar el archivo: {str(e)}")
        input("\nPresione Enter para continuar...")
        return
    
    input("\nPresione Enter para continuar...")

def monitorear_cambios():
    clear_screen()
    print("\n=== MONITOREO DE CAMBIOS EN DOCUMENTOS ===")
    print("Monitoreando cambios en la carpeta Documentos (Ctrl+C para detener)...")
    
    drive = DriveTools()
    # Obtener ID de la carpeta Documentos
    structure = drive.get_detailed_structure()
    documentos_id = None
    for item in structure:
        if "📁" in item and "Documentos" in item:
            documentos_id = item.split("(ID:")[1].strip()[:-1]
            break
    
    if not documentos_id:
        print("Error: No se encontró la carpeta Documentos")
        input("\nPresione Enter para continuar...")
        return
    
    # Obtener lista inicial de archivos
    initial_files = set()
    try:
        files = drive.service.files().list(
            q=f"'{documentos_id}' in parents",
            fields="files(id, name, mimeType, createdTime, size)"
        ).execute().get('files', [])
        
        for file in files:
            initial_files.add(file['id'])
        
        print(f"\nMonitoreando la carpeta Documentos...")
        print(f"Archivos actuales: {len(initial_files)}")
        
        while True:
            time.sleep(10)  # Revisar cada 10 segundos
            current_files = drive.service.files().list(
                q=f"'{documentos_id}' in parents",
                fields="files(id, name, mimeType, createdTime, size)"
            ).execute().get('files', [])
            
            for file in current_files:
                if file['id'] not in initial_files:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"\n¡Nuevo archivo detectado! ({timestamp})")
                    print(f"Nombre: {file['name']}")
                    if 'size' in file:
                        size = int(file['size'])
                        print(f"Tamaño: {size:,} bytes")
                    print("-------------------")
                    initial_files.add(file['id'])
                    
    except KeyboardInterrupt:
        print("\nMonitoreo detenido")
        input("\nPresione Enter para continuar...")

def main():
    while True:
        print_menu()
        option = input("\nSeleccione una opción (1-4): ")
        
        if option == "1":
            analizar_estructura()
        elif option == "2":
            subir_archivo()  # Ya no necesitamos pasar la API key
        elif option == "3":
            monitorear_cambios()
        elif option == "4":
            print("\n¡Hasta luego!")
            break
        else:
            print("\nOpción inválida")
            time.sleep(1)

if __name__ == "__main__":
    main() 