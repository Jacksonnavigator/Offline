"""Search screen for searching documents"""
import customtkinter as ctk
from storage.search_engine import SearchEngine
from utils.logger import get_logger

logger = get_logger(__name__)


class SearchScreen(ctk.CTkFrame):
    """Screen for searching documents"""
    
    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config
        self.search_engine = SearchEngine()
        self._create_widgets()
    
    def _create_widgets(self):
        try:
            # Title
            title = ctk.CTkLabel(self, text="Search Documents", font=ctk.CTkFont(size=24, weight="bold"))
            title.pack(pady=20)
            
            # Search input frame
            search_frame = ctk.CTkFrame(self)
            search_frame.pack(fill="x", padx=20, pady=10)
            
            self.search_input = ctk.CTkEntry(search_frame, placeholder_text="Enter search query...")
            self.search_input.pack(side="left", fill="x", expand=True, padx=(0, 10))
            self.search_input.bind("<Return>", lambda e: self._perform_search())
            
            search_btn = ctk.CTkButton(search_frame, text="Search", command=self._perform_search, width=100)
            search_btn.pack(side="left")
            
            # Results frame
            results_frame = ctk.CTkFrame(self)
            results_frame.pack(fill="both", expand=True, padx=20, pady=10)
            
            results_label = ctk.CTkLabel(results_frame, text="Results:", font=ctk.CTkFont(size=12, weight="bold"))
            results_label.pack(anchor="w", pady=(0, 10))
            
            self.results_frame = ctk.CTkScrollableFrame(results_frame)
            self.results_frame.pack(fill="both", expand=True)
        
        except Exception as e:
            logger.error(f"Error creating search screen: {e}")
    
    def _perform_search(self):
        try:
            query = self.search_input.get().strip()
            if not query:
                return
            
            # Clear results
            for widget in self.results_frame.winfo_children():
                widget.destroy()
            
            # Search
            results = self.search_engine.search(query)
            
            if not results:
                no_results = ctk.CTkLabel(self.results_frame, text=f"No results found for '{query}'")
                no_results.pack(pady=20)
                return
            
            # Display results
            for result in results:
                self._create_result_item(result)
        
        except Exception as e:
            logger.error(f"Error performing search: {e}")
    
    def _create_result_item(self, result):
        try:
            item = ctk.CTkFrame(self.results_frame, corner_radius=8)
            item.pack(fill="x", padx=5, pady=5)
            
            title = ctk.CTkLabel(item, text=result.get('title', 'Untitled'),
                                font=ctk.CTkFont(size=12, weight="bold"))
            title.pack(anchor="w", padx=10, pady=(10, 0))
            
            preview = result.get('content', '')[:150] + "..."
            preview_label = ctk.CTkLabel(item, text=preview, justify="left", wraplength=400)
            preview_label.pack(anchor="w", padx=10, pady=(0, 10))
        
        except Exception as e:
            logger.error(f"Error creating result item: {e}")
