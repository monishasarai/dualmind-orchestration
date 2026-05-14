"""
PubMed Search Tool
Searches biomedical and life sciences literature using NCBI E-utilities API.
Access to 35M+ citations from MEDLINE and other databases.
"""

import requests
import xml.etree.ElementTree as ET
import logging
from typing import Dict, Any, List
from urllib.parse import quote

class PubMedTool:
    """Tool for searching PubMed/MEDLINE database."""
    
    def __init__(self):
        """Initialize the PubMed tool."""
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.logger = logging.getLogger(__name__)
        self.max_results = 10
    
    def search_pubmed(self, query: str, limit: int = None) -> List[str]:
        """
        Search PubMed and get article IDs.
        
        Args:
            query (str): Search query
            limit (int): Maximum number of results
            
        Returns:
            List[str]: List of PubMed IDs
        """
        if limit is None:
            limit = self.max_results
            
        try:
            # ESearch to get IDs
            esearch_url = f"{self.base_url}/esearch.fcgi"
            params = {
                "db": "pubmed",
                "term": query,
                "retmax": min(limit, 100),
                "retmode": "xml",
                "sort": "relevance"
            }
            
            self.logger.info(f"Searching PubMed for: {query}")
            response = requests.get(esearch_url, params=params, timeout=15)
            response.raise_for_status()
            
            # Parse XML response
            root = ET.fromstring(response.content)
            id_list = root.find('IdList')
            
            if id_list is None:
                self.logger.warning(f"No PubMed articles found for: {query}")
                return []
            
            pmids = [id_elem.text for id_elem in id_list.findall('Id')]
            self.logger.info(f"Found {len(pmids)} PubMed articles")
            return pmids
            
        except Exception as e:
            self.logger.error(f"Error searching PubMed: {e}")
            return []
    
    def fetch_article_details(self, pmids: List[str]) -> List[Dict[str, Any]]:
        """
        Fetch detailed information for PubMed articles.
        
        Args:
            pmids (List[str]): List of PubMed IDs
            
        Returns:
            List[Dict]: List of article details
        """
        if not pmids:
            return []
        
        try:
            # EFetch to get details
            efetch_url = f"{self.base_url}/efetch.fcgi"
            params = {
                "db": "pubmed",
                "id": ",".join(pmids),
                "retmode": "xml"
            }
            
            response = requests.get(efetch_url, params=params, timeout=20)
            response.raise_for_status()
            
            # Parse XML response
            root = ET.fromstring(response.content)
            articles = []
            
            for article_elem in root.findall('.//PubmedArticle'):
                try:
                    # Extract article information
                    medline = article_elem.find('.//MedlineCitation')
                    article_data = article_elem.find('.//Article')
                    
                    if medline is None or article_data is None:
                        continue
                    
                    # PMID
                    pmid_elem = medline.find('PMID')
                    pmid = pmid_elem.text if pmid_elem is not None else 'Unknown'
                    
                    # Title
                    title_elem = article_data.find('.//ArticleTitle')
                    title = title_elem.text if title_elem is not None else 'Untitled'
                    
                    # Authors
                    authors = []
                    author_list = article_data.find('.//AuthorList')
                    if author_list is not None:
                        for author in author_list.findall('Author'):
                            last_name = author.find('LastName')
                            fore_name = author.find('ForeName')
                            if last_name is not None:
                                name = last_name.text
                                if fore_name is not None:
                                    name = f"{fore_name.text} {name}"
                                authors.append(name)
                    
                    # Abstract
                    abstract_elem = article_data.find('.//Abstract/AbstractText')
                    abstract = abstract_elem.text if abstract_elem is not None else 'No abstract available'
                    
                    # Journal
                    journal_elem = article_data.find('.//Journal/Title')
                    journal = journal_elem.text if journal_elem is not None else 'Unknown journal'
                    
                    # Publication date
                    pub_date = article_data.find('.//Journal/JournalIssue/PubDate')
                    year = 'N/A'
                    if pub_date is not None:
                        year_elem = pub_date.find('Year')
                        year = year_elem.text if year_elem is not None else 'N/A'
                    
                    articles.append({
                        'pmid': pmid,
                        'title': title,
                        'authors': authors,
                        'abstract': abstract,
                        'journal': journal,
                        'year': year
                    })
                    
                except Exception as e:
                    self.logger.warning(f"Error parsing article: {e}")
                    continue
            
            return articles
            
        except Exception as e:
            self.logger.error(f"Error fetching PubMed details: {e}")
            return []
    
    def format_articles(self, articles: List[Dict[str, Any]], query: str) -> str:
        """
        Format articles into a readable string.
        
        Args:
            articles (List[Dict]): List of article dictionaries
            query (str): Original search query
            
        Returns:
            str: Formatted article information
        """
        # Handle None or empty list
        if articles is None or not articles:
            return f"No biomedical articles found on PubMed for query: '{query}'"
        
        result = f"## 🏥 PubMed/MEDLINE Results for '{query}'\n\n"
        result += f"Found {len(articles)} peer-reviewed biomedical articles:\n\n"
        
        for i, article in enumerate(articles, 1):
            title = article.get('title', 'Untitled')
            authors = article.get('authors', [])
            author_str = ', '.join(authors[:3])
            if len(authors) > 3:
                author_str += f" et al. ({len(authors)} total)"
            
            year = article.get('year', 'N/A')
            journal = article.get('journal', 'Unknown')
            pmid = article.get('pmid', 'Unknown')
            abstract = article.get('abstract', 'No abstract available')
            
            # Truncate abstract if too long
            if len(abstract) > 400:
                abstract = abstract[:400] + "..."
            
            result += f"### {i}. **{title}**\n\n"
            result += f"- **Authors**: {author_str}\n"
            result += f"- **Journal**: {journal}\n"
            result += f"- **Year**: {year}\n"
            result += f"- **PubMed ID**: {pmid}\n"
            result += f"- **URL**: https://pubmed.ncbi.nlm.nih.gov/{pmid}/\n\n"
            result += f"**Abstract**: {abstract}\n\n"
            result += "---\n\n"
        
        result += f"\n**Note**: These are peer-reviewed biomedical publications from the PubMed/MEDLINE database.\n"
        result += f"For full text and citations, visit the URLs above.\n"
        
        return result
    
    def run(self, query: str) -> str:
        """
        Main method to run the PubMed search tool.
        
        Args:
            query (str): Search query
            
        Returns:
            str: Formatted search results
        """
        try:
            pmids = self.search_pubmed(query)
            if pmids is None:
                pmids = []
            articles = self.fetch_article_details(pmids)
            if articles is None:
                articles = []
            return self.format_articles(articles, query)
        except Exception as e:
            self.logger.error(f"Error in PubMed run: {e}")
            return f"Error searching PubMed for '{query}': {str(e)}"


def pubmed_search_tool(query: str) -> str:
    """
    Standalone function for PubMed tool.
    
    Args:
        query (str): Search query
        
    Returns:
        str: Formatted search results
    """
    tool = PubMedTool()
    return tool.run(query)
