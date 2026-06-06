"""Documents screen showing list of scanned documents"""
import customtkinter as ctk
from storage.document_manager import DocumentManager
from utils.logger import get_logger

logger = get_logger(__name__)


class DocumentsScreen(ctk.CTkFrame):
    """Screen for viewing and managing documents"""
    
    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config
        self.doc_manager = DocumentManager()
        self._create_widgets()
        self._load_documents()
    
    def _create_widgets(self):
        try:
            # Title
            title = ctk.CTkLabel(self, text="Documents", font=ctk.CTkFont(size=24, weight="bold"))
            title.pack(pady=20)
            
            # List frame
            list_frame = ctk.CTkFrame(self)
            list_frame.pack(fill="both", expand=True, padx=20, pady=10)
            
            # Create scrollable frame for documents
            self.documents_frame = ctk.CTkScrollableFrame(list_frame)
            self.documents_frame.pack(fill="both", expand=True)
            
        except Exception as e:
            logger.error(f"Error creating documents screen: {e}")
    
    def _load_documents(self):
        try:
            # Clear existing widgets
            for widget in self.documents_frame.winfo_children():
                widget.destroy()
            
            # Load documents
            docs = self.doc_manager.list_all_documents(limit=50)
            
            if not docs:
                no_docs = ctk.CTkLabel(self.documents_frame, text="No documents yet. Start by scanning a document!")
                no_docs.pack(pady=20)
                return
            
            # Display each document
            for doc in docs:
                self._create_document_item(doc)
        
        except Exception as e:
            logger.error(f"Error loading documents: {e}")
    
    def _create_document_item(self, doc):
        try:
            item_frame = ctk.CTkFrame(self.documents_frame, corner_radius=8)
            item_frame.pack(fill="x", padx=5, pady=5)
            
            # Title and info
            title = ctk.CTkLabel(item_frame, text=doc.get('title', 'Untitled'), 
                                font=ctk.CTkFont(size=12, weight="bold"), justify="left")
            title.pack(anchor="w", padx=10, pady=(10, 0))
            
            info = f"Language: {doc.get('language', 'unknown')} | Words: {doc.get('word_count', 0)} | Confidence: {doc.get('ocr_confidence', 0):.1%}"
            info_label = ctk.CTkLabel(item_frame, text=info, font=ctk.CTkFont(size=10), text_color="gray")
            info_label.pack(anchor="w", padx=10)
            
            # Preview of content
            content = doc.get('content', '')[:200] + "..."
            content_label = ctk.CTkLabel(item_frame, text=content, justify="left", wraplength=400)
            content_label.pack(anchor="w", padx=10, pady=(0, 10))
        
        except Exception as e:
            logger.error(f"Error creating document item: {e}")
