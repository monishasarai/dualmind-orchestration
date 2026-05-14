"""
Verifier LLM Module
Reviews and critiques Planner output in the GAN-inspired architecture.
"""

import json
import logging
import os
from typing import Dict, Any, List, Tuple
from datetime import datetime

# Import JSON fixer for robust LLM response parsing
try:
    from json_fixer import parse_llm_json, validate_verification_json
except ImportError:
    parse_llm_json = None
    validate_verification_json = None

class Verifier:
    """
    Verifier LLM that acts as the Discriminator in the GAN-inspired architecture.
    Reviews the Planner's reasoning and proposed plan, detecting errors and suggesting improvements.
    """

    def __init__(self, tools_file: str = "tools_description.json"):
        """
        Initialize the Verifier.

        Args:
            tools_file (str): Path to tools description JSON file
        """
        self.tools_file = tools_file
        self.logger = logging.getLogger(__name__)
        self.tools = self._load_tools()
        self.llm_client = None
        
        # Try to import and initialize LLM client
        try:
            from llm_client import llm_client
            self.llm_client = llm_client
        except ImportError:
            self.logger.warning("LLM client not available, using rule-based verification")
            
        # Common verification rules
        self.verification_rules = {
            "redundancy": "Check for redundant tool usage",
            "relevance": "Ensure tools are relevant to the query",
            "completeness": "Verify the plan covers all aspects of the query",
            "efficiency": "Check if the pipeline is optimally structured",
            "feasibility": "Verify that all planned tools are available and functional"
        }

    def _load_tools(self) -> List[Dict[str, Any]]:
        """Load tools from the tools description file."""
        try:
            with open(self.tools_file, 'r') as f:
                data = json.load(f)
                return data.get('tools', [])
        except FileNotFoundError:
            self.logger.error(f"Tools file not found: {self.tools_file}")
            return []
        except json.JSONDecodeError:
            self.logger.error(f"Invalid JSON in tools file: {self.tools_file}")
            return []

    def verify_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify and critique a task plan.

        Args:
            plan (Dict[str, Any]): The task plan to verify

        Returns:
            Dict[str, Any]: Verification results and feedback
        """
        # Try to use LLM for intelligent verification if available
        if self.llm_client and self.llm_client.is_available():
            try:
                llm_verification = self._llm_verify_plan(plan)
                if llm_verification and "score" in llm_verification:
                    self.logger.info("Successfully completed LLM-based verification")
                    return llm_verification
                else:
                    self.logger.warning("LLM verification was empty or invalid, using rule-based")
                    return self._rule_based_verify_plan(plan)
            except Exception as e:
                self.logger.warning(f"LLM verification failed ({type(e).__name__}), using rule-based")
                self.logger.debug(f"LLM verification error details: {e}")
                return self._rule_based_verify_plan(plan)
        else:
            self.logger.info("LLM not available, using rule-based verification")
            return self._rule_based_verify_plan(plan)

    def _llm_verify_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM for intelligent plan verification."""
        
        # Prepare the system prompt for verification
        system_prompt = """You are a JSON-only response bot. You MUST respond with ONLY valid JSON. No other text is allowed.

Available tools:
{tools_description}

⚠️ CRITICAL INSTRUCTIONS - FOLLOW EXACTLY:
1. Your response MUST start with {{ and end with }}
2. DO NOT write ANY text before the {{
3. DO NOT write ANY text after the }}
4. DO NOT use markdown code blocks (```)
5. DO NOT include explanations or comments
6. ONLY output valid, parseable JSON

Required structure:
{{
    "overall_approval": true,
    "score": 85,
    "issues": ["list issues"],
    "suggestions": ["list suggestions"],
    "improvements": ["list improvements"],
    "reasoning": "verification reasoning"
}}

Scoring (0-100):
- 80-100: Excellent (approve)
- 60-79: Good (approve with suggestions)
- 40-59: Fair (needs revision)
- 0-39: Poor (reject)

Criteria:
- Relevance 30%: Do tools match query?
- Efficiency 25%: Is sequence logical?
- Completeness 25%: Covers all aspects?
- Feasibility 20%: Are tools available?

Note: Empty arrays are valid: "issues": []

IMPORTANT: Your ENTIRE response must be valid JSON. Start typing {{ immediately."""

        # Format the plan for the prompt
        plan_json = json.dumps(plan, indent=2)
        
        # Format available tools for the prompt
        tools_description = ""
        for tool in self.tools:
            tools_description += f"- {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}\n"

        prompt = f"Please verify this task plan:\n\n{plan_json}\n\nProvide detailed verification feedback:"

        llm_response = self.llm_client.call_llm(
            prompt=prompt,
            system_prompt=system_prompt.format(tools_description=tools_description),
            max_tokens=2000
        )

        if llm_response:
            try:
                # Use robust JSON parser with automatic fixing when available
                if parse_llm_json:
                    expected_keys = ["overall_approval", "score", "issues", "suggestions", "improvements"]
                    verification_data = parse_llm_json(llm_response, expected_keys)

                    if validate_verification_json and not validate_verification_json(verification_data):
                        self.logger.warning("LLM verification failed validation, normalising defaults")
                        verification_data.setdefault("overall_approval", False)
                        verification_data.setdefault("score", 50)
                        verification_data.setdefault("issues", [])
                        verification_data.setdefault("suggestions", [])
                        verification_data.setdefault("improvements", [])
                else:
                    clean_response = self._extract_json_from_response(llm_response)
                    verification_data = json.loads(clean_response)
            except ValueError as exc:
                self.logger.warning(
                    "LLM verification response missing expected keys (%s); applying permissive fallback",
                    exc,
                )
                clean_response = self._extract_json_from_response(llm_response)
                verification_data = json.loads(clean_response)
            except json.JSONDecodeError as exc:
                self.logger.debug(f"Failed to parse LLM verification JSON: {exc}")
                raise

            # Ensure all required fields exist with sensible defaults
            verification_data.setdefault("overall_approval", False)
            verification_data.setdefault("score", 50)
            verification_data.setdefault("issues", [])
            verification_data.setdefault("suggestions", [])
            verification_data.setdefault("improvements", [])
            verification_data.setdefault("reasoning", "LLM-generated verification")

            # Add metadata before returning
            verification_data.update({
                "plan_id": f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "verified_at": datetime.now().isoformat(),
                "verification_method": "llm",
                "tools_available": len(self.tools)
            })

            self.logger.info(
                "Successfully parsed LLM verification (score: %s)",
                verification_data.get("score", 0),
            )
            return verification_data
        else:
            self.logger.debug("LLM returned None, falling back")
            raise ValueError("LLM returned no response")

    def _extract_json_from_response(self, response: str) -> str:
        """Extract JSON content from LLM response, handling various formats."""
        if not response:
            raise ValueError("Empty response")
        
        import re
        
        # Strip whitespace
        response = response.strip()
        
        # Remove common LLM prefixes
        response = re.sub(r'^(Here is|Here\'s|Sure|Certainly|Of course)[^\{]*', '', response, flags=re.IGNORECASE)
        response = response.strip()
        
        # Try direct parsing first
        try:
            json.loads(response)
            return response
        except json.JSONDecodeError:
            pass
        
        # Remove markdown code blocks
        code_block_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', response, re.DOTALL)
        if code_block_match:
            cleaned = code_block_match.group(1).strip()
            try:
                json.loads(cleaned)
                return cleaned
            except json.JSONDecodeError:
                pass
        
        # Find the first { and last } - most aggressive approach
        first_brace = response.find('{')
        last_brace = response.rfind('}')
        
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            potential_json = response[first_brace:last_brace + 1]
            try:
                json.loads(potential_json)
                return potential_json
            except json.JSONDecodeError:
                pass
        
        # Try to extract balanced braces from the start
        if response.startswith('{'):
            brace_count = 0
            end_idx = 0
            
            for i, char in enumerate(response):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_idx = i + 1
                        break
            
            if end_idx > 0:
                potential_json = response[:end_idx]
                try:
                    json.loads(potential_json)
                    return potential_json
                except json.JSONDecodeError:
                    pass
        
        # Look for JSON pattern with proper structure
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(json_pattern, response, re.DOTALL)
        
        for match in reversed(matches):  # Try longest matches first
            try:
                json.loads(match)
                return match
            except json.JSONDecodeError:
                continue
        
        # If nothing works, raise an error with sample of response
        sample = response[:200] if len(response) > 200 else response
        raise ValueError(f"Could not extract valid JSON from LLM response. Sample: {sample}...")

    def _rule_based_verify_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Use rule-based verification as fallback."""
        verification_results = {
            "plan_id": f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "verified_at": datetime.now().isoformat(),
            "overall_approval": True,
            "issues": [],
            "suggestions": [],
            "improvements": [],
            "score": 100,
            "verification_method": "rule_based"
        }

        # Run verification checks
        issues, suggestions, improvements = self._run_verification_checks(plan)

        verification_results["issues"] = issues
        verification_results["suggestions"] = suggestions
        verification_results["improvements"] = improvements

        # Calculate overall score and approval
        score_deductions = len(issues) * 10 + len(suggestions) * 5
        verification_results["score"] = max(0, 100 - score_deductions)
        verification_results["overall_approval"] = verification_results["score"] >= 70

        return verification_results

    def _run_verification_checks(self, plan: Dict[str, Any]) -> Tuple[List[str], List[str], List[str]]:
        """
        Run comprehensive verification checks on the plan.
        Returns lists of issues, suggestions, and improvements.
        """
        issues = []
        suggestions = []
        improvements = []

        query = plan.get("query", "")
        pipeline = plan.get("pipeline", [])

        # Skip verification if pipeline is empty (handled elsewhere)
        if not pipeline:
            return issues, suggestions, improvements

        # Check 1: Relevance - Be more lenient, only flag obvious mismatches
        if len(pipeline) > 1 and not self._check_relevance(query, pipeline):
            suggestions.append("Some tools may not be directly relevant to the query")
            improvements.append("Review tool selection for better alignment with query intent")

        # Check 2: Redundancy - Only flag exact duplicate tools in sequence
        redundant_tools = self._check_redundancy(pipeline)
        if redundant_tools:
            issues.append(f"Redundant tool usage detected: {', '.join(redundant_tools)}")
            suggestions.append("Remove or consolidate duplicate tools in the pipeline")

        # Check 3: Completeness - Only suggest for very short pipelines
        if len(pipeline) < 2 and len(query.split()) > 5:  # If query is detailed but pipeline is short
            suggestions.append("Consider adding more tools for comprehensive coverage")

        # Check 4: Efficiency - Only suggest for pipelines with 3+ tools
        if len(pipeline) >= 3 and not self._check_efficiency(pipeline):
            improvements.append("Consider reordering tools for better efficiency")

        # Check 5: Feasibility - Only check if we have tools defined
        if self.tools and not self._check_feasibility(pipeline):
            issues.append("Some planned tools may not be available")
            suggestions.append("Verify tool availability or use alternatives")

        return issues, suggestions, improvements

    def _check_relevance(self, query: str, pipeline: List[Dict[str, Any]]) -> bool:
        """
        Check if tools are relevant to the query.
        Returns True by default unless there's a clear mismatch.
        """
        if not pipeline:
            return True
            
        query_lower = query.lower()
        
        # Define keyword mappings for tool relevance - expanded and more flexible
        relevance_keywords = {
            "wikipedia_search": ["information", "overview", "definition", "explain", "what is", "who is", "about"],
            "news_fetcher": ["news", "current", "recent", "latest", "update", "happening", "trend"],
            "arxiv_summarizer": ["research", "academic", "paper", "study", "scientific", "publication"],
            "sentiment_analyzer": ["sentiment", "opinion", "feeling", "mood", "attitude", "reaction"],
            "data_plotter": ["visualize", "chart", "graph", "plot", "data", "analysis", "analyze"],
            "qa_engine": ["question", "answer", "explain", "what", "how", "why", "when", "where", "which"],
            "document_writer": ["report", "document", "pdf", "write", "generate", "create", "summarize"]
        }
        
        # Common research-related terms that suggest broader tool usage
        research_terms = ["research", "analyze", "investigate", "study", "explore"]
        
        # If it's a research query, be more lenient with tool relevance
        is_research_query = any(term in query_lower for term in research_terms)
        
        irrelevant_tools = 0
        total_tools = len(pipeline)
        
        for step in pipeline:
            tool = step.get("tool", "")
            purpose = step.get("purpose", "").lower()
            
            # If we have a clear purpose, assume relevance
            if purpose and len(purpose.split()) > 2:  # More than 2 words suggests actual content
                continue
                
            # Check if tool is relevant based on keywords or purpose
            tool_relevant = (
                any(keyword in query_lower for keyword in relevance_keywords.get(tool, [])) or
                any(keyword in purpose for keyword in relevance_keywords.get(tool, [])) or
                is_research_query  # If it's a research query, be more lenient
            )
            
            if not tool_relevant:
                irrelevant_tools += 1
        
        # Allow up to 1 irrelevant tool in small pipelines, more in larger ones
        max_irrelevant = max(1, total_tools // 3)
        
        return irrelevant_tools <= max_irrelevant

    def _check_redundancy(self, pipeline: List[Dict[str, Any]]) -> bool:
        """Check for redundant tool usage."""
        tools_used = []
        for step in pipeline:
            tool = step.get("tool", "")
            if tool in tools_used:
                return True
            tools_used.append(tool)
        return False

    def _check_completeness(self, query: str, pipeline: List[Dict[str, Any]]) -> bool:
        """Check if plan covers all aspects of the query."""
        query_lower = query.lower()

        # Define query complexity indicators
        complexity_indicators = [
            "comprehensive", "detailed", "thorough", "complete", "full", "all"
        ]

        # If query suggests comprehensive coverage, check for multiple data sources
        needs_multiple_sources = any(indicator in query_lower for indicator in complexity_indicators)

        if needs_multiple_sources and len(pipeline) < 2:
            return False

        return True

    def _check_efficiency(self, pipeline: List[Dict[str, Any]]) -> bool:
        """Check pipeline efficiency."""
        # Simple check: avoid unnecessary complexity
        if len(pipeline) > 5:
            return False

        # Check for logical flow (information gathering before processing)
        info_tools = ["wikipedia_search", "news_fetcher", "arxiv_summarizer"]
        processing_tools = ["sentiment_analyzer", "data_plotter", "document_writer"]

        info_positions = []
        processing_positions = []

        for i, step in enumerate(pipeline):
            if step.get("tool") in info_tools:
                info_positions.append(i)
            elif step.get("tool") in processing_tools:
                processing_positions.append(i)

        # Processing tools should generally come after info tools
        for proc_pos in processing_positions:
            if not any(info_pos < proc_pos for info_pos in info_positions):
                return False

        return True

    def _check_feasibility(self, pipeline: List[Dict[str, Any]]) -> bool:
        """Check if all planned tools are available."""
        available_tools = [tool.get("name", "") for tool in self.tools]

        for step in pipeline:
            tool_name = step.get("tool", "")
            if tool_name not in available_tools:
                return False

        return True

    def generate_feedback(self, verification_results: Dict[str, Any]) -> str:
        """
        Generate human-readable feedback from verification results.

        Args:
            verification_results (Dict[str, Any]): Verification results

        Returns:
            str: Formatted feedback
        """
        feedback = "🔍 **Verifier Feedback & Plan Validation**\n\n"

        # Overall assessment
        score = verification_results.get("score", 0)
        approval = verification_results.get("overall_approval", False)

        if approval:
            feedback += f"✅ **Plan Approved** (Score: {score}/100)\n\n"
        else:
            feedback += f"❌ **Plan Needs Revision** (Score: {score}/100)\n\n"

        # Issues
        issues = verification_results.get("issues", [])
        if issues:
            feedback += "**🚨 Issues Found:**\n"
            for issue in issues:
                feedback += f"• {issue}\n"
            feedback += "\n"

        # Suggestions
        suggestions = verification_results.get("suggestions", [])
        if suggestions:
            feedback += "**💡 Suggestions:**\n"
            for suggestion in suggestions:
                feedback += f"• {suggestion}\n"
            feedback += "\n"

        # Improvements
        improvements = verification_results.get("improvements", [])
        if improvements:
            feedback += "**🚀 Recommended Improvements:**\n"
            for improvement in improvements:
                feedback += f"• {improvement}\n"
            feedback += "\n"

        # Summary
        feedback += "**📊 Verification Summary:**\n"
        feedback += f"• Plan ID: {verification_results.get('plan_id', 'Unknown')}\n"
        feedback += f"• Verified at: {verification_results.get('verified_at', 'Unknown')}\n"
        feedback += f"• Tools checked: {len(self.tools)}\n"
        feedback += f"• Rules applied: {len(self.verification_rules)}"

        return feedback


def create_verifier() -> Verifier:
    """
    Factory function to create a Verifier instance.

    Returns:
        Verifier: Configured verifier instance
    """
    return Verifier()
