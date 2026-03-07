import os
from tavily import TavilyClient
from typing import List, Dict
from app.core.config import settings

class SearchService:
    def __init__(self):
        # We look for TAVILY_API_KEY in the environment
        self.api_key = os.environ.get("TAVILY_API_KEY")
        if self.api_key:
            self.client = TavilyClient(api_key=self.api_key)
        else:
            self.client = None

    def search(self, query: str, max_results: int = 5) -> str:
        """
        Perform a live web search using Tavily (Optimized for AI).
        """
        print(f"WEB SEARCH: Searching for: {query}")
        
        if not self.client:
            return "Web search is disabled. TAVILY_API_KEY not found in environment."

        try:
            # search_depth="advanced" ensures we find specific data like past prices
            results = self.client.search(query, max_results=max_results, search_depth="advanced")
            
            if not results or not results.get('results'):
                return "No web search results found for this query."

            formatted_results = []
            for i, res in enumerate(results['results']):
                title = res.get('title', 'No Title')
                snippet = res.get('content', 'No Content')
                link = res.get('url', 'No Link')
                formatted_results.append(f"<web_source name=\"{title}\" url=\"{link}\">\n{snippet}\n</web_source>")

            return "\n\n".join(formatted_results)
            
        except Exception as e:
            print(f"WEB SEARCH: Error during search: {e}")
            return f"Error performing web search: {str(e)}"

search_service = SearchService()
