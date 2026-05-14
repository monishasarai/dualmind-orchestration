# 🧠 DualMind Orchestrator

A **GAN-Inspired Multi-Agent Task Planning & Execution System** that demonstrates intelligent task planning, tool usage, adversarial self-verification, and report generation.

## 🌟 Overview

DualMind Orchestrator implements a novel approach to AI task execution using a **Generator-Discriminator architecture** inspired by Generative Adversarial Networks (GANs):

- **Planner LLM (Generator)**: Creates structured task pipelines by analyzing user queries and available tools
- **Verifier LLM (Discriminator)**: Reviews and critiques the Planner's output, detecting errors and suggesting improvements
- **Orchestrator**: Coordinates the entire process, executing tools and managing the feedback loop

## ✨ Key Features

- 🤖 **Multi-Agent Architecture**: Planner and Verifier LLMs work together in an adversarial setup
- 🔧 **Extensible Tool System**: Modular tools for various tasks (research, summarization, analysis, visualization)
- ✅ **Self-Verification**: Automatic plan validation and improvement suggestions
- 📊 **Visual Interface**: Beautiful Gradio UI showing the complete reasoning process
- 📄 **PDF Report Generation**: Automatic creation of structured reports
- 🛠️ **Fallback Mechanisms**: Works even when APIs are unavailable (demo mode)

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐
│   User Query    │───▶│   Planner LLM    │
│                 │    │   (Generator)    │
└─────────────────┘    └──────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │   Verifier LLM   │
                       │ (Discriminator)  │
                       └──────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │  Orchestrator    │
                       │   (Coordinator)  │
                       └──────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │   Tool Chain     │
                       │   Execution      │
                       └──────────────────┘
```

## 🧰 Available Tools

1. **ArXiv Summarizer**: Fetches and summarizes academic papers
2. **Wikipedia Search**: Retrieves information from Wikipedia
3. **News Fetcher**: Gets latest news articles
4. **Sentiment Analyzer**: Performs sentiment analysis on text
5. **Data Plotter**: Creates visualizations (charts, graphs)
6. **QA Engine**: Answers questions using LLM
7. **Document Writer**: Generates PDF reports

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the project
cd dualmind_orchestrator

# Install dependencies
pip install -r requirements.txt

# Optional: Install PyTorch for better transformer performance
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### 2. Configuration

1. Copy the `.env` file:
   ```bash
   cp .env .env.local
   ```

2. Edit `.env.local` and add your API keys:
   ```env
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   NEWSAPI_KEY=your_newsapi_key_here  # Optional
   ```

3. Get free API keys:
   - **OpenRouter**: https://openrouter.ai/ (for LLM access)
   - **NewsAPI**: https://newsapi.org/ (optional, for news fetching)

### 3. Run the System

```bash
python main.py
```

The system will start a Gradio interface at `http://localhost:7860`

## 📖 Usage Examples

### Example 1: Research & Report Generation
```
Query: "Summarize recent AI breakthroughs in climate research and generate a visual report."
```

**System Response:**
- 📋 **Planning**: Creates a 4-step pipeline (research → news → analysis → report)
- 🔍 **Verification**: Validates plan logic and tool selection
- ⚙️ **Execution**: Runs tools sequentially with progress tracking
- 📄 **Output**: Comprehensive PDF report with visualizations

### Example 2: Data Analysis & Visualization
```
Query: "Analyze sentiment in recent news about renewable energy and visualize the trends."
```

**System Response:**
- 📋 **Planning**: Selects news fetching and sentiment analysis tools
- 🔍 **Verification**: Ensures proper data flow and analysis approach
- ⚙️ **Execution**: Processes articles and creates sentiment visualizations
- 📊 **Output**: Sentiment trend charts and analysis summary

## 🔧 Tool Development

### Adding New Tools

1. Create a new file in `tools/` directory:
   ```python
   # tools/my_new_tool.py
   def my_new_tool(input_data: str) -> str:
       # Tool implementation
       return "Tool output"
   ```

2. Update `tools_description.json`:
   ```json
   {
     "name": "my_new_tool",
     "description": "Description of what the tool does",
     "input": "input description",
     "output": "output description"
   }
   ```

3. The system will automatically discover and use the new tool!

## 🧪 Demo Mode

The system includes intelligent fallbacks for when APIs are unavailable:

- **LLM Fallbacks**: Predefined responses for common queries
- **News Fallbacks**: Demo articles for testing
- **PDF Generation**: Always works with local libraries
- **All Features**: Fully functional even without API keys

## 📁 Project Structure

```
dualmind_orchestrator/
├── main.py                 # Entry point
├── planner.py             # Planner LLM (Generator)
├── verifier.py            # Verifier LLM (Discriminator)
├── orchestrator.py        # Coordination logic
├── ui.py                  # Gradio interface
├── tools/                 # Tool implementations
│   ├── arxiv_summarizer.py
│   ├── wikipedia_search.py
│   ├── news_fetcher.py
│   ├── sentiment_analyzer.py
│   ├── data_plotter.py
│   ├── qa_engine.py
│   └── document_writer.py
├── tools_description.json # Tool definitions
├── requirements.txt       # Python dependencies
├── .env                   # Environment configuration
├── logs/                  # Execution logs
└── output/                # Generated files (PDFs, charts)
```

## 🔬 Technical Details

### GAN-Inspired Design

- **Generator (Planner)**: Creates task plans that maximize utility
- **Discriminator (Verifier)**: Evaluates plans for correctness and efficiency
- **Adversarial Training**: Iterative improvement through feedback loops

### Key Innovations

1. **Dynamic Tool Selection**: Intelligent matching of queries to available tools
2. **Self-Verification**: Automatic detection of plan flaws and inefficiencies
3. **Fallback Resilience**: Graceful degradation when external services fail
4. **Transparent Reasoning**: Full visibility into AI decision-making process

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all requirements are installed
   ```bash
   pip install -r requirements.txt
   ```

2. **API Key Issues**: Use demo/fallback mode for testing
   ```bash
   # The system works without API keys in demo mode
   OPENROUTER_API_KEY=demo_key
   ```

3. **Port Conflicts**: Change the default port
   ```bash
   python main.py --port 8080
   ```

4. **Memory Issues**: For large reports, ensure sufficient RAM (4GB+ recommended)

## 📈 Performance Tips

- Use CPU-optimized PyTorch for better performance
- Enable GPU acceleration if available for transformer models
- Monitor logs for performance bottlenecks
- Use the `--log-level DEBUG` flag for detailed diagnostics

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- [ ] Enhanced tool discovery and composition
- [ ] Advanced verification algorithms
- [ ] Memory and context management
- [ ] Performance optimizations
- [ ] Additional tool integrations

## 📄 License

This project is for educational and demonstration purposes. Please respect API terms of service.

## 🙏 Acknowledgments

- Inspired by HuggingGPT and other multi-agent AI systems
- Built with open-source tools and free-tier APIs
- Thanks to the AI research community for advancing these concepts

---


