"""
UI Module
Gradio interface for the DualMind Orchestrator system.
"""

import gradio as gr
import json
import logging
import os
from typing import Dict, Any, Tuple

# Import the answer synthesizer
try:
    from synthesizer import synthesize_answer, create_executive_summary
except ImportError:
    synthesize_answer = None
    create_executive_summary = None

class DualMindUI:
    """
    Gradio UI for the DualMind Orchestrator system.
    Provides an interactive interface for users to submit queries and view results.
    """

    def __init__(self):
        """Initialize the UI."""
        self.orchestrator = None
        self.logger = logging.getLogger(__name__)

        # Try to import and initialize the orchestrator
        try:
            from orchestrator import create_orchestrator
            self.orchestrator = create_orchestrator()
        except Exception as e:
            self.logger.error(f"Error initializing orchestrator: {e}")
            self.orchestrator = None

    def process_query(self, user_query: str) -> Tuple[str, str, str, str, str]:
        """
        Process a user query and return formatted results.

        Args:
            user_query (str): The user's query

        Returns:
            Tuple[str, str, str, str, str]: Formatted results for each UI component
        """
        if not self.orchestrator:
            error_msg = "❌ **Error:** Orchestrator not initialized. Please check the server logs."
            return error_msg, error_msg, error_msg, error_msg, error_msg

        if not user_query.strip():
            error_msg = "❌ **Error:** Please enter a query."
            return error_msg, error_msg, error_msg, error_msg, error_msg

        try:
            # Process the query
            results = self.orchestrator.process_query(user_query)

            # Format different aspects of the results
            plan_text = self._format_plan(results)
            verification_text = self._format_verification(results)
            execution_text = self._format_execution(results)
            summary_text = self._format_summary(results)

            # Get final output
            final_output = self._get_final_output(results)

            return plan_text, verification_text, execution_text, summary_text, final_output

        except Exception as e:
            self.logger.error(f"Error processing query: {e}")
            error_msg = f"❌ **Error:** {str(e)}"
            return error_msg, error_msg, error_msg, error_msg, error_msg

    def _format_plan(self, results: Dict[str, Any]) -> str:
        """Format the planning phase results."""
        plan = results.get('plan', {})
        plan_explanation = results.get('plan_explanation', '')

        formatted = "🎯 **Planning Phase**\n\n"
        formatted += plan_explanation

        return formatted

    def _format_verification(self, results: Dict[str, Any]) -> str:
        """Format the verification phase results."""
        verifier_feedback = results.get('verifier_feedback', '')

        formatted = "🔍 **Verification Phase**\n\n"
        formatted += verifier_feedback

        return formatted

    def _format_execution(self, results: Dict[str, Any]) -> str:
        """Format the execution phase results."""
        execution_results = results.get('execution_results', [])

        formatted = "⚙️ **Execution Phase**\n\n"

        if not execution_results:
            formatted += "No execution results available.\n"
            return formatted

        for i, result in enumerate(execution_results, 1):
            status_icon = "✅" if result.get('status') == 'success' else "❌"
            formatted += f"**Step {i}: {result.get('tool', 'Unknown')}** {status_icon}\n"
            formatted += f"• Purpose: {result.get('purpose', 'No purpose specified')}\n"
            formatted += f"• Execution Time: {result.get('execution_time', 0):.2f}s\n"

            if result.get('status') == 'success':
                output = result.get('output', 'No output')
                formatted += f"• Output: {output}\n"
            else:
                formatted += f"• Error: {result.get('error', 'Unknown error')}\n"

            formatted += "\n"

        return formatted

    def _format_summary(self, results: Dict[str, Any]) -> str:
        """Format the overall summary."""
        return self.orchestrator.get_execution_summary(results)

    def _get_final_output(self, results: Dict[str, Any]) -> str:
        """Get the final output using intelligent synthesis."""
        execution_results = results.get('execution_results', [])
        plan = results.get('plan', {})
        user_query = plan.get('query', results.get('user_query', 'your query'))

        if not execution_results:
            return "❌ No results were generated. Please try again."

        # Use the intelligent synthesizer if available
        if synthesize_answer:
            try:
                synthesized = synthesize_answer(user_query, execution_results, plan)
                return synthesized
            except Exception as e:
                self.logger.error(f"Error in synthesizer: {e}")
                # Fall back to simple output
        
        # Fallback: Simple combination of outputs
        answer_parts = [f"# 🎯 Answer to: {user_query}\n\n"]
        
        # Collect successful outputs
        for result in execution_results:
            if result.get('status') == 'success':
                tool_name = result.get('tool', 'Unknown')
                raw_output = result.get('output', '')
                try:
                    if isinstance(raw_output, (dict, list)):
                        output = json.dumps(raw_output, ensure_ascii=False)
                    else:
                        output = str(raw_output) if raw_output is not None else ""
                except Exception:
                    output = ""
                
                if output and output.strip() and not output.startswith('Error:'):
                    if tool_name == 'wikipedia_search':
                        answer_parts.append(f"## 📚 Background\n\n{output}\n\n")
                    elif tool_name == 'arxiv_summarizer':
                        answer_parts.append(f"## 🔬 Research\n\nAcademic papers found (see execution details for full list)\n\n")
                    elif tool_name == 'news_fetcher':
                        answer_parts.append(f"## 📰 News\n\nRecent articles found (see execution details for full list)\n\n")
                    elif tool_name == 'qa_engine':
                        answer_parts.append(f"## 💡 Answer\n\n{output}\n\n")
                    elif 'successfully' not in output.lower():
                        answer_parts.append(f"## {tool_name}\n\n{output}\n\n")
        
        if len(answer_parts) == 1:
            return "❌ No meaningful results were generated. Please try a different query."
        
        answer_parts.append("✅ Query completed. Check execution details for more information.")
        return ''.join(answer_parts)

    def download_pdf_report(self, results: Dict[str, Any]) -> str:
        """
        Generate and provide download link for PDF report.

        Args:
            results (Dict[str, Any]): Execution results

        Returns:
            str: Download link or error message
        """
        try:
            # Check if we have PDF files in the output directory
            output_dir = "output"
            if os.path.exists(output_dir):
                pdf_files = [f for f in os.listdir(output_dir) if f.endswith('.pdf')]
                if pdf_files:
                    # Return the most recent PDF file
                    most_recent = max(pdf_files, key=lambda f: os.path.getctime(os.path.join(output_dir, f)))
                    pdf_path = os.path.join(output_dir, most_recent)
                    return f"📄 **PDF Report Generated:** [Download Report](file/{pdf_path})"

            return "📄 **PDF Report:** No PDF report was generated in this session."

        except Exception as e:
            self.logger.error(f"Error generating PDF download: {e}")
            return f"❌ **Error:** Could not generate PDF download: {str(e)}"

    def create_interface(self) -> gr.Blocks:
        """
        Create the Gradio interface.

        Returns:
            gr.Blocks: The complete Gradio interface
        """
        with gr.Blocks(
            title="DualMind Orchestrator",
            theme=gr.themes.Soft(),
            css="""
            .gradio-container {
                max-width: 1400px;
                margin: auto;
            }
            .title {
                text-align: center;
                color: #2563eb;
                font-size: 2.5em;
                font-weight: bold;
                margin-bottom: 1em;
            }
            .subtitle {
                text-align: center;
                color: #64748b;
                font-size: 1.2em;
                margin-bottom: 2em;
            }
            .final-output {
                font-size: 1.1em;
                line-height: 1.8;
                padding: 1.5em;
                background: #f8fafc;
                border-radius: 10px;
                border-left: 4px solid #667eea;
                color: #1e293b;
                overflow: visible;
                max-height: none;
            }
            .final-output h1 {
                color: #1e293b;
                border-bottom: 2px solid #667eea;
                padding-bottom: 0.5em;
            }
            .final-output h2 {
                color: #334155;
                margin-top: 1.5em;
            }
            .final-output h3 {
                color: #475569;
                margin-top: 1.2em;
                font-weight: 600;
            }
            .final-output h4 {
                color: #64748b;
                margin-top: 1em;
                font-weight: 600;
            }
            .final-output h5, .final-output h6 {
                color: #64748b;
                font-weight: 600;
            }
            .final-output p, .final-output li {
                color: #1e293b;
            }
            .final-output strong, .final-output b {
                color: #1e293b;
                font-weight: 700;
            }
            .final-output table {
                color: #1e293b;
                border-collapse: collapse;
                margin: 1em 0;
            }
            .final-output th, .final-output td {
                color: #1e293b;
                border: 1px solid #cbd5e1;
                padding: 8px;
                text-align: left;
            }
            .final-output th {
                background-color: #f1f5f9;
                font-weight: 600;
            }
            .markdown-text {
                color: #1e293b;
            }
            .prose {
                max-width: none !important;
                max-height: none !important;
            }
            .overflow-y-auto {
                max-height: none !important;
            }
            """
        ) as interface:

            # Header
            gr.HTML("""
            <div class="title">🧠 DualMind Orchestrator</div>
            <div class="subtitle">GAN-Inspired Multi-Agent Task Planning & Execution System</div>
            """)

            # Input section
            with gr.Row():
                with gr.Column(scale=3):
                    query_input = gr.Textbox(
                        label="Enter your query",
                        placeholder="e.g., Summarize recent AI breakthroughs in climate research and generate a visual report",
                        lines=3,
                        show_label=True
                    )

                with gr.Column(scale=1):
                    submit_btn = gr.Button(
                        "🚀 Execute Query",
                        variant="primary",
                        size="lg"
                    )

            # Results section
            with gr.Tab("🎉 Answer"):
                gr.HTML("""<div style='text-align: center; padding: 1em; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px; margin-bottom: 1em;'>
                    <h2 style='margin: 0;'>📖 Your Answer</h2>
                    <p style='margin: 0.5em 0 0 0; opacity: 0.9;'>Complete answer synthesized from all sources</p>
                </div>""")
                
                final_output = gr.Markdown(
                    value="Your answer will appear here after query execution...",
                    show_label=False,
                    elem_classes="final-output"
                )
            
            with gr.Tab("📋 Execution Details"):
                with gr.Row():
                    with gr.Column():
                        plan_output = gr.Markdown(
                            label="🎯 Planning Phase",
                            value="Planning results will appear here..."
                        )
                    with gr.Column():
                        verification_output = gr.Markdown(
                            label="🔍 Verification Phase",
                            value="Verification results will appear here..."
                        )

                with gr.Row():
                    with gr.Column():
                        execution_output = gr.Markdown(
                            label="⚙️ Execution Phase",
                            value="Execution results will appear here..."
                        )
                    with gr.Column():
                        summary_output = gr.Markdown(
                            label="📊 Summary",
                            value="Execution summary will appear here..."
                        )

            # Examples section
            gr.Examples(
                examples=[
                    "Summarize recent AI breakthroughs in climate research and generate a visual report.",
                    "Research the latest developments in quantum computing and create a comprehensive overview.",
                    "Analyze sentiment in recent news about renewable energy and visualize the trends.",
                    "Create a report on machine learning applications in healthcare with academic sources."
                ],
                inputs=query_input,
                label="💡 Example Queries"
            )

            # Footer
            gr.HTML("""
            <div style="text-align: center; margin-top: 2em; color: #64748b;">
                <p>🤖 Powered by DualMind Orchestrator - GAN-Inspired Multi-Agent System</p>
                <p>Built with ❤️ using Gradio, OpenRouter, and HuggingFace</p>
            </div>
            """)

            # Event handlers
            submit_btn.click(
                fn=self.process_query,
                inputs=[query_input],
                outputs=[plan_output, verification_output, execution_output, summary_output, final_output]
            )

        return interface


def create_ui() -> gr.Blocks:
    """
    Factory function to create the UI.

    Returns:
        gr.Blocks: The Gradio interface
    """
    ui = DualMindUI()
    return ui.create_interface()


# Standalone interface creation for testing
if __name__ == "__main__":
    ui = create_ui()
    ui.launch(server_name="0.0.0.0", server_port=7860, share=False)
