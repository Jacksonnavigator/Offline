"""
Question-answering system using Ollama for answering questions about documents
"""

from typing import Optional, Dict, List
from ai.document_analyzer import DocumentAnalyzer
from utils.logger import get_logger

logger = get_logger(__name__)


class QuestionAnswering:
    """Answers questions about documents using Ollama"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "neural-chat", timeout: int = 30):
        """
        Initialize Q&A system
        
        Args:
            base_url: Ollama API base URL
            model: Model name to use
            timeout: Request timeout in seconds
        """
        self.analyzer = DocumentAnalyzer(base_url, model, timeout)
        self.conversation_history: List[Dict] = []
        logger.info("QuestionAnswering initialized")
    
    def answer_question(self, document_content: str, question: str, context: bool = True) -> Optional[Dict]:
        """
        Answer question about document
        
        Args:
            document_content: Document text
            question: Question to answer
            context: Include document context in response
        
        Returns:
            Dictionary with answer and confidence
        """
        try:
            if not self.analyzer.is_ready:
                logger.error("Ollama not available")
                return None
            
            # Prepare prompt
            if context:
                prompt = f"""Based on the following document, answer the question:

DOCUMENT:
{document_content}

QUESTION: {question}

ANSWER:"""
            else:
                prompt = f"""Answer this question: {question}

ANSWER:"""
            
            answer = self.analyzer._call_ollama(prompt)
            
            if answer:
                result = {
                    "question": question,
                    "answer": answer,
                    "success": True
                }
                
                # Add to conversation history
                self.conversation_history.append({
                    "role": "user",
                    "content": question
                })
                self.conversation_history.append({
                    "role": "assistant",
                    "content": answer
                })
                
                logger.info(f"Question answered: {question[:50]}...")
                return result
            
            return None
        
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return None
    
    def clarify_term(self, document_content: str, term: str) -> Optional[str]:
        """
        Clarify or explain a specific term from document
        
        Args:
            document_content: Document text
            term: Term to clarify
        
        Returns:
            Explanation of term
        """
        try:
            if not self.analyzer.is_ready:
                return None
            
            prompt = f"""In the context of the following document, explain what "{term}" means:

{document_content}

Explanation:"""
            
            explanation = self.analyzer._call_ollama(prompt)
            
            if explanation:
                logger.info(f"Term clarified: {term}")
                return explanation
            
            return None
        
        except Exception as e:
            logger.error(f"Error clarifying term: {e}")
            return None
    
    def find_answer_in_document(self, document_content: str, question: str) -> Optional[Dict]:
        """
        Find specific information in document
        
        Args:
            document_content: Document text
            question: Question/Information to find
        
        Returns:
            Found information with context
        """
        try:
            if not self.analyzer.is_ready:
                return None
            
            prompt = f"""Find and extract the information requested from the document.
If not found, say "Not found in document".

DOCUMENT:
{document_content}

QUERY: {question}

RESULT:"""
            
            result = self.analyzer._call_ollama(prompt)
            
            if result and "Not found" not in result:
                return {
                    "query": question,
                    "found": True,
                    "information": result
                }
            else:
                return {
                    "query": question,
                    "found": False,
                    "information": None
                }
        
        except Exception as e:
            logger.error(f"Error finding answer: {e}")
            return None
    
    def ask_followup(self, follow_up_question: str) -> Optional[Dict]:
        """
        Ask follow-up question in conversation
        
        Args:
            follow_up_question: Follow-up question
        
        Returns:
            Dictionary with answer
        """
        try:
            if not self.analyzer.is_ready:
                return None
            
            if not self.conversation_history:
                logger.warning("No conversation history")
                return None
            
            # Build context from conversation history
            context = "Previous conversation:\n"
            for msg in self.conversation_history[-4:]:  # Last 2 exchanges
                role = msg['role'].upper()
                context += f"{role}: {msg['content']}\n"
            
            prompt = f"""{context}

FOLLOW-UP QUESTION: {follow_up_question}

ANSWER:"""
            
            answer = self.analyzer._call_ollama(prompt)
            
            if answer:
                self.conversation_history.append({
                    "role": "user",
                    "content": follow_up_question
                })
                self.conversation_history.append({
                    "role": "assistant",
                    "content": answer
                })
                
                return {
                    "question": follow_up_question,
                    "answer": answer,
                    "success": True
                }
            
            return None
        
        except Exception as e:
            logger.error(f"Error asking follow-up: {e}")
            return None
    
    def get_conversation_history(self) -> List[Dict]:
        """
        Get conversation history
        
        Returns:
            List of conversation messages
        """
        return self.conversation_history.copy()
    
    def clear_conversation_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        logger.info("Conversation history cleared")
    
    def generate_qa_pairs(self, document_content: str, num_pairs: int = 5) -> Optional[List[Dict]]:
        """
        Generate Q&A pairs from document
        
        Args:
            document_content: Document text
            num_pairs: Number of Q&A pairs to generate
        
        Returns:
            List of Q&A pairs
        """
        try:
            if not self.analyzer.is_ready:
                return None
            
            prompt = f"""Generate {num_pairs} important question-answer pairs from this document:

{document_content}

Format:
Q1: [question]
A1: [answer]
Q2: [question]
A2: [answer]
..."""
            
            result = self.analyzer._call_ollama(prompt)
            
            if result:
                qa_pairs = self._parse_qa_pairs(result)
                logger.info(f"Generated {len(qa_pairs)} Q&A pairs")
                return qa_pairs
            
            return None
        
        except Exception as e:
            logger.error(f"Error generating Q&A pairs: {e}")
            return None
    
    @staticmethod
    def _parse_qa_pairs(text: str) -> List[Dict]:
        """
        Parse Q&A pairs from text
        
        Args:
            text: Text containing Q&A pairs
        
        Returns:
            List of Q&A pair dictionaries
        """
        pairs = []
        lines = text.split('\n')
        
        current_q = None
        current_a = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('Q'):
                if current_q and current_a:
                    pairs.append({"question": current_q, "answer": current_a})
                # Extract question
                current_q = line.split(':', 1)[1].strip() if ':' in line else None
                current_a = None
            elif line.startswith('A') and current_q:
                # Extract answer
                current_a = line.split(':', 1)[1].strip() if ':' in line else None
        
        # Add last pair
        if current_q and current_a:
            pairs.append({"question": current_q, "answer": current_a})
        
        return pairs
