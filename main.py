#!/usr/bin/env python3
"""
DualMind Orchestrator - Main Entry Point
GAN-Inspired Multi-Agent Task Planning & Execution System
"""

import os
import sys
import logging
import argparse
import socket
from pathlib import Path

# Add the current directory to Python path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def setup_logging(log_level: str = "INFO", log_file: str = "logs/dualmind.log"):
    """
    Set up logging configuration with UTF-8 encoding support for Windows.

    Args:
        log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file (str): Path to log file
    """
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Fix Windows console encoding for Unicode/emoji support
    if sys.platform == 'win32':
        import io
        # Reconfigure stdout and stderr to use UTF-8
        if sys.stdout.encoding != 'utf-8':
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        if sys.stderr.encoding != 'utf-8':
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

    # Configure logging with UTF-8 encoding
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

    logger = logging.getLogger(__name__)
    logger.info("Logging initialized with UTF-8 encoding")

def check_dependencies():
    """Check if all required dependencies are installed."""
    required_packages = [
        'openai', 'requests', 'transformers', 'bs4',
        'matplotlib', 'pandas', 'fpdf', 'gradio', 'flask',
        'json', 'time', 'logging', 'os', 'dotenv'
    ]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"  • {package}")
        print("\nPlease install missing packages:")
        print(f"pip install {' '.join(missing_packages)}")
        return False

    print("✅ All required packages are installed")
    return True

def create_env_file():
    """Create a .env file template if it doesn't exist."""
    env_file = ".env"

    if not os.path.exists(env_file):
        env_content = """# DualMind Orchestrator Environment Configuration
# Copy this file and rename it to .env, then fill in your API keys

# OpenRouter API Key (for LLM access)
# Get your free API key from: https://openrouter.ai/
OPENROUTER_API_KEY=your_openrouter_api_key_here

# NewsAPI Key (optional, for news fetching)
# Get your free API key from: https://newsapi.org/
NEWSAPI_KEY=demo_key

# Optional: Custom model settings
# OPENROUTER_MODEL=meta-llama/llama-3.2-3b-instruct:free

# Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Server settings
GRADIO_SERVER_PORT=7860
GRADIO_SHARE=False
"""

        try:
            with open(env_file, 'w') as f:
                f.write(env_content)
            print("📝 Created .env template file")
            print("Please edit .env file and add your API keys before running")
        except Exception as e:
            print(f"❌ Error creating .env file: {e}")
    else:
        print("✅ .env file already exists")

def main():
    """Main entry point for DualMind Orchestrator."""
    parser = argparse.ArgumentParser(
        description="DualMind Orchestrator - GAN-Inspired Multi-Agent System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Run with default settings
  python main.py --port 8080        # Run on custom port
  python main.py --check-deps       # Check dependencies only
  python main.py --create-env       # Create .env template
        """
    )

    parser.add_argument(
        '--port', '-p',
        type=int,
        default=7860,
        help='Port to run the Gradio server on (default: 7860)'
    )

    parser.add_argument(
        '--host',
        default='0.0.0.0',
        help='Host to bind the server to (default: 0.0.0.0)'
    )

    parser.add_argument(
        '--share',
        action='store_true',
        help='Create a public link (requires Gradio account)'
    )

    parser.add_argument(
        '--check-deps',
        action='store_true',
        help='Check if all dependencies are installed'
    )

    parser.add_argument(
        '--create-env',
        action='store_true',
        help='Create .env template file'
    )

    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='INFO',
        help='Set logging level (default: INFO)'
    )

    args = parser.parse_args()

    # Handle special actions
    if args.check_deps:
        success = check_dependencies()
        sys.exit(0 if success else 1)

    if args.create_env:
        create_env_file()
        return

    # Check dependencies before proceeding
    if not check_dependencies():
        print("\n❌ Please install missing dependencies and try again.")
        sys.exit(1)

    # Create .env file if it doesn't exist
    create_env_file()

    # Setup logging
    setup_logging(args.log_level)

    logger = logging.getLogger(__name__)

    try:
        # Import and start the UI
        logger.info("Starting DualMind Orchestrator...")

        from ui import create_ui

        # Create the interface
        interface = create_ui()

        # Resolve server settings with environment overrides
        env_port = os.getenv('GRADIO_SERVER_PORT')
        env_share = os.getenv('GRADIO_SHARE')
        try:
            port = int(env_port) if env_port else int(args.port)
        except Exception:
            port = int(args.port)

        share_flag = args.share
        if isinstance(env_share, str):
            share_flag = env_share.lower() in ("1", "true", "yes")

        # Helper: check if a port is free
        def _is_port_free(host: str, p: int) -> bool:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    s.bind((host, p))
                return True
            except OSError:
                return False

        # If desired port is busy, search for a free one in a small range
        chosen_port = port
        if not _is_port_free(args.host, chosen_port):
            for candidate in range(port, port + 50):
                if _is_port_free(args.host, candidate):
                    chosen_port = candidate
                    break

        if chosen_port != port:
            logger.warning(f"Port {port} is busy. Using available port {chosen_port} instead.")

        # Launch the server
        logger.info(f"Launching Gradio server on {args.host}:{chosen_port}")
        interface.launch(
            server_name=args.host,
            server_port=chosen_port,
            share=share_flag,
            show_api=False
        )

    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error starting DualMind Orchestrator: {e}")
        print(f"\n❌ Error: {e}")
        print("Please check the logs for more details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
