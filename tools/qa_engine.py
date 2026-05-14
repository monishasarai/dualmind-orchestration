"""
QA Engine Tool — DualMind v3
Answers queries using OpenRouter LLM with full context from other tools.
"""

import json
import logging
import os
import requests
from typing import Any, Dict

logger = logging.getLogger(__name__)

_FALLBACK_NOTE = (
    "\n\n---\n"
    "*Note: AI synthesis unavailable — showing rule-based summary. "
    "Ensure OPENROUTER_API_KEY is set and valid.*"
)


class QAEngine:

    def __init__(self):
        self.api_key  = (os.getenv("OPENROUTER_API_KEY") or "").strip()
        self.base_url = "https://openrouter.ai/api/v1"
        self.model    = os.getenv("OPENROUTER_MODEL", "microsoft/wizardlm-2-8x22b")

    # ── LLM call ───────────────────────────────────────────────────────────────

    def _call_llm(self, system: str, user: str, max_tokens: int = 2500) -> str | None:
        if not self.api_key:
            return None
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type":  "application/json",
                "HTTP-Referer":  "https://github.com/dualmind",
                "X-Title":       "DualMind",
            }
            data = {
                "model":    self.model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user",   "content": user},
                ],
                "max_tokens":  max_tokens,
                "temperature": 0.65,
            }
            r = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers, json=data, timeout=45,
            )
            if r.status_code != 200:
                logger.error("QA engine HTTP %s: %s", r.status_code, r.text[:200])
                return None
            content = r.json()["choices"][0]["message"]["content"]
            return content.strip() if content else None
        except Exception as e:
            logger.error("QA engine LLM error: %s", e)
            return None

    # ── Main entry ─────────────────────────────────────────────────────────────

    def run(self, question: str, context: str = "") -> str:
        # Extract embedded context (injected by orchestrator)
        if "|||CONTEXT:" in question:
            parts    = question.split("|||CONTEXT:", 1)
            question = parts[0].strip()
            context  = parts[1].strip()

        system = (
            "You are an expert research analyst. "
            "Write a comprehensive, well-structured answer in Markdown. "
            "Use ## and ### headings, bullet points, and bold key terms. "
            "Cover: overview, key concepts, techniques/methods, real-world examples, "
            "challenges, future directions, and practical impact. "
            "Aim for 600-1000 words. Be specific and factual."
        )

        if context:
            user = (
                f"Using the research context below, answer the question comprehensively.\n\n"
                f"## Research Context\n{context[:6000]}\n\n"
                f"## Question\n{question}\n\n"
                f"Synthesise the context into a detailed, structured answer:"
            )
        else:
            user = (
                f"Answer this question comprehensively:\n\n{question}\n\n"
                "Cover all relevant aspects with specific details, examples, and insights."
            )

        answer = self._call_llm(system, user)

        if not answer:
            # Graceful fallback — never crash
            answer = self._rule_based_answer(question, context)
            return answer + _FALLBACK_NOTE

        # Ensure answer starts with a heading
        if not answer.startswith("#"):
            answer = f"## {question}\n\n{answer}"

        return answer

    def _rule_based_answer(self, question: str, context: str) -> str:
        """Produce a minimal but useful answer from context when LLM is unavailable."""
        lines = [f"## {question}", ""]
        if context:
            # Extract first meaningful paragraph from each context section
            sections = context.split("\n\n")
            for s in sections[:6]:
                s = s.strip()
                if len(s) > 80:
                    lines.append(s[:500])
                    lines.append("")
        else:
            lines.append(
                "This query requires an AI-powered response. "
                "Please ensure your OpenRouter API key is configured correctly."
            )
        return "\n".join(lines)


def qa_engine_tool(question: str, context: str = "") -> str:
    return QAEngine().run(question, context)
