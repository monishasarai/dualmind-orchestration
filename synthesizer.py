"""
Answer Synthesizer — DualMind v4
Produces a rich, fully-populated response with all sections filled.
"""

import json
import logging
import re
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _to_text(val: Any) -> str:
    if isinstance(val, str):
        return val.strip()
    try:
        return json.dumps(val, ensure_ascii=False, indent=2)
    except Exception:
        return str(val).strip()


def _collect(execution_results: List[Dict[str, Any]]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for r in execution_results:
        if r.get("status") != "success":
            continue
        name = r.get("tool", "unknown")
        text = _to_text(r.get("output", ""))
        if text and not text.lower().startswith("error"):
            out[name] = text
    return out


def _collect_files(execution_results: List[Dict[str, Any]]) -> List[tuple]:
    files = []
    for r in execution_results:
        text = _to_text(r.get("output", ""))
        low = text.lower()
        if "successfully created" in low or "generated" in low:
            if ".png" in low or "chart" in low:
                files.append(("chart", text))
            elif ".pdf" in low or "pdf" in low:
                files.append(("pdf", text))
    return files


# ── Section formatters ─────────────────────────────────────────────────────────

def _fmt_arxiv(query: str, raw: str) -> str:
    if not raw or len(raw) < 30:
        return f"*No academic papers could be retrieved for **{query}** at this time.*"
    lines = raw.strip().split("\n")
    count = sum(1 for l in lines if re.match(r"^\d+\.", l.strip()))
    result = raw.strip()
    if count > 0:
        result += f"\n\n> 📌 **{count} paper(s)** retrieved from arXiv."
    return result


def _fmt_news(query: str, raw: str) -> str:
    if not raw or len(raw) < 20:
        return f"*No recent news articles found for **{query}**.*"

    # Try JSON dict (news_fetcher returns dict serialised as JSON)
    try:
        data = json.loads(raw)
        articles = data.get("data", [])
        if not articles:
            return f"*No recent news articles found for **{query}**.*"
        result = ""
        for i, art in enumerate(articles, 1):
            title  = art.get("title", "Untitled")
            source = art.get("source", "Unknown")
            desc   = (art.get("description") or art.get("content") or "")[:220]
            url    = art.get("url", "")
            pub    = (art.get("published_at") or "")[:10]
            result += f"**{i}. {title}**\n"
            result += f"   📰 *{source}*"
            if pub:
                result += f" · {pub}"
            result += "\n"
            if desc:
                result += f"   {desc}{'...' if len(desc) == 220 else ''}\n"
            if url:
                result += f"   🔗 [{url}]({url})\n"
            result += "\n"
        return result.strip()
    except (json.JSONDecodeError, TypeError):
        pass

    # Already a formatted string
    if len(raw) > 80:
        return raw.strip()
    return f"*No recent news articles found for **{query}**.*"


def _fmt_wiki(raw: str) -> str:
    return raw.strip() if raw and len(raw) > 30 else "*Wikipedia data unavailable.*"


def _key_insights(query: str, outputs: Dict[str, str]) -> str:
    bullets = []
    if "wikipedia_search"  in outputs: bullets.append("✓ **Wikipedia** — encyclopedic background retrieved")
    if "arxiv_summarizer"  in outputs: bullets.append("✓ **arXiv** — peer-reviewed academic papers found")
    if "news_fetcher"      in outputs: bullets.append("✓ **News** — recent developments analysed")
    if "semantic_scholar"  in outputs: bullets.append("✓ **Semantic Scholar** — citation data included")
    if "pubmed_search"     in outputs: bullets.append("✓ **PubMed** — biomedical literature consulted")
    if "sentiment_analyzer" in outputs: bullets.append("✓ **Sentiment** — public perception analysed")
    if "qa_engine"         in outputs: bullets.append("✓ **AI Synthesis** — comprehensive answer generated")
    if not bullets:
        return f"Information about **{query}** gathered from available sources."
    return "\n".join(bullets) + f"\n\n*{len(bullets)} source(s) consulted for this analysis.*"


# ── Main synthesizer ───────────────────────────────────────────────────────────

def synthesize_answer(
    user_query: str,
    execution_results: List[Dict[str, Any]],
    plan: Dict[str, Any],
) -> str:

    outputs = _collect(execution_results)
    files   = _collect_files(execution_results)

    if not outputs:
        return (
            "❌ **No results were generated.**\n\n"
            "The query could not be processed. Please check that the backend is running "
            "and your API key is valid."
        )

    answer = f"# 📖 {user_query}\n\n"

    # ── 1. Plain-text intro (always shown first) ───────────────────────────────
    qa_text = outputs.get("qa_engine", "")
    qa_is_real = (
        len(qa_text) > 200
        and "fallback response" not in qa_text.lower()
        and "i'm sorry" not in qa_text.lower()
        and "configure openrouter" not in qa_text.lower()
    )

    if qa_is_real:
        # Show the AI answer as the primary readable response
        answer += qa_text.strip() + "\n\n"
        answer += "---\n\n"

    # ── 2. Wikipedia ───────────────────────────────────────────────────────────
    if "wikipedia_search" in outputs:
        answer += "## 📖 Wikipedia Background\n\n"
        answer += _fmt_wiki(outputs["wikipedia_search"]) + "\n\n"

    # ── 3. Academic Research ───────────────────────────────────────────────────
    if "arxiv_summarizer" in outputs:
        answer += "## 🔬 Academic Research (arXiv)\n\n"
        answer += _fmt_arxiv(user_query, outputs["arxiv_summarizer"]) + "\n\n"

    if "semantic_scholar" in outputs:
        answer += "## 🎓 Semantic Scholar\n\n"
        answer += outputs["semantic_scholar"].strip() + "\n\n"

    if "pubmed_search" in outputs:
        answer += "## 🏥 PubMed Research\n\n"
        answer += outputs["pubmed_search"].strip() + "\n\n"

    # ── 4. Recent News ─────────────────────────────────────────────────────────
    if "news_fetcher" in outputs:
        answer += "## 📰 Recent News & Developments\n\n"
        answer += _fmt_news(user_query, outputs["news_fetcher"]) + "\n\n"

    # ── 5. Sentiment ───────────────────────────────────────────────────────────
    if "sentiment_analyzer" in outputs:
        answer += "## 💭 Sentiment Analysis\n\n"
        answer += outputs["sentiment_analyzer"].strip() + "\n\n"

    # ── 6. If no QA answer, show a fallback summary ────────────────────────────
    if not qa_is_real and not any(
        k in outputs for k in ("wikipedia_search", "arxiv_summarizer", "news_fetcher")
    ):
        answer += "## 💡 Summary\n\n"
        answer += (
            f"Your query **\"{user_query}\"** was processed. "
            "The system gathered information from available sources. "
            "For a more detailed AI-generated answer, ensure your OpenRouter API key is valid "
            "and the model is accessible.\n\n"
        )

    # ── 7. Key Insights ────────────────────────────────────────────────────────
    answer += "## 🎯 Key Insights\n\n"
    answer += _key_insights(user_query, outputs) + "\n\n"

    # ── 8. Generated files ─────────────────────────────────────────────────────
    if files:
        answer += "## 📊 Generated Resources\n\n"
        for ftype, finfo in files:
            icon = "📈" if ftype == "chart" else "📄"
            answer += f"{icon} {finfo.strip()}\n"
        answer += "\n"

    answer += "---\n\n"
    answer += "✅ **Analysis Complete** — synthesised from multiple sources.\n"
    return answer


def create_executive_summary(user_query: str, execution_results: List[Dict[str, Any]]) -> str:
    tools = [r.get("tool", "") for r in execution_results if r.get("status") == "success"]
    if not tools:
        return "No results could be generated for this query."
    parts = [f"Regarding **{user_query}**:"]
    if "qa_engine"        in tools: parts.append("AI-generated answer provided.")
    if "wikipedia_search" in tools: parts.append("Wikipedia background retrieved.")
    if "arxiv_summarizer" in tools: parts.append("Academic papers identified.")
    if "news_fetcher"     in tools: parts.append("Recent news analysed.")
    parts.append(f"Total: {len(tools)} source(s) consulted.")
    return " ".join(parts)
