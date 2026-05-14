"""
Wikipedia Search Tool
Retrieves brief summaries from Wikipedia using the Wikipedia API.
"""

import logging
import json
import re
import urllib.parse
from typing import Dict, Any, Optional, List

import requests

class WikipediaSearch:
    """Tool for searching and retrieving Wikipedia content."""

    def __init__(self):
        """Initialize the Wikipedia search tool."""
        self.base_url = "https://en.wikipedia.org/api/rest_v1/page/summary"
        self.search_url = "https://en.wikipedia.org/w/api.php"
        self.logger = logging.getLogger(__name__)

    def get_closest_title(self, query: str) -> Optional[str]:
        """Search for a topic and return the most relevant Wikipedia title."""
        try:
            params = {
                'action': 'opensearch',
                'search': query,
                'limit': 1,
                'namespace': 0,
                'format': 'json'
            }

            headers = {
                'User-Agent': 'DualMind-Orchestrator/1.0 (Research Tool)'
            }

            response = requests.get(self.search_url, params=params, headers=headers, timeout=10)
            response.raise_for_status()

            results = response.json()
            if results and len(results) >= 2 and results[1]:
                return results[1][0]  # The best matching article title

        except Exception as e:
            self.logger.error(f"Error in Wikipedia title search: {e}")

        return None


    def search_page(self, topic: str) -> Dict[str, Any]:
        """Search for a topic on Wikipedia with prompt-aware fallbacks."""
        clean_topic = self._preprocess_query(topic)

        if not clean_topic:
            return self._get_fallback_summary(topic)

        search_variants = self._build_search_variants(clean_topic)
        last_result: Optional[Dict[str, Any]] = None

        for variant in search_variants:
            result = self._fetch_summary(variant)
            if result.get('success'):
                return result
            last_result = result

        fallback_topic = (
            (last_result or {}).get('title')
            or self._extract_keywords(clean_topic)
            or clean_topic
        )
        return self._get_fallback_summary(fallback_topic)

    def _candidate_titles(self, phrase: str, limit: int = 5) -> List[str]:
        """Return a list of possible Wikipedia titles for a phrase."""
        titles: List[str] = []

        # Direct attempt first
        if phrase:
            titles.append(phrase)

        # Use opensearch to get additional suggestions
        try:
            params = {
                'action': 'opensearch',
                'search': phrase,
                'limit': limit,
                'namespace': 0,
                'format': 'json'
            }
            headers = {
                'User-Agent': 'DualMind-Orchestrator/1.0 (Research Tool)'
            }
            res = requests.get(self.search_url, params=params, headers=headers, timeout=10)
            res.raise_for_status()
            data = res.json()
            if isinstance(data, list) and len(data) >= 2:
                for title in data[1]:
                    if title and title not in titles:
                        titles.append(title)
        except Exception as e:
            self.logger.debug(f"opensearch failed for '{phrase}': {e}")

        return titles[:limit]

    def _try_summary(self, title: str) -> Dict[str, Any]:
        """Attempt to fetch a summary for a single title."""
        encoded_title = urllib.parse.quote(title.replace(' ', '_'))
        url = f"{self.base_url}/{encoded_title}"
        headers = {'User-Agent': 'DualMind-Orchestrator/1.0 (Research Tool)'}
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Skip disambiguation pages
            if data.get('type') == 'disambiguation':
                return {'success': False, 'title': title, 'error': 'disambiguation'}

            return {
                'title': data.get('title', title),
                'extract': data.get('extract', 'No summary available'),
                'url': data.get('content_urls', {}).get('desktop', {}).get('page', f'https://en.wikipedia.org/wiki/{encoded_title}'),
                'thumbnail': data.get('thumbnail', {}).get('source', '') if 'thumbnail' in data else '',
                'success': True
            }
        except Exception as e:
            # Log at debug to avoid spam; we'll try other titles
            self.logger.debug(f"Summary fetch failed for '{title}': {e}")
            return {'success': False, 'title': title, 'error': 'request_failed'}

    def _fetch_summary(self, search_phrase: str) -> Dict[str, Any]:
        """Fetch summary using multiple candidate titles until success."""
        for candidate in self._candidate_titles(search_phrase):
            result = self._try_summary(candidate)
            if result.get('success'):
                return result
        # If none succeeded, return the last attempt info
        return result

    def _preprocess_query(self, query: str) -> str:
        """Preprocess and clean the query to remove problematic characters."""
        if not query:
            return ""
        
        # Remove newlines and other problematic whitespace
        cleaned = query.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        
        # Remove multiple spaces and trim
        cleaned = ' '.join(cleaned.split())
        
        # Remove any non-printable characters except spaces
        cleaned = ''.join(char for char in cleaned if char.isprintable() or char == ' ')
        
        return cleaned.strip()

    def _build_search_variants(self, clean_topic: str) -> List[str]:
        """Create prompt-aware search variants for Wikipedia calls."""
        variants = []

        # Primary attempt: trimmed clean topic (avoid extremely long URLs)
        primary = clean_topic[:180]
        if primary:
            variants.append(primary)

        # Secondary attempt: keyword-focused search
        keyword_phrase = self._extract_keywords(clean_topic)
        if keyword_phrase and keyword_phrase.lower() not in {v.lower() for v in variants}:
            variants.append(keyword_phrase)

        return variants

    def _extract_keywords(self, text: str, max_keywords: int = 6) -> str:
        """Extract a concise keyword phrase from the prompt."""
        tokens = re.findall(r"[A-Za-z0-9\-']+", text.lower())
        stopwords = {
            'the', 'and', 'or', 'for', 'with', 'about', 'into', 'from', 'over', 'last',
            'recent', 'analysis', 'analyze', 'report', 'generate', 'summarize', 'perform',
            'comprehensive', 'investigation', 'impact', 'impacts', 'include', 'including',
            'across', 'trend', 'trends', 'data', 'visualize', 'visualization', 'societal',
            'study', 'studies', 'research', 'information', 'create', 'detailed', 'latest'
        }

        keywords: List[str] = []
        for token in tokens:
            if token in stopwords:
                continue
            if token.isdigit():
                continue
            if token not in keywords:
                keywords.append(token)
            if len(keywords) >= max_keywords:
                break

        return ' '.join(keywords)

    def _get_fallback_summary(self, topic: str) -> Dict[str, Any]:
        """Get a fallback summary when API fails."""
        fallback_summaries = {
            'artificial intelligence': 'Artificial Intelligence (AI) is the simulation of human intelligence processes by machines, especially computer systems. These processes include learning, reasoning, and self-correction. AI research has been highly successful in developing effective techniques for solving a wide range of problems.',
            'machine learning': 'Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed. It focuses on the development of computer programs that can access data and use it to learn for themselves.',
            'deep learning': 'Deep learning is part of a broader family of machine learning methods based on artificial neural networks. It can automatically learn representations from data without manual feature engineering.',
            'natural language processing': 'Natural language processing (NLP) is a subfield of linguistics, computer science, and artificial intelligence concerned with the interactions between computers and human language.',
            'computer vision': 'Computer vision is an interdisciplinary field that deals with how computers can gain high-level understanding from digital images or videos. It seeks to automate tasks that the human visual system can do.',
            'robotics': 'Robotics is an interdisciplinary branch of engineering and science that includes mechanical engineering, electronic engineering, information engineering, computer science, and others.'
        }

        summary = fallback_summaries.get(topic.lower(), f'"{topic}" is a topic in computer science and technology. The Wikipedia API is currently unavailable, but this represents knowledge about the subject.')

        return {
            'title': topic,
            'extract': summary,
            'url': f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}",
            'success': False
        }

    def run(self, topic: str) -> str:
        """
        Main method to run the Wikipedia search tool.

        Args:
            topic (str): Topic to search for

        Returns:
            str: Formatted Wikipedia summary
        """
        result = self.search_page(topic)

        formatted_result = f"## {result['title']}\n\n"
        formatted_result += f"{result['extract']}\n\n"
        formatted_result += f"**Source:** [{result['url']}]({result['url']})"

        if not result['success']:
            formatted_result += "\n\n*Note: This is a fallback summary as the Wikipedia API could not be accessed.*"

        return formatted_result


def wikipedia_search_tool(topic: str) -> str:
    """
    Standalone function for Wikipedia search tool.

    Args:
        topic (str): Topic to search for

    Returns:
        str: Formatted Wikipedia summary
    """
    search = WikipediaSearch()
    return search.run(topic)