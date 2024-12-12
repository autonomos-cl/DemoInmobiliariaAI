from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
import PyPDF2
import mimetypes

class FileAnalyzer:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("No se encontró OPENAI_API_KEY en el archivo .env")
        os.environ['OPENAI_API_KEY'] = self.api_key

    def _read_file_content(self, file_path):
        """Lee el contenido del archivo según su tipo"""
        mime_type, _ = mimetypes.guess_type(file_path)
        
        try:
            if mime_type == 'application/pdf':
                # Leer PDF
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    content = ""
                    for page in pdf_reader.pages:
                        content += page.extract_text() + "\n"
                    return content
            elif mime_type and mime_type.startswith('text/'):
                # Leer archivos de texto
                with open(file_path, 'r', encoding='utf-8') as file:
                    return file.read()
            else:
                # Para otros tipos de archivo, usar solo el nombre
                return os.path.basename(file_path)
        except Exception as e:
            print(f"Advertencia al leer archivo: {str(e)}")
            return os.path.basename(file_path)

    def analyze_file(self, file_path):
        """Analiza el contenido y sugiere ubicación y nombre"""
        file_name = os.path.basename(file_path)
        content = self._read_file_content(file_path)
        
        llm = ChatOpenAI(model='gpt-4')
        
        prompt = f"""
        Analiza el siguiente archivo:
        Nombre original: {file_name}
        Contenido/Extracto: {content[:1000]}...

        Basado en el contenido y nombre, determina:
        1. La carpeta más apropiada entre las siguientes opciones:
           - Documentos (para documentos generales)
           - Legal (para contratos, acuerdos, documentos legales)
           - Mercado (para análisis de mercado, estudios, reportes)
           - Informes Generados (para informes y reportes generados internamente)

        2. Un nombre estructurado para el archivo que siga este formato:
           [tipo_documento]_[categoria]_[descripcion].[extension]
           Ejemplo: contrato_legal_arrendamiento_local_comercial.pdf

        Formato de respuesta:
        carpeta: [nombre de la carpeta]
        nombre: [nombre estructurado del archivo]
        razón: [explicación breve de la decisión]
        """
        
        response = llm.invoke(prompt)
        
        # Parsear resultado
        lines = response.content.split('\n')
        result = {}
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                result[key.strip()] = value.strip()
        
        # Asegurar que la extensión sea la misma que el archivo original
        if 'nombre' in result:
            original_ext = os.path.splitext(file_name)[1]
            new_name = os.path.splitext(result['nombre'])[0] + original_ext
            result['nombre'] = new_name
                
        return result 