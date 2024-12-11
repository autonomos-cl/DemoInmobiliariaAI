import os
import json
import requests
from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from dotenv import load_dotenv

load_dotenv()

class SearchInput(BaseModel):
    """Input for SerperSearch."""
    query: str = Field(..., description="The search query to look up.")

class SerperSearchTool(BaseTool):
    name: str = "Serper Search"
    description: str = (
        "A tool for performing internet searches using Serper API. "
        "Useful for finding current information about real estate markets, "
        "property trends, and legal regulations."
    )
    args_schema: Type[BaseModel] = SearchInput

    def _run(self, query: str) -> str:
        """Execute the search query."""
        api_key = os.getenv('SERPER_API_KEY')
        if not api_key:
            raise ValueError("Serper API key not found in environment variables")

        headers = {
            'X-API-KEY': api_key,
            'Content-Type': 'application/json'
        }
        
        payload = json.dumps({"q": query})
        response = requests.post(
            'https://google.serper.dev/search',
            headers=headers,
            data=payload
        )
        
        if response.status_code != 200:
            raise Exception(f'Request failed with status code: {response.status_code}')

        try:
            results = response.json()
            
            # Format the results
            formatted_results = []
            
            # Add organic results
            if 'organic' in results:
                for result in results['organic'][:5]:  # Limit to top 5 results
                    formatted_results.append(
                        f"Title: {result.get('title', 'N/A')}\n"
                        f"Snippet: {result.get('snippet', 'N/A')}\n"
                        f"Link: {result.get('link', 'N/A')}\n"
                    )
            
            # Add news results if available
            if 'news' in results and results['news']:
                formatted_results.append("\nRelevant News:")
                for news in results['news'][:3]:  # Limit to top 3 news items
                    formatted_results.append(
                        f"Title: {news.get('title', 'N/A')}\n"
                        f"Date: {news.get('date', 'N/A')}\n"
                        f"Snippet: {news.get('snippet', 'N/A')}\n"
                        f"Link: {news.get('link', 'N/A')}\n"
                    )
            
            return "\n\n".join(formatted_results)
            
        except Exception as e:
            return f"Error processing search results: {str(e)}"
