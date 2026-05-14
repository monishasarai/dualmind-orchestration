"""
QA Engine Tool
Answers user queries using OpenRouter LLM API.
"""

import requests
import json
import logging
import os
from typing import Dict, Any

class QAEngine:
    """Tool for answering questions using LLM API."""

    def __init__(self):
        """Initialize the QA engine."""
        self.api_key = os.getenv('OPENROUTER_API_KEY', '')
        self.base_url = "https://openrouter.ai/api/v1"
        self.model = os.getenv('OPENROUTER_MODEL', 'openai/gpt-oss-20b:free')  # Use model from env or default to gpt-oss-20b
        self.logger = logging.getLogger(__name__)

        # Fallback responses when API is not available
        self.fallback_responses = {
            "hello": "Hello! I'm a QA assistant. How can I help you today?",
            "how are you": "I'm functioning well, thank you for asking! How can I assist you?",
            "what is ai": "AI, or Artificial Intelligence, is the simulation of human intelligence processes by machines, especially computer systems.",
            "what is machine learning": "Machine learning is a subset of AI that enables computers to learn and improve from experience without being explicitly programmed.",
            "what is deep learning": "Deep learning is a subset of machine learning that uses neural networks with multiple layers to model and understand complex patterns."
        }

    def ask_question(self, question: str, context: str = "") -> Dict[str, Any]:
        """
        Ask a question to the LLM API.

        Args:
            question (str): Question to ask
            context (str): Additional context

        Returns:
            Dict[str, Any]: API response
        """
        if not self.api_key:
            # Return fallback response
            return self._get_fallback_response(question)

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            # Prepare comprehensive prompt with detailed instructions
            system_prompt = """You are an expert AI research analyst providing in-depth, comprehensive answers.

CRITICAL REQUIREMENTS FOR FACTUAL ACCURACY:
- ONLY use information provided in the context - DO NOT make up facts, papers, or statistics
- If context mentions specific papers, cite them EXACTLY as provided
- If context has numbers/dates, use those EXACT values
- If information is not in context, explicitly state "Based on general knowledge..." or "Additional context needed..."
- When context is limited, acknowledge gaps rather than inventing details

CRITICAL REQUIREMENTS FOR COMPREHENSIVENESS:
- Write 1500-2000 words minimum - extract and synthesize ALL relevant info from context
- Structure with multiple markdown sections (## Main Section, ### Subsections)
- Use bullet points with detailed explanations
- Compare different approaches and perspectives found in context
- Discuss current state, challenges, and future directions based on provided sources
- Be technical but accessible - explain complex concepts clearly

CITATION REQUIREMENTS:
- When referencing papers from context, use format: "Paper Title (Authors, Year)"
- When using statistics from context, cite the source: "According to [source]..."
- Distinguish between context-based facts and general knowledge

AVOID:
- Making up paper titles, authors, or statistics not in context
- Hallucinating specific numbers or dates
- Inventing company names or project names
- Generic statements when specific context info is available

Your goal: Synthesize the provided context into a comprehensive, factually grounded answer."""
            
            if context:
                prompt = f"""Using the following context information, provide a comprehensive answer to the user's question.

Context:
{context}

Question: {question}

Provide a detailed, well-structured answer that synthesizes the context information and addresses all aspects of the question:"""
            else:
                prompt = f"""Question: {question}

Provide an EXTREMELY comprehensive, detailed answer (1500-2000 words) that covers:

1. **Overview & Current State**: What is the current state? What's happening now?
2. **Key Concepts & Definitions**: Define all important terms with examples
3. **Specific Techniques/Methods**: Name actual algorithms, frameworks, or approaches used
4. **Real-World Examples**: Cite specific companies, projects, or research studies (with names)
5. **Comparative Analysis**: Compare different approaches, methodologies, or perspectives
6. **Research Findings**: Discuss recent breakthroughs or important papers
7. **Challenges & Limitations**: What are the current obstacles or problems?
8. **Future Directions**: Where is this field heading? What's next?
9. **Practical Impact**: Real-world implications and applications

Use specific details, numbers, dates, and names throughout. Structure with ## and ### headers.

Answer:"""

            data = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 2000,
                "temperature": 0.7
            }

            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                answer = result["choices"][0]["message"]["content"]

                return {
                    'answer': answer,
                    'success': True,
                    'model': self.model
                }
            else:
                self.logger.error(f"API error: {response.status_code} - {response.text}")
                return self._get_fallback_response(question)

        except requests.RequestException as e:
            self.logger.error(f"Error calling OpenRouter API: {e}")
            return self._get_fallback_response(question)
        except Exception as e:
            self.logger.error(f"Unexpected error in QA engine: {e}")
            return self._get_fallback_response(question)

    def _get_fallback_response(self, question: str) -> Dict[str, Any]:
        """Get a fallback response when API is not available."""
        question_lower = question.lower().strip()

        # Try to find a matching fallback response
        for key, response in self.fallback_responses.items():
            if key in question_lower:
                return {
                    'answer': response,
                    'success': False,
                    'method': 'fallback'
                }

        # Default fallback response
        return {
            'answer': "I'm sorry, I don't have a specific answer for that question right now. Please try rephrasing or ask something else!",
            'success': False,
            'method': 'fallback'
        }

    def run(self, question: str, context: str = "") -> str:
        """
        Main method to run the QA engine tool.

        Args:
            question (str): Question to answer or question|||CONTEXT:context_data
            context (str): Additional context (optional, can also be in question)

        Returns:
            str: Formatted answer
        """
        # Check if context is embedded in question using special separator
        if "|||CONTEXT:" in question:
            parts = question.split("|||CONTEXT:", 1)
            question = parts[0].strip()
            context = parts[1].strip()
        
        result = self.ask_question(question, context)

        answer = result['answer']
        
        # Format the answer properly
        if answer.strip().startswith('#'):
            # Already has markdown formatting
            formatted_result = answer
        else:
            # Add basic formatting
            formatted_result = f"## 💡 Comprehensive Answer\n\n{answer}"

        if not result.get('success', True):
            formatted_result += "\n\n---\n*Note: This is a fallback response. Configure OPENROUTER_API_KEY in .env for AI-powered comprehensive answers.*"

        return formatted_result


def qa_engine_tool(question: str, context: str = "") -> str:
    """
    Standalone function for QA engine tool.

    Args:
        question (str): Question to answer
        context (str): Additional context

    Returns:
        str: Formatted answer
    """
    engine = QAEngine()
    return engine.run(question, context)
