"""
Wikipedia Search Tool — DualMind v3
Fetches rich Wikipedia content using multiple strategies:
  1. REST summary API  (fast intro paragraph)
  2. Full intro section via parse API  (richer content)
  3. opensearch → REST summary  (handles alternate titles)
  4. Full-text search → REST summary  (most robust)
  5. Shorter keyword fallback
  6. Hard-coded topic fallback
"""

import logging
import re
import urllib.parse
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────────────
_UA       = "DualMind-Orchestrator/3.0 (research; contact@dualmind.ai)"
_REST     = "https://en.wikipedia.org/api/rest_v1/page/summary"
_API      = "https://en.wikipedia.org/w/api.php"
_TIMEOUT  = 14

_STOPWORDS = {
    "a","an","the","and","or","for","with","about","into","from","over",
    "last","recent","analysis","analyze","analyse","report","generate",
    "summarize","summarise","perform","comprehensive","investigation",
    "impact","impacts","include","including","across","trend","trends",
    "data","visualize","visualise","visualization","societal","study",
    "studies","research","information","create","detailed","latest",
    "please","tell","me","what","is","are","how","why","when","where",
    "give","find","show","explain","describe","list","write","make",
    "this","that","these","those","it","its","of","in","on","at","to",
    "do","does","did","can","could","would","should","will","shall",
    "chart","graph","plot","table","image","picture","photo","video",
}

_NON_ENCYCLOPEDIC = {
    "data","chart","graph","plot","table","image","news","latest news",
    "recent news","current news","this data","analyse data","analyze data",
    "create chart","make chart","summarize news","latest updates",
}

_HARDCODED: Dict[str, str] = {
    "artificial intelligence": "Artificial intelligence (AI) is the capability of computational systems to perform tasks typically associated with human intelligence, such as learning, reasoning, problem-solving, perception, and language understanding. AI is a broad field encompassing machine learning, deep learning, natural language processing, computer vision, and robotics.",
    "machine learning": "Machine learning (ML) is a field of study in artificial intelligence concerned with the development and study of statistical algorithms that can learn from data and generalise to unseen data, and thus perform tasks without explicit instructions.",
    "deep learning": "Deep learning is part of a broader family of machine learning methods based on artificial neural networks with representation learning. Learning can be supervised, semi-supervised or unsupervised.",
    "natural language processing": "Natural language processing (NLP) is an interdisciplinary subfield of computer science and linguistics. It is primarily concerned with giving computers the ability to support and manipulate human language.",
    "quantum computing": "Quantum computing is a type of computation whose operations can harness the phenomena of quantum mechanics, such as superposition, interference, and entanglement. Devices that perform quantum computations are known as quantum computers.",
    "blockchain": "A blockchain is a distributed ledger with growing lists of records (blocks) that are securely linked together via cryptographic hashes. Each block contains a cryptographic hash of the previous block, a timestamp, and transaction data.",
    "climate change": "Climate change refers to long-term shifts in temperatures and weather patterns. Such shifts can be natural, due to changes in the sun's activity or large volcanic eruptions. But since the 1800s, human activities have been the main driver of climate change.",
    "cryptocurrency": "A cryptocurrency is a digital currency designed to work through a computer network that is not reliant on any central authority, such as a government or bank, to uphold or maintain it.",
    "python programming": "Python is a high-level, general-purpose programming language. Its design philosophy emphasises code readability with the use of significant indentation. Python is dynamically typed and garbage-collected.",
    "news": "News is information about current events. This may be provided through many different media: word of mouth, printing, postal systems, broadcasting, electronic communication, or through the testimony of observers and witnesses to events.",
}


# ── HTTP helper ────────────────────────────────────────────────────────────────

def _get(url: str, params: dict = None) -> Optional[requests.Response]:
    try:
        r = requests.get(url, params=params,
                         headers={"User-Agent": _UA}, timeout=_TIMEOUT)
        r.raise_for_status()
        return r
    except Exception as e:
        logger.debug("HTTP GET failed %s: %s", url, e)
        return None


# ── Wikipedia API strategies ───────────────────────────────────────────────────

def _rest_summary(title: str) -> Optional[Dict[str, Any]]:
    """Strategy 1 — REST summary endpoint (fast, clean intro paragraph)."""
    enc = urllib.parse.quote(title.replace(" ", "_"), safe="")
    r = _get(f"{_REST}/{enc}")
    if not r:
        return None
    d = r.json()
    if d.get("type") == "disambiguation":
        return None
    extract = d.get("extract", "").strip()
    if len(extract) < 40:
        return None
    return {
        "title":     d.get("title", title),
        "extract":   extract,
        "url":       d.get("content_urls", {}).get("desktop", {}).get(
                         "page", f"https://en.wikipedia.org/wiki/{enc}"),
        "thumbnail": d.get("thumbnail", {}).get("source", "") if "thumbnail" in d else "",
        "success":   True,
        "source":    "wikipedia_rest",
    }


def _full_intro(title: str) -> Optional[str]:
    """Strategy 2 — parse API: fetch the full intro section (richer than REST)."""
    r = _get(_API, {
        "action":      "query",
        "titles":      title,
        "prop":        "extracts",
        "exintro":     True,
        "explaintext": True,
        "format":      "json",
    })
    if not r:
        return None
    pages = r.json().get("query", {}).get("pages", {})
    for page in pages.values():
        if page.get("pageid", -1) == -1:
            return None
        extract = page.get("extract", "").strip()
        if len(extract) > 100:
            return extract
    return None


def _opensearch(query: str, limit: int = 6) -> List[str]:
    """Return article titles from Wikipedia opensearch."""
    r = _get(_API, {"action": "opensearch", "search": query,
                    "limit": limit, "namespace": 0, "format": "json"})
    if not r:
        return []
    d = r.json()
    return [t for t in (d[1] if isinstance(d, list) and len(d) >= 2 else []) if t]


def _fulltext(query: str, limit: int = 4) -> List[str]:
    """Return article titles from Wikipedia full-text search."""
    r = _get(_API, {"action": "query", "list": "search",
                    "srsearch": query, "srlimit": limit, "format": "json"})
    if not r:
        return []
    return [i["title"] for i in r.json().get("query", {}).get("search", []) if i.get("title")]


def _fetch_best(title: str) -> Optional[Dict[str, Any]]:
    """Fetch REST summary, then try to enrich with full intro."""
    result = _rest_summary(title)
    if not result:
        return None
    # Try to get richer intro text
    full = _full_intro(title)
    if full and len(full) > len(result["extract"]):
        result["extract"] = full
    return result


# ── Topic extraction ───────────────────────────────────────────────────────────

def _extract_topic(raw: str) -> str:
    """Extract the encyclopedic topic from a noisy orchestrator query."""
    text = raw.strip()

    # Strip orchestrator context injection
    if "|||CONTEXT:" in text:
        text = text.split("|||CONTEXT:")[0].strip()

    # Pattern-based extraction
    patterns = [
        r"(?:about|on|for|regarding|related to|concerning)\s+(.+)",
        r"(?:what is|what are|explain|describe|define|tell me about)\s+(.+)",
        r"(?:summarize|summarise|summary of)\s+(?:the\s+)?(.+)",
        r"(?:latest|recent|current)\s+(?:news|updates?|developments?)\s+(?:on|about|in|for)?\s*(.+)",
        r"(?:research|find|search)\s+(?:on|about|for)?\s*(.+)",
        r"(?:how does|how do|how is|how are)\s+(.+?)(?:\s+work|\s+function|\s+operate)?$",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            candidate = m.group(1).strip().rstrip(".,;:?!")
            words = [w for w in candidate.lower().split() if w not in _STOPWORDS]
            if words:
                return candidate[:120]

    # Strip leading action verbs
    text = re.sub(
        r"^(?:analyse|analyze|summarize|summarise|explain|describe|research|"
        r"find|search|show|tell|give|create|generate|write|make|list|"
        r"what|how|why|when|where|get|fetch|retrieve)\s+",
        "", text, flags=re.IGNORECASE,
    ).strip()

    # Strip trailing noise
    text = re.sub(
        r"\s+(?:and|with|including|using|to)\s+(?:create|generate|make|build|"
        r"produce|visualize|visualise|plot|chart|graph|table|report|document|"
        r"pdf|image|picture|summary|overview).*$",
        "", text, flags=re.IGNORECASE,
    ).strip()

    # Trim to meaningful keywords if too long
    if len(text.split()) > 7:
        tokens = re.findall(r"[A-Za-z0-9\-']+", text)
        kw = [t for t in tokens if t.lower() not in _STOPWORDS and not t.isdigit()]
        text = " ".join(kw[:5])

    return text.strip()[:120] or raw[:80]


def _hardcoded_fallback(topic: str) -> Dict[str, Any]:
    key = topic.lower().strip()
    for k, v in _HARDCODED.items():
        if k in key or key in k:
            return {
                "title":   k.title(),
                "extract": v,
                "url":     f"https://en.wikipedia.org/wiki/{urllib.parse.quote(k.replace(' ','_'))}",
                "success": False,
                "source":  "hardcoded",
            }
    return {
        "title":   topic,
        "extract": (f'**{topic}** — Wikipedia content could not be retrieved. '
                    f'Visit: https://en.wikipedia.org/wiki/{urllib.parse.quote(topic.replace(" ","_"))}'),
        "url":     f"https://en.wikipedia.org/wiki/{urllib.parse.quote(topic.replace(' ','_'))}",
        "success": False,
        "source":  "generic_fallback",
    }


# ── Main class ─────────────────────────────────────────────────────────────────

class WikipediaSearch:

    def search_page(self, raw_query: str) -> Dict[str, Any]:
        topic = _extract_topic(raw_query)
        logger.debug("Wikipedia: raw=%r → topic=%r", raw_query[:80], topic)

        if not topic or topic.lower() in _NON_ENCYCLOPEDIC:
            return _hardcoded_fallback(topic or raw_query[:60])

        # Strategy 1 — direct title
        r = _fetch_best(topic)
        if r:
            return r

        # Strategy 2 — opensearch suggestions
        for title in _opensearch(topic):
            r = _fetch_best(title)
            if r:
                return r

        # Strategy 3 — full-text search
        for title in _fulltext(topic):
            r = _fetch_best(title)
            if r:
                return r

        # Strategy 4 — shorter keyword phrase
        tokens = [t for t in topic.split() if t.lower() not in _STOPWORDS]
        if len(tokens) >= 2:
            short = " ".join(tokens[:3])
            for title in _opensearch(short, limit=3):
                r = _fetch_best(title)
                if r:
                    return r

        logger.warning("Wikipedia: all strategies failed for %r", topic)
        return _hardcoded_fallback(topic)

    def run(self, raw_query: str) -> str:
        result = self.search_page(raw_query)

        title   = result["title"]
        extract = result["extract"]
        url     = result["url"]
        live    = result.get("success", False)

        # Format richly for the synthesizer / QA engine
        lines = [
            f"### 📖 Wikipedia: {title}",
            "",
            extract,
            "",
            f"🔗 **Read more:** [{url}]({url})",
        ]

        if not live:
            lines.append("")
            lines.append("*⚠️ Live Wikipedia data unavailable — showing cached summary.*")

        return "\n".join(lines)


# ── Standalone entry point ─────────────────────────────────────────────────────

def wikipedia_search_tool(topic: str) -> str:
    """Called by the orchestrator pipeline."""
    return WikipediaSearch().run(topic)
