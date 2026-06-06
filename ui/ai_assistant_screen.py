"""AI Assistant screen for document analysis and Q&A"""
import customtkinter as ctk
from ai.question_answering import QuestionAnswering
from storage.document_manager import DocumentManager
from utils.logger import get_logger

logger = get_logger(__name__)


class AIAssistantScreen(ctk.CTkFrame):
    """Screen for AI-powered document analysis and Q&A"""
    
    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config
        self.qa = QuestionAnswering()
        self.doc_manager = DocumentManager()
        self.current_document = None
        self._create_widgets()
    
    def _create_widgets(self):
        try:
            # Title
            title = ctk.CTkLabel(self, text="AI Assistant", font=ctk.CTkFont(size=24, weight="bold"))
            title.pack(pady=20)
            
            # Main frame
            main_frame = ctk.CTkFrame(self)
            main_frame.pack(fill="both", expand=True, padx=20, pady=10)
            main_frame.grid_columnconfigure(0, weight=0)
            main_frame.grid_columnconfigure(1, weight=1)
            
            # Document selector
            doc_frame = ctk.CTkFrame(main_frame)
            doc_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
            
            doc_label = ctk.CTkLabel(doc_frame, text="Select Document:", font=ctk.CTkFont(size=12, weight="bold"))
            doc_label.pack()
            
            # Load documents
            docs = self.doc_manager.list_all_documents(limit=20)
            doc_titles = [f"{d.get('title', 'Untitled')} (ID: {d['id']})" for d in docs]
            
            self.doc_menu = ctk.CTkComboBox(doc_frame, values=doc_titles if doc_titles else ["No documents"])
            self.doc_menu.pack(padx=5, pady=5, fill="x")
            
            load_btn = ctk.CTkButton(doc_frame, text="Load", command=self._load_selected_document)
            load_btn.pack(padx=5, pady=5)
            
            # Chat area
            chat_frame = ctk.CTkFrame(main_frame)
            chat_frame.grid(row=0, column=1, sticky="nsew", rowspan=2, padx=5, pady=5)
            chat_frame.grid_rowconfigure(0, weight=1)
            
            self.chat_display = ctk.CTkTextbox(chat_frame, height=300, state="disabled")
            self.chat_display.pack(fill="both", expand=True, padx=5, pady=5)
            
            # Question input
            input_frame = ctk.CTkFrame(main_frame)
            input_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
            
            self.question_input = ctk.CTkEntry(input_frame, placeholder_text="Ask a question...")
            self.question_input.pack(fill="x", padx=5, pady=5)
            self.question_input.bind("<Return>", lambda e: self._ask_question())
            
            ask_btn = ctk.CTkButton(input_frame, text="Ask", command=self._ask_question)
            ask_btn.pack(padx=5, pady=5)
        
        except Exception as e:
            logger.error(f"Error creating AI assistant screen: {e}")
    
    def _load_selected_document(self):
        try:
            selection = self.doc_menu.get()
            if selection and "ID:" in selection:
                doc_id = int(selection.split("ID: ")[1].rstrip(")"))
                self.current_document = self.doc_manager.get_document(doc_id)
                if self.current_document:
                    self._add_to_chat("System", f"Document loaded: {self.current_document.get('title', 'Untitled')}")
                    logger.info(f"Document loaded: {doc_id}")
        except Exception as e:
            logger.error(f"Error loading document: {e}")
    
    def _ask_question(self):
        try:
            if not self.current_document:
                self._add_to_chat("System", "Please load a document first.")
                return
            
            question = self.question_input.get().strip()
            if not question:
                return
            
            self._add_to_chat("You", question)
            self.question_input.delete(0, "end")
            
            # Get answer
            result = self.qa.answer_question(self.current_document.get('content', ''), question)
            if result:
                self._add_to_chat("Assistant", result.get('answer', ''))
            else:
                self._add_to_chat("System", "Could not get answer. Ollama may not be running.")
        
        except Exception as e:
            logger.error(f"Error asking question: {e}")
            self._add_to_chat("System", f"Error: {str(e)}")
    
    def _add_to_chat(self, sender, message):
        try:
            self.chat_display.configure(state="normal")
            self.chat_display.insert("end", f"{sender}: {message}\n\n")
            self.chat_display.see("end")
            self.chat_display.configure(state="disabled")
        except Exception as e:
            logger.error(f"Error adding to chat: {e}")
