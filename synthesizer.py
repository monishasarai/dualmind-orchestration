"""
Answer Synthesizer — DualMind v5
Clean, deduplicated, well-structured response with all sections.
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional

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
    """Collect successful tool outputs keyed by tool name."""
    out: Dict[str, str] = {}
    for r in execution_results:
        if r.get("status") != "success":
            continue
        name = r.get("tool", "unknown")
        text = _to_text(r.get("output", ""))
        if text and not text.lower().startswith("error"):
            out[name] = text
    return out


def _extract_file_refs(execution_results: List[Dict[str, Any]]) -> List[tuple]:
    """
    Extract ONLY the short file-path references from tool outputs.
    Avoids pulling in the full document text as a 'file'.
    Returns list of (type, short_description).
    """
    files = []
    seen = set()

    for r in execution_results:
        if r.get("status") != "success":
            continue
        tool = r.get("tool", "")
        text = _to_text(r.get("output", ""))

        # Only look at data_plotter and document_writer outputs
        if tool not in ("data_plotter", "document_writer"):
            continue

        # Extract chart file references  e.g. "output\bar_chart_3_...png"
        chart_matches = re.findall(
            r'(?:output[/\\][\w\-\.]+\.png|[\w\-]+\.png)',
            text, re.IGNORECASE
        )
        for m in chart_matches:
            if m not in seen:
                seen.add(m)
                files.append(("chart", f"Chart saved: `{m}`"))

        # Extract PDF file references  e.g. "output\report_...pdf"
        pdf_matches = re.findall(
            r'(?:output[/\\][\w\-\.]+\.pdf|[\w\-]+\.pdf)',
            text, re.IGNORECASE
        )
        for m in pdf_matches:
            if m not in seen:
                seen.add(m)
                files.append(("pdf", f"PDF report saved: `{m}`"))

        # If no file path found but tool says "successfully created"
        if not chart_matches and not pdf_matches:
            low = text.lower()
            if "successfully created" in low or "chart" in low:
                # Extract just the first line (the status line)
                first_line = text.split("\n")[0].strip()
                if len(first_line) < 200 and first_line not in seen:
                    seen.add(first_line)
                    ftype = "chart" if "chart" in low or ".png" in low else "pdf"
                    files.append((ftype, first_line))

    return files


# ── Section formatters ─────────────────────────────────────────────────────────

def _fmt_arxiv(query: str, raw: str) -> str:
    if not raw or len(raw) < 30:
        return f"*No academic papers could be retrieved for **{query}** at this time.*"
    lines = raw.strip().split("\n")
    count = sum(1 for ln in lines if re.match(r"^\d+\.", ln.strip()))
    result = raw.strip()
    if count > 0:
        result += f"\n\n> 📌 **{count} paper(s)** retrieved from arXiv."
    return result


def _fmt_news(query: str, raw: str) -> str:
    if not raw or len(raw) < 20:
        return f"*No recent news articles found for **{query}**.*"

    # Try JSON dict (news_fetcher returns serialised dict)
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

    if len(raw) > 80:
        return raw.strip()
    return f"*No recent news articles found for **{query}**.*"


def _fmt_wiki(raw: str) -> str:
    return raw.strip() if raw and len(raw) > 30 else "*Wikipedia data unavailable.*"


def _key_insights(query: str, outputs: Dict[str, str]) -> str:
    bullets = []
    if "wikipedia_search"   in outputs: bullets.append("✓ **Wikipedia** — encyclopedic background retrieved")
    if "arxiv_summarizer"   in outputs: bullets.append("✓ **arXiv** — peer-reviewed academic papers found")
    if "semantic_scholar"   in outputs: bullets.append("✓ **Semantic Scholar** — citation data included")
    if "pubmed_search"      in outputs: bullets.append("✓ **PubMed** — biomedical literature consulted")
    if "news_fetcher"       in outputs: bullets.append("✓ **News** — recent developments analysed")
    if "sentiment_analyzer" in outputs: bullets.append("✓ **Sentiment** — public perception analysed")
    if "data_plotter"       in outputs: bullets.append("✓ **Data Plotter** — visual chart generated")
    if "document_writer"    in outputs: bullets.append("✓ **Document Writer** — PDF report generated")
    if "qa_engine"          in outputs: bullets.append("✓ **AI Synthesis** — comprehensive answer generated")
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
    files   = _extract_file_refs(execution_results)   # ← fixed: short refs only

    if not outputs:
        return (
            "❌ **No results were generated.**\n\n"
            "The query could not be processed. Please check that the backend is running "
            "and your API key is valid."
        )

    sections: List[str] = []

    # ── 1. AI-generated answer (primary, shown first) ──────────────────────────
    qa_text = outputs.get("qa_engine", "")
    qa_is_real = (
        len(qa_text) > 200
        and "fallback response" not in qa_text.lower()
        and "i'm sorry" not in qa_text.lower()
        and "configure openrouter" not in qa_text.lower()
    )

    if qa_is_real:
        sections.append(qa_text.strip())
        sections.append("---")

    # ── 2. Wikipedia ───────────────────────────────────────────────────────────
    if "wikipedia_search" in outputs:
        sections.append("## 📖 Wikipedia Background\n\n" + _fmt_wiki(outputs["wikipedia_search"]))

    # ── 3. Academic Research ───────────────────────────────────────────────────
    if "arxiv_summarizer" in outputs:
        sections.append("## 🔬 Academic Research (arXiv)\n\n" + _fmt_arxiv(user_query, outputs["arxiv_summarizer"]))

    if "semantic_scholar" in outputs:
        ss = outputs["semantic_scholar"].strip()
        if "No papers found" not in ss:
            sections.append("## 🎓 Semantic Scholar\n\n" + ss)

    if "pubmed_search" in outputs:
        pm = outputs["pubmed_search"].strip()
        if "No biomedical articles found" not in pm:
            sections.append("## 🏥 PubMed Research\n\n" + pm)

    # ── 4. Recent News ─────────────────────────────────────────────────────────
    if "news_fetcher" in outputs:
        sections.append("## 📰 Recent News & Developments\n\n" + _fmt_news(user_query, outputs["news_fetcher"]))

    # ── 5. Sentiment ───────────────────────────────────────────────────────────
    if "sentiment_analyzer" in outputs:
        sections.append("## 💭 Sentiment Analysis\n\n" + outputs["sentiment_analyzer"].strip())

    # ── 6. Fallback summary if nothing useful ─────────────────────────────────
    if not qa_is_real and not any(
        k in outputs for k in ("wikipedia_search", "arxiv_summarizer", "news_fetcher")
    ):
        sections.append(
            "## 💡 Summary\n\n"
            f"Your query **\"{user_query}\"** was processed. "
            "The system gathered information from available sources. "
            "For a more detailed AI-generated answer, ensure your OpenRouter API key is valid."
        )

    # ── 7. Key Insights ────────────────────────────────────────────────────────
    sections.append("## 🎯 Key Insights\n\n" + _key_insights(user_query, outputs))

    # ── 8. Generated files (charts / PDFs) — short refs only ──────────────────
    if files:
        file_lines = []
        for ftype, finfo in files:
            icon = "📈" if ftype == "chart" else "📄"
            file_lines.append(f"{icon} {finfo}")
        sections.append("## 📊 Generated Resources\n\n" + "\n".join(file_lines))

    # ── Assemble ───────────────────────────────────────────────────────────────
    header = f"# 📖 {user_query}\n"
    body   = "\n\n".join(sections)
    footer = "\n\n---\n\n✅ **Analysis Complete** — synthesised from multiple sources."

    return header + "\n" + body + footer


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
