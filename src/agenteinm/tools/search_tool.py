# Herramienta de búsqueda web usando Serper API
# Permite a los agentes buscar información actualizada sobre mercado inmobiliario
# Retorna resultados estructurados con título, snippet y enlace

import os
import json
import requests
from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from dotenv import load_dotenv

load_dotenv()

class SearchInput(BaseModel):
    """Parámetros de búsqueda"""
    query: str = Field(..., description="Consulta de búsqueda")

class SerperSearchTool(BaseTool):
    name: str = "Serper Search"
    description: str = (
        "Búsqueda web para información inmobiliaria actualizada: "
        "mercados, tendencias, regulaciones y precios"
    )
    args_schema: Type[BaseModel] = SearchInput

    def _run(self, query: str) -> str:
        """Ejecuta búsqueda en Serper"""
        try:
            # Configuración API
            api_key = os.getenv('SERPER_API_KEY')
            if not api_key:
                raise ValueError("API key de Serper no encontrada")

            headers = {
                'X-API-KEY': api_key,
                'Content-Type': 'application/json'
            }
            
            # Ejecuta búsqueda
            payload = json.dumps({"q": query})
            response = requests.post(
                'https://google.serper.dev/search',
                headers=headers,
                data=payload
            )
            
            if response.status_code != 200:
                raise Exception(f'Error: código {response.status_code}')

            # Formatea resultados
            results = response.json()
            formatted_results = []
            
            # Resultados orgánicos
            if 'organic' in results:
                for result in results['organic'][:5]:
                    formatted_results.append(
                        f"Title: {result.get('title', 'N/A')}\n"
                        f"Snippet: {result.get('snippet', 'N/A')}\n"
                        f"Link: {result.get('link', 'N/A')}\n"
                    )
            
            # Noticias
            if 'news' in results and results['news']:
                formatted_results.append("\nRelevant News:")
                for news in results['news'][:3]:
                    formatted_results.append(
                        f"Title: {news.get('title', 'N/A')}\n"
                        f"Date: {news.get('date', 'N/A')}\n"
                        f"Snippet: {news.get('snippet', 'N/A')}\n"
                        f"Link: {news.get('link', 'N/A')}\n"
                    )
            
            return "\n\n".join(formatted_results)
            
        except Exception as e:
            return f"Error en búsqueda: {str(e)}"
