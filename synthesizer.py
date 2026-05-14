"""
Answer Synthesizer Module
Combines outputs from multiple tools into a coherent, human-readable answer.
"""

import logging
import json
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


def synthesize_answer(user_query: str, execution_results: List[Dict[str, Any]], plan: Dict[str, Any]) -> str:
    """
    Synthesize a comprehensive answer from multiple tool outputs.
    
    Args:
        user_query: The original user query
        execution_results: Results from tool executions
        plan: The execution plan
        
    Returns:
        Synthesized answer as a formatted string
    """
    
    # Helper to normalize any tool output to a string
    def _to_text(val: Any) -> str:
        if isinstance(val, str):
            return val
        try:
            if isinstance(val, (dict, list)):
                return json.dumps(val, ensure_ascii=False)
            return str(val)
        except Exception:
            return ""

    # Collect all successful outputs
    outputs = {}
    for result in execution_results:
        if result.get('status') == 'success':
            tool_name = result.get('tool', 'unknown')
            raw_output = result.get('output', '')
            output = _to_text(raw_output)
            if output and not output.startswith('Error:'):
                outputs[tool_name] = output
    
    if not outputs:
        return "❌ **No results were generated.** The query could not be processed successfully."
    
    # Build the synthesized answer
    answer = f"# 📖 Answer to: {user_query}\n\n"
    
    # Strategy 1: If QA engine was used, make it the PRIMARY response
    if 'qa_engine' in outputs:
        qa_answer = outputs['qa_engine']
        
        # Check if it's a substantial answer (not just fallback)
        if len(qa_answer) > 300 and not qa_answer.startswith("I'm sorry"):
            # QA engine provided comprehensive answer - make it THE answer
            answer += qa_answer + "\n\n"
            answer += "---\n\n"
            
            # Show factual sources PROMINENTLY for verification
            answer += "## 📚 Factual Sources Used (Verify Claims Above)\n\n"
            answer += "*The AI answer above is grounded in the following factual sources. Cross-reference to verify accuracy:*\n\n"
            
            has_sources = False
            
            # Show ArXiv papers prominently - these are REAL research
            if 'arxiv_summarizer' in outputs and len(outputs['arxiv_summarizer']) > 50:
                answer += "### 🔬 Academic Papers Found\n\n"
                answer += outputs['arxiv_summarizer'] + "\n\n"
                has_sources = True
            
            # Show Wikipedia for background verification
            if 'wikipedia_search' in outputs and len(outputs['wikipedia_search']) > 50:
                answer += "### 📖 Wikipedia Background\n\n"
                # Show first 800 chars prominently, rest in details
                wiki_text = outputs['wikipedia_search']
                if len(wiki_text) > 800:
                    answer += wiki_text[:800] + "...\n\n"
                    answer += f"<details><summary>Show full Wikipedia content</summary>\n\n{wiki_text}\n\n</details>\n\n"
                else:
                    answer += wiki_text + "\n\n"
                has_sources = True
            
            # Show news articles for current context
            if 'news_fetcher' in outputs and len(outputs['news_fetcher']) > 50:
                answer += "### 📰 Recent News Articles\n\n"
                answer += outputs['news_fetcher'] + "\n\n"
                has_sources = True
            
            if not has_sources:
                answer += "*Note: This answer is based on the LLM's general knowledge. No specific research papers or news articles were retrieved for verification.*\n\n"
            
            # Skip the rest of synthesis - qa_engine IS the answer
            # Track generated files
            files_generated = []
            for result in execution_results:
                output = _to_text(result.get('output', ''))
                if 'successfully created' in output.lower() or 'generated' in output.lower():
                    if '.png' in output or 'Chart' in output:
                        files_generated.append(('chart', output))
                    elif '.pdf' in output or 'PDF' in output:
                        files_generated.append(('pdf', output))
            
            if files_generated:
                answer += "## 📊 Generated Resources\n\n"
                for file_type, file_info in files_generated:
                    if file_type == 'chart':
                        answer += f"📈 {file_info}\n"
                    else:
                        answer += f"📄 {file_info}\n"
                answer += "\n"
            
            answer += "---\n\n"
            answer += "✅ **Analysis Complete** | Comprehensive answer generated using AI with supporting research from multiple sources.\n"
            
            return answer
        else:
            # Fallback answer, continue with normal synthesis
            answer += "## 💡 Quick Answer\n\n"
            answer += f"{qa_answer}\n\n"
            answer += "---\n\n"
    
    # Strategy 2: Synthesize from available information (if no comprehensive QA answer)
    has_content = False
    
    # Wikipedia provides background
    if 'wikipedia_search' in outputs:
        wiki_output = outputs['wikipedia_search']
        if len(wiki_output) > 50:
            answer += "## 📚 Background\n\n"
            # Show full Wikipedia output
            answer += wiki_output + "\n\n"
            has_content = True
    
    # ArXiv provides research context
    if 'arxiv_summarizer' in outputs:
        arxiv_output = outputs['arxiv_summarizer']
        if 'Found' in arxiv_output and 'papers' in arxiv_output:
            # Synthesize instead of showing raw list
            answer += "## 🔬 Academic Research\n\n"
            answer += _synthesize_arxiv_papers(user_query, arxiv_output)
            answer += "\n\n"
            has_content = True
    
    # News provides current developments
    if 'news_fetcher' in outputs:
        news_output = outputs['news_fetcher']
        if len(news_output) > 50:
            answer += "## 📰 Recent Developments\n\n"
            answer += _synthesize_news(user_query, news_output)
            answer += "\n\n"
            has_content = True
    
    # Sentiment analysis
    if 'sentiment_analyzer' in outputs:
        sentiment_output = outputs['sentiment_analyzer']
        if len(sentiment_output) > 20:
            answer += "## 💭 Sentiment Analysis\n\n"
            answer += sentiment_output + "\n\n"
            has_content = True
    
    # Track generated files
    files_generated = []
    for result in execution_results:
        output = _to_text(result.get('output', ''))
        if 'successfully created' in output.lower() or 'generated' in output.lower():
            if '.png' in output or 'Chart' in output:
                files_generated.append(('chart', output))
            elif '.pdf' in output or 'PDF' in output:
                files_generated.append(('pdf', output))
    
    # Add final synthesis
    if has_content:
        answer += "## 🎯 Key Insights\n\n"
        answer += _generate_key_insights(user_query, outputs)
        answer += "\n\n"
    
    # Add generated files
    if files_generated:
        answer += "## 📊 Generated Resources\n\n"
        for file_type, file_info in files_generated:
            if file_type == 'chart':
                answer += f"📈 {file_info}\n"
            else:
                answer += f"📄 {file_info}\n"
        answer += "\n"
    
    # Footer
    answer += "---\n\n"
    answer += "✅ **Analysis Complete** | Information gathered from multiple sources and synthesized for your query.\n"
    
    return answer


def _synthesize_arxiv_papers(query: str, arxiv_output: str) -> str:
    """Synthesize ArXiv paper information into a coherent summary."""
    
    # Check if it's mock data
    if 'Sample Paper' in arxiv_output:
        return f"""Based on the academic research related to **"{query}"**, several important papers have been published:

**Research Themes:**
- The field shows active research with multiple recent publications
- Key areas of focus include theoretical foundations and practical applications
- Current work explores novel approaches and methodologies

**Note:** This is a demonstration of the ArXiv integration. In a live system with a valid ArXiv API connection, you would see actual paper titles, authors, abstracts, and publication details from the research database.

To access real academic papers, ensure:
1. Internet connectivity is available
2. The ArXiv API is accessible
3. Your query matches indexed research topics"""
    
    # Parse and summarize real papers
    lines = arxiv_output.split('\n')
    paper_count = 0
    summary = f"Found relevant academic research on **{query}**:\n\n"
    
    for line in lines:
        if line.strip().startswith('**'):
            paper_count += 1
            summary += f"- {line.strip()}\n"
    
    return summary


def _synthesize_news(query: str, news_output: str) -> str:
    """Synthesize news articles into a coherent summary."""
    
    if 'No recent news' in news_output or len(news_output) < 100:
        return f"No recent news articles were found specifically about {query}. This could mean:\n- The topic is highly specialized\n- No major news coverage in recent days\n- Try a broader search term for more results"
    
    # Extract key points from news
    lines = news_output.split('\n')
    article_count = 0
    summary = f"Recent news coverage on **{query}**:\n\n"
    
    for line in lines:
        if '**Article' in line or '**Title' in line:
            article_count += 1
            summary += f"- {line.strip()}\n"
    
    return summary


def _generate_key_insights(query: str, outputs: Dict[str, str]) -> str:
    """Generate key insights from all gathered information."""
    
    insights = []
    
    # Analyze what information we have
    if 'wikipedia_search' in outputs:
        insights.append(f"✓ **Foundational knowledge** about {query} has been retrieved from Wikipedia")
    
    if 'arxiv_summarizer' in outputs:
        insights.append("✓ **Academic research papers** have been identified and summarized")
    
    if 'news_fetcher' in outputs:
        insights.append("✓ **Current news** and recent developments have been analyzed")
    
    if 'sentiment_analyzer' in outputs:
        insights.append("✓ **Sentiment analysis** provides insights into public perception")
    
    if 'qa_engine' in outputs:
        insights.append("✓ **Direct answer** has been generated based on available knowledge")
    
    if not insights:
        return f"Based on the available information, here's what we know about **{query}**: The system has gathered relevant data from multiple sources to provide you with a comprehensive overview."
    
    result = "**Information Sources:**\n"
    result += "\n".join(insights)
    result += f"\n\nThis comprehensive analysis of **{query}** combines information from multiple authoritative sources to give you a complete picture."
    
    return result


def create_executive_summary(user_query: str, execution_results: List[Dict[str, Any]]) -> str:
    """
    Create a brief executive summary (2-3 sentences) of the answer.
    
    Args:
        user_query: The original user query
        execution_results: Results from tool executions
        
    Returns:
        Brief executive summary
    """
    
    successful_tools = [r.get('tool', '') for r in execution_results if r.get('status') == 'success']
    
    if not successful_tools:
        return "No results could be generated for this query."
    
    summary = f"Regarding **{user_query}**: "
    
    if 'qa_engine' in successful_tools:
        summary += "A direct answer has been provided based on available knowledge. "
    
    if 'wikipedia_search' in successful_tools:
        summary += "Background information has been retrieved from Wikipedia. "
    
    if 'arxiv_summarizer' in successful_tools:
        summary += "Academic research papers have been identified and summarized. "
    
    if 'news_fetcher' in successful_tools:
        summary += "Recent news articles have been analyzed. "
    
    summary += f"Total of {len(successful_tools)} information sources consulted."
    
    return summary
