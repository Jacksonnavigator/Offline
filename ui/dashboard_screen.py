"""Dashboard screen showing application overview"""
import customtkinter as ctk
from storage.document_manager import DocumentManager
from utils.logger import get_logger

logger = get_logger(__name__)


class DashboardScreen(ctk.CTkFrame):
    """Dashboard showing statistics and overview"""
    
    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config
        self.doc_manager = DocumentManager()
        self._create_widgets()
    
    def _create_widgets(self):
        try:
            # Title
            title = ctk.CTkLabel(self, text="Dashboard", font=ctk.CTkFont(size=24, weight="bold"))
            title.pack(pady=20)
            
            # Statistics frame
            stats_frame = ctk.CTkFrame(self)
            stats_frame.pack(fill="x", padx=20, pady=10)
            
            stats = self.doc_manager.get_statistics()
            total_docs = stats.get('total_documents', 0)
            total_words = stats.get('total_words', 0)
            avg_confidence = stats.get('average_confidence', 0)
            
            # Stat cards
            self._create_stat_card(stats_frame, "Total Documents", str(total_docs), 0)
            self._create_stat_card(stats_frame, "Total Words", str(total_words), 1)
            self._create_stat_card(stats_frame, "Avg OCR Confidence", f"{avg_confidence:.1%}", 2)
            
            # Info section
            info_frame = ctk.CTkFrame(self)
            info_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            info_text = """
Portable Offline AI Document Reader
Version 1.0

Features:
• Camera document scanning
• Automatic document detection
• OCR with PaddleOCR and Tesseract
• AI document analysis with Ollama
• Text-to-speech with Piper
• Full-text search
• Multi-language support

Ready to get started?
Click "Scan Document" to begin!
            """
            
            info_label = ctk.CTkLabel(info_frame, text=info_text, justify="left", font=ctk.CTkFont(size=12))
            info_label.pack(pady=20)
            
        except Exception as e:
            logger.error(f"Error creating dashboard: {e}")
    
    def _create_stat_card(self, parent, title, value, column):
        card = ctk.CTkFrame(parent, corner_radius=10)
        card.grid(row=0, column=column, padx=10, pady=10, sticky="ew")
        
        title_label = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=12), text_color="gray")
        title_label.pack(pady=(10, 0))
        
        value_label = ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=20, weight="bold"))
        value_label.pack(pady=(0, 10))
        
        parent.grid_columnconfigure(column, weight=1)
