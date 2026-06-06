"""
Main application window using CustomTkinter
"""

import customtkinter as ctk
from pathlib import Path
import json
from typing import Optional
from utils.logger import get_logger, load_config

logger = get_logger(__name__)


class MainWindow:
    """Main application window"""
    
    def __init__(self, root: ctk.CTk):
        """
        Initialize main window
        
        Args:
            root: CustomTkinter root window
        """
        self.root = root
        self.config = load_config()
        self.current_screen = None
        self.screens = {}
        
        self._setup_window()
        self._create_ui()
        
        logger.info("Main window initialized")
    
    def _setup_window(self):
        """Setup main window properties"""
        try:
            app_config = self.config.get('app', {})
            window_width = app_config.get('window_width', 1400)
            window_height = app_config.get('window_height', 900)
            theme = app_config.get('theme', 'dark')
            app_name = app_config.get('name', 'Portable Offline AI Document Reader')
            
            # Set theme
            ctk.set_appearance_mode(theme)
            ctk.set_default_color_theme("blue")
            
            # Configure window
            self.root.title(app_name)
            self.root.geometry(f"{window_width}x{window_height}")
            self.root.minsize(1200, 700)
            
            # Handle window close
            self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
            
            logger.info(f"Window setup: {window_width}x{window_height}, theme: {theme}")
        
        except Exception as e:
            logger.error(f"Error setting up window: {e}")
    
    def _create_ui(self):
        """Create main UI structure"""
        try:
            # Create grid configuration
            self.root.grid_rowconfigure(0, weight=1)
            self.root.grid_columnconfigure(0, weight=0)
            self.root.grid_columnconfigure(1, weight=1)
            
            # Create sidebar with navigation
            self._create_sidebar()
            
            # Create main content area
            self.content_frame = ctk.CTkFrame(self.root)
            self.content_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
            self.content_frame.grid_rowconfigure(0, weight=1)
            self.content_frame.grid_columnconfigure(0, weight=1)
            
            # Lazy load screens
            self._show_screen("dashboard")
            
            logger.info("UI created successfully")
        
        except Exception as e:
            logger.error(f"Error creating UI: {e}")
    
    def _create_sidebar(self):
        """Create navigation sidebar"""
        try:
            sidebar = ctk.CTkFrame(self.root, width=200, corner_radius=0)
            sidebar.grid(row=0, column=0, sticky="nsew")
            sidebar.grid_columnconfigure(0, weight=1)
            
            # Title
            title = ctk.CTkLabel(
                sidebar,
                text="AI Document\nReader",
                font=ctk.CTkFont(size=16, weight="bold"),
                justify="center"
            )
            title.grid(row=0, column=0, padx=10, pady=20)
            
            # Navigation buttons
            nav_buttons = [
                ("Dashboard", "dashboard"),
                ("Scan Document", "scan"),
                ("Documents", "documents"),
                ("Search", "search"),
                ("AI Assistant", "ai"),
                ("Settings", "settings")
            ]
            
            for idx, (label, screen_id) in enumerate(nav_buttons, start=1):
                btn = ctk.CTkButton(
                    sidebar,
                    text=label,
                    command=lambda s=screen_id: self._show_screen(s),
                    height=40,
                    corner_radius=8
                )
                btn.grid(row=idx, column=0, padx=10, pady=5, sticky="ew")
            
            # Spacer
            spacer = ctk.CTkLabel(sidebar, text="")
            spacer.grid(row=len(nav_buttons) + 1, column=0, sticky="ew")
            sidebar.grid_rowconfigure(len(nav_buttons) + 1, weight=1)
            
            # Exit button
            exit_btn = ctk.CTkButton(
                sidebar,
                text="Exit",
                command=self._on_closing,
                height=40,
                corner_radius=8,
                fg_color="red"
            )
            exit_btn.grid(row=len(nav_buttons) + 2, column=0, padx=10, pady=10, sticky="ew")
            
            logger.info("Sidebar created")
        
        except Exception as e:
            logger.error(f"Error creating sidebar: {e}")
    
    def _show_screen(self, screen_id: str):
        """
        Show specific screen
        
        Args:
            screen_id: Screen identifier
        """
        try:
            # Hide current screen if any
            if self.current_screen:
                self.current_screen.pack_forget()
            
            # Load screen if not already loaded
            if screen_id not in self.screens:
                self._load_screen(screen_id)
            
            # Show screen
            if screen_id in self.screens:
                self.screens[screen_id].pack(fill="both", expand=True)
                self.current_screen = self.screens[screen_id]
                logger.info(f"Showing screen: {screen_id}")
        
        except Exception as e:
            logger.error(f"Error showing screen {screen_id}: {e}")
    
    def _load_screen(self, screen_id: str):
        """
        Load screen module dynamically
        
        Args:
            screen_id: Screen identifier
        """
        try:
            from ui.dashboard_screen import DashboardScreen
            from ui.scan_screen import ScanScreen
            from ui.documents_screen import DocumentsScreen
            from ui.search_screen import SearchScreen
            from ui.ai_assistant_screen import AIAssistantScreen
            from ui.settings_screen import SettingsScreen
            
            screen_map = {
                "dashboard": DashboardScreen,
                "scan": ScanScreen,
                "documents": DocumentsScreen,
                "search": SearchScreen,
                "ai": AIAssistantScreen,
                "settings": SettingsScreen
            }
            
            screen_class = screen_map.get(screen_id)
            if screen_class:
                screen = screen_class(self.content_frame, self.config)
                self.screens[screen_id] = screen
                logger.info(f"Screen loaded: {screen_id}")
            else:
                logger.error(f"Unknown screen: {screen_id}")
        
        except ImportError as e:
            logger.error(f"Error loading screen module: {e}")
        except Exception as e:
            logger.error(f"Error loading screen {screen_id}: {e}")
    
    def _on_closing(self):
        """Handle window closing"""
        try:
            logger.info("Application closing")
            self.root.quit()
            self.root.destroy()
        except Exception as e:
            logger.error(f"Error closing application: {e}")
