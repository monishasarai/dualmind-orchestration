"""
Semantic Scholar Tool
Searches academic papers across all disciplines with citation metrics.
More comprehensive than ArXiv - covers 200M+ papers.
"""

import requests
import logging
from typing import Dict, Any, List

class SemanticScholarTool:
    """Tool for searching academic papers using Semantic Scholar API."""
    
    def __init__(self):
        """Initialize the Semantic Scholar tool."""
        self.base_url = "https://api.semanticscholar.org/graph/v1"
        self.logger = logging.getLogger(__name__)
        self.max_results = 10
    
    def search_papers(self, query: str, limit: int = None) -> List[Dict[str, Any]]:
        """
        Search for academic papers using Semantic Scholar API.
        
        Args:
            query (str): Search query
            limit (int): Maximum number of results (default: 10)
            
        Returns:
            List[Dict]: List of papers with metadata
        """
        if limit is None:
            limit = self.max_results
            
        try:
            endpoint = f"{self.base_url}/paper/search"
            params = {
                "query": query,
                "limit": min(limit, 100),  # API limit
                "fields": "title,authors,year,citationCount,influentialCitationCount,abstract,url,venue,publicationDate,paperId"
            }
            
            self.logger.info(f"Searching Semantic Scholar for: {query}")
            response = requests.get(endpoint, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            papers = data.get("data", [])
            
            if not papers:
                self.logger.warning(f"No papers found for query: {query}")
                return []
            
            self.logger.info(f"Found {len(papers)} papers on Semantic Scholar")
            return papers
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error searching Semantic Scholar: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error in Semantic Scholar search: {e}")
            return []
    
    def format_papers(self, papers: List[Dict[str, Any]], query: str) -> str:
        """
        Format papers into a readable string.
        
        Args:
            papers (List[Dict]): List of paper dictionaries
            query (str): Original search query
            
        Returns:
            str: Formatted paper information
        """
        # Handle None or empty list
        if papers is None or not papers:
            return f"No papers found on Semantic Scholar for query: '{query}'"
        
        result = f"## 🎓 Semantic Scholar Results for '{query}'\n\n"
        result += f"Found {len(papers)} highly-cited papers across all academic disciplines:\n\n"
        
        for i, paper in enumerate(papers, 1):
            title = paper.get('title', 'Untitled')
            authors = paper.get('authors', [])
            author_names = ', '.join([a.get('name', 'Unknown') for a in authors[:3]])
            if len(authors) > 3:
                author_names += f" et al. ({len(authors)} total)"
            
            year = paper.get('year', 'N/A')
            citations = paper.get('citationCount', 0)
            influential_citations = paper.get('influentialCitationCount', 0)
            abstract = paper.get('abstract', 'No abstract available')
            venue = paper.get('venue', 'Unknown venue')
            url = paper.get('url', '')
            paper_id = paper.get('paperId', '')
            
            # Truncate abstract if too long
            if len(abstract) > 400:
                abstract = abstract[:400] + "..."
            
            result += f"### {i}. **{title}**\n\n"
            result += f"- **Authors**: {author_names}\n"
            result += f"- **Year**: {year}\n"
            result += f"- **Venue**: {venue}\n"
            result += f"- **Citations**: {citations} total, {influential_citations} influential\n"
            result += f"- **Impact Score**: {influential_citations / max(citations, 1) * 100:.1f}% influential\n"
            result += f"- **Semantic Scholar ID**: {paper_id}\n"
            result += f"- **URL**: {url}\n\n"
            result += f"**Abstract**: {abstract}\n\n"
            result += "---\n\n"
        
        # Add summary statistics
        total_citations = sum(p.get('citationCount', 0) for p in papers)
        avg_citations = total_citations / len(papers) if papers else 0
        
        result += f"**Summary Statistics**:\n"
        result += f"- Total papers: {len(papers)}\n"
        result += f"- Total citations: {total_citations:,}\n"
        result += f"- Average citations per paper: {avg_citations:.1f}\n"
        result += f"- Most cited: {max((p.get('citationCount', 0) for p in papers), default=0):,} citations\n"
        
        return result
    
    def run(self, query: str) -> str:
        """
        Main method to run the Semantic Scholar search tool.
        
        Args:
            query (str): Search query
            
        Returns:
            str: Formatted search results
        """
        try:
            papers = self.search_papers(query)
            # Ensure papers is a list, not None
            if papers is None:
                papers = []
            return self.format_papers(papers, query)
        except Exception as e:
            self.logger.error(f"Error in Semantic Scholar run: {e}")
            return f"Error searching Semantic Scholar for '{query}': {str(e)}"


def semantic_scholar_tool(query: str) -> str:
    """
    Standalone function for Semantic Scholar tool.
    
    Args:
        query (str): Search query
        
    Returns:
        str: Formatted search results
    """
    tool = SemanticScholarTool()
    return tool.run(query)
