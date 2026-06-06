#!/usr/bin/env python3
"""
Portable Offline AI Document Reader - Auto Mode
Automatically detects display and runs GUI or Headless mode
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.logger import get_logger

logger = get_logger(__name__)


def has_display():
    """Check if display is available"""
    try:
        # Check DISPLAY environment variable (Linux)
        if 'DISPLAY' in os.environ and os.environ['DISPLAY']:
            return True
        
        # Try to import tkinter to test GUI capability
        import tkinter as tk
        root = tk.Tk()
        root.destroy()
        return True
    except Exception as e:
        logger.debug(f"Display check: {e}")
        return False


def run_gui_mode():
    """Run GUI mode with CustomTkinter"""
    try:
        logger.info("Running in GUI Mode")
        from ui.main_window import MainWindow
        import customtkinter as ctk
        
        root = ctk.CTk()
        app = MainWindow(root)
        logger.info("Application window created successfully")
        root.mainloop()
    
    except Exception as e:
        logger.error(f"GUI mode failed: {e}")
        print(f"GUI Error: {e}")
        # Fall back to headless
        run_headless_mode_interactive()


def run_headless_mode():
    """Run headless mode with CLI"""
    try:
        logger.info("Running in Headless Mode (CLI)")
        from app_headless import main
        main()
    except Exception as e:
        logger.error(f"Headless mode error: {e}")
        print(f"Error: {e}")
        sys.exit(1)


def run_headless_mode_interactive():
    """Run interactive headless mode"""
    print("\n" + "=" * 60)
    print("🖥️  No Display Detected - Running in Headless Mode")
    print("=" * 60)
    print("\nAvailable modes:")
    print("1. REST API Server  - Access via web browser (recommended)")
    print("2. Command Line     - Execute single commands")
    print("3. Interactive CLI  - Interactive command mode")
    
    choice = input("\nSelect mode (1-3, default: 1): ").strip() or "1"
    
    if choice == "1":
        run_api_mode()
    elif choice == "2":
        run_headless_mode()
    elif choice == "3":
        run_interactive_cli()
    else:
        run_api_mode()


def run_api_mode():
    """Run REST API server mode"""
    try:
        logger.info("Starting REST API Server")
        print("\n" + "=" * 60)
        print("🌐 REST API Server - Headless Mode")
        print("=" * 60)
        print("\n✅ Server starting...")
        print("   Web Interface: http://localhost:5000")
        print("   API Base URL:  http://localhost:5000/api")
        print("\n📚 API Key (change in app_api.py): your-api-key-change-me")
        print("\n💡 Example requests:")
        print("   GET  /api/health           - Check health")
        print("   GET  /api/stats            - Get statistics")
        print("   GET  /api/documents        - List documents")
        print("   POST /api/scan             - Scan image")
        print("   GET  /api/search?q=query   - Search documents")
        print("\nPress Ctrl+C to stop server\n")
        
        from app_api import app
        app.run(host='0.0.0.0', port=5000, debug=False)
    
    except Exception as e:
        logger.error(f"API mode error: {e}")
        print(f"Error: {e}")
        sys.exit(1)


def run_interactive_cli():
    """Run interactive CLI mode"""
    try:
        logger.info("Starting Interactive CLI Mode")
        from app_headless import HeadlessApp
        
        app = HeadlessApp()
        
        print("\n" + "=" * 60)
        print("🖥️  Interactive CLI Mode")
        print("=" * 60)
        print("Commands: scan, capture, list, search, get, analyze, summarize, ask, export, stats, quit")
        print("Type 'help' for more information\n")
        
        while True:
            try:
                cmd = input(">>> ").strip().lower()
                
                if not cmd:
                    continue
                elif cmd == "quit" or cmd == "exit":
                    print("Goodbye!")
                    break
                elif cmd == "help":
                    print_cli_help()
                elif cmd == "list":
                    docs = app.list_documents()
                    for doc in docs:
                        print(f"  [{doc['id']}] {doc['title']} ({doc['language']})")
                elif cmd == "stats":
                    stats = app.get_stats()
                    print(f"Total documents: {stats.get('total_documents', 0)}")
                    print(f"Total text: {stats.get('total_text_length', 0)} chars")
                elif cmd.startswith("search "):
                    query = cmd[7:]
                    results = app.search(query)
                    print(f"Found {len(results)} results")
                    for r in results:
                        print(f"  - {r.get('title', 'Untitled')}")
                elif cmd.startswith("get "):
                    doc_id = int(cmd[4:])
                    doc = app.get_document(doc_id)
                    print(f"Title: {doc.get('title')}")
                    print(f"Language: {doc.get('language')}")
                    print(f"Content preview: {doc.get('content', '')[:200]}...")
                else:
                    print("Unknown command. Type 'help' for commands.")
            
            except KeyboardInterrupt:
                print("\nInterrupted")
                break
            except Exception as e:
                print(f"Error: {e}")
        
        app.cleanup()
    
    except Exception as e:
        logger.error(f"Interactive CLI error: {e}")
        print(f"Error: {e}")
        sys.exit(1)


def print_cli_help():
    """Print CLI help"""
    print("""
Available Commands:
  list              - List all documents
  stats             - Show statistics
  search <query>    - Search documents
  get <id>          - Get document details
  analyze <id>      - Analyze document
  summarize <id>    - Summarize document
  ask <id> <q>      - Ask question about document
  export <id> <fmt> - Export document (txt, pdf, docx, md)
  help              - Show this help
  quit/exit         - Exit interactive mode
    """)


def main():
    """Main entry point - Auto-detect mode"""
    logger.info("=" * 60)
    logger.info("Starting Portable Offline AI Document Reader")
    logger.info("=" * 60)
    
    # Check for command-line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "api":
            run_api_mode()
        elif sys.argv[1] == "cli":
            run_headless_mode()
        elif sys.argv[1] == "interactive":
            run_interactive_cli()
        else:
            # Pass remaining arguments to headless mode
            run_headless_mode()
        return
    
    # Auto-detect display
    if has_display():
        print("✅ Display detected - Running GUI Mode")
        run_gui_mode()
    else:
        print("⚠️  No display detected")
        # Check if running in terminal
        if sys.stdin.isatty():
            # Interactive terminal - show menu
            run_headless_mode_interactive()
        else:
            # Non-interactive - default to API
            print("Running in API server mode...")
            run_api_mode()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        print("\nShutdown complete")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"Fatal error: {e}")
        sys.exit(1)
