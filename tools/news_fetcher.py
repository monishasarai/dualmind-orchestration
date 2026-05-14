"""
News Fetcher Tool
Fetches latest news articles using TheNewsAPI.
"""

import requests
import json
import logging
import os
from typing import List, Dict, Any
from datetime import datetime, timedelta

class NewsFetcher:
    """Tool for fetching news articles from TheNewsAPI."""

    def __init__(self):
        """Initialize the News fetcher."""
        self.api_key = os.getenv('THENEWSAPI_KEY') or os.getenv('NEWSAPI_KEY', 'demo_key')
        self.base_url = "https://api.thenewsapi.com/v1/news/all"
        self.logger = logging.getLogger(__name__)

        # Demo articles for when API key is not available
        self.demo_articles = [
            {
                'title': 'AI Breakthrough in Climate Research Announced',
                'snippet': 'Scientists develop new machine learning model to predict climate patterns with unprecedented accuracy.',
                'source': {'name': 'TechCrunch'},
                'published_at': datetime.now().isoformat(),
                'url': 'https://example.com/ai-climate-news',
                'language': 'en'
            },
            {
                'title': 'Breakthrough in Quantum Computing Research',
                'snippet': 'Researchers achieve quantum supremacy milestone with new experimental processor.',
                'source': {'name': 'Nature'},
                'published_at': datetime.now().isoformat(),
                'url': 'https://example.com/quantum-news',
                'language': 'en'
            },
            {
                'title': 'Machine Learning Transforms Healthcare Industry',
                'snippet': 'AI-powered diagnostic tools show 95% accuracy in early disease detection.',
                'source': {'name': 'MIT Technology Review'},
                'published_at': datetime.now().isoformat(),
                'url': 'https://example.com/ml-healthcare-news',
                'language': 'en'
            }
        ]

    def fetch_news(self, keyword: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Fetch news articles based on keyword using TheNewsAPI.

        Args:
            keyword (str): Keyword to search for
            max_results (int): Maximum number of results (max 100)

        Returns:
            List[Dict[str, Any]]: List of news articles with source, title, and URL
        """
        # If using demo key, return mock data
        if self.api_key == 'demo_key' or not self.api_key:
            self.logger.warning("Using demo news data - please set THENEWSAPI_KEY in .env file")
            return self._get_demo_articles(keyword, max_results)

        try:
            # Prepare request parameters for TheNewsAPI
            params = {
                'api_token': self.api_key,
                'search': keyword,
                'limit': min(max_results, 100),  # Ensure we don't exceed API limits
                'language': 'en',
                'search_fields': 'title,description,content',
                'sort': 'relevance',
                'published_after': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%S')
            }

            headers = {
                'Accept': 'application/json'
            }

            response = requests.get(
                self.base_url,
                params=params,
                headers=headers,
                timeout=15
            )
            response.raise_for_status()

            data = response.json()
            
            # Transform TheNewsAPI response to match expected format
            articles = []
            if 'data' in data and isinstance(data['data'], list):
                for item in data['data']:
                    article = {
                        'title': item.get('title', 'No title'),
                        'description': item.get('snippet', ''),
                        'source': {'name': item.get('source', {}).get('name', 'Unknown')},
                        'publishedAt': item.get('published_at', datetime.now().isoformat()),
                        'url': item.get('url', ''),
                        'urlToImage': item.get('image_url', ''),
                        'content': item.get('content', '')
                    }
                    articles.append(article)
                
                return articles[:max_results]
            else:
                self.logger.error(f"Unexpected API response format: {data}")
                return self._get_demo_articles(keyword, max_results)

        except requests.RequestException as e:
            self.logger.error(f"Error fetching news from TheNewsAPI: {e}")
            return self._get_demo_articles(keyword, max_results)
        except Exception as e:
            self.logger.error(f"Unexpected error in news fetcher: {e}")
            return self._get_demo_articles(keyword, max_results)

    def _get_demo_articles(self, keyword: str, max_results: int) -> List[Dict[str, Any]]:
        """Get demo articles for demonstration purposes."""
        # Always return a consistent format
        result = []
        for article in self.demo_articles[:max_results]:
            # Ensure article is a dictionary
            if not isinstance(article, dict):
                self.logger.warning(f"Invalid article format: {article}, skipping")
                continue
                
            result.append({
                'title': article.get('title', 'No title'),
                'description': article.get('snippet', 'No description available'),
                'source': article.get('source', {'name': 'Demo Source'}) if isinstance(article.get('source'), dict) else {'name': 'Demo Source'},
                'publishedAt': article.get('published_at', datetime.now().isoformat()),
                'url': article.get('url', ''),
                'content': article.get('snippet', '')  # Use snippet as content for demo
            })
        return result

    def run(self, keyword: str, max_results: int = 5) -> Dict[str, Any]:
        """
        Main method to run the news fetcher tool.

        Args:
            keyword (str): Keyword to search for
            max_results (int): Maximum number of results

        Returns:
            Dict[str, Any]: Structured news data
        """
        try:
            articles = self.fetch_news(keyword, max_results)
            
            if not articles:
                return {
                    'status': 'success',
                    'data': [],
                    'message': f'No news articles found for keyword: {keyword}'
                }

            # Format the response in a consistent structure
            formatted_articles = []
            for article in articles:
                formatted_article = {
                    'title': article.get('title', 'Untitled'),
                    'source': article.get('source', {}).get('name', 'Unknown'),
                    'published_at': article.get('publishedAt', ''),
                    'description': article.get('description', ''),
                    'url': article.get('url', ''),
                    'content': article.get('content', '')
                }
                formatted_articles.append(formatted_article)

            return {
                'status': 'success',
                'data': formatted_articles,
                'count': len(formatted_articles),
                'query': keyword
            }
            
        except Exception as e:
            self.logger.error(f"Error in news fetcher run method: {str(e)}")
            return {
                'status': 'error',
                'message': f'Failed to fetch news: {str(e)}',
                'data': []
            }


def news_fetcher_tool(keyword: str, max_results: int = 5) -> Dict[str, Any]:
    """
    Standalone function for news fetcher tool.

    Args:
        keyword (str): Keyword to search for
        max_results (int): Maximum number of results

    Returns:
        Dict[str, Any]: Structured news data
    """
    fetcher = NewsFetcher()
    return fetcher.run(keyword, max_results)
