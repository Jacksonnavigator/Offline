"""
Document summarizer using Ollama for AI-powered summarization
"""

from typing import Optional, Dict
from ai.document_analyzer import DocumentAnalyzer
from utils.logger import get_logger

logger = get_logger(__name__)


class DocumentSummarizer:
    """Generates summaries of documents using Ollama"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "neural-chat", timeout: int = 30):
        """
        Initialize document summarizer
        
        Args:
            base_url: Ollama API base URL
            model: Model name to use
            timeout: Request timeout in seconds
        """
        self.analyzer = DocumentAnalyzer(base_url, model, timeout)
        logger.info("DocumentSummarizer initialized")
    
    def generate_short_summary(self, content: str, max_sentences: int = 3) -> Optional[str]:
        """
        Generate short summary
        
        Args:
            content: Document content
            max_sentences: Maximum sentences in summary
        
        Returns:
            Summary text or None
        """
        try:
            if not self.analyzer.is_ready:
                logger.error("Ollama not available")
                return None
            
            prompt = f"""Summarize the following text in {max_sentences} sentences:

{content}

Summary:"""
            
            summary = self.analyzer._call_ollama(prompt)
            
            if summary:
                logger.info(f"Short summary generated ({len(summary)} chars)")
                return summary
            
            return None
        
        except Exception as e:
            logger.error(f"Error generating short summary: {e}")
            return None
    
    def generate_detailed_summary(self, content: str) -> Optional[Dict]:
        """
        Generate detailed summary with sections
        
        Args:
            content: Document content
        
        Returns:
            Dictionary with summary sections
        """
        try:
            if not self.analyzer.is_ready:
                return None
            
            prompt = f"""Provide a detailed summary of the following document:

{content}

Include:
1. Overview
2. Main Points
3. Important Details
4. Conclusion

Use markdown formatting."""
            
            summary = self.analyzer._call_ollama(prompt)
            
            if summary:
                return {
                    "summary": summary,
                    "type": "detailed",
                    "success": True
                }
            
            return None
        
        except Exception as e:
            logger.error(f"Error generating detailed summary: {e}")
            return None
    
    def extract_key_points(self, content: str, num_points: int = 5) -> Optional[list]:
        """
        Extract key points from document
        
        Args:
            content: Document content
            num_points: Number of key points to extract
        
        Returns:
            List of key points
        """
        try:
            if not self.analyzer.is_ready:
                return None
            
            prompt = f"""Extract {num_points} key points from the following text as a numbered list:

{content}

Key Points:"""
            
            result = self.analyzer._call_ollama(prompt)
            
            if result:
                # Parse the numbered list
                points = []
                for line in result.split('\n'):
                    line = line.strip()
                    if line and (line[0].isdigit() or line.startswith('-')):
                        # Remove numbering or bullets
                        point = line.lstrip('0123456789.-) ').strip()
                        if point:
                            points.append(point)
                
                logger.info(f"Extracted {len(points)} key points")
                return points if points else None
            
            return None
        
        except Exception as e:
            logger.error(f"Error extracting key points: {e}")
            return None
    
    def generate_abstractive_summary(self, content: str) -> Optional[str]:
        """
        Generate abstractive summary (rephrased)
        
        Args:
            content: Document content
        
        Returns:
            Abstractive summary
        """
        try:
            if not self.analyzer.is_ready:
                return None
            
            prompt = f"""Rephrase and summarize the following text in your own words:

{content}

Rephrased summary:"""
            
            summary = self.analyzer._call_ollama(prompt)
            
            if summary:
                logger.info(f"Abstractive summary generated ({len(summary)} chars)")
                return summary
            
            return None
        
        except Exception as e:
            logger.error(f"Error generating abstractive summary: {e}")
            return None
    
    def estimate_reading_time(self, content: str) -> Optional[Dict]:
        """
        Estimate reading time for content
        
        Args:
            content: Document content
        
        Returns:
            Dictionary with reading time estimate
        """
        try:
            words = len(content.split())
            # Average reading speed: 200-250 words per minute
            minutes = max(1, words // 200)
            
            return {
                "words": words,
                "estimated_minutes": minutes,
                "estimated_seconds": minutes * 60
            }
        
        except Exception as e:
            logger.error(f"Error estimating reading time: {e}")
            return None
    
    def generate_outline(self, content: str) -> Optional[str]:
        """
        Generate document outline
        
        Args:
            content: Document content
        
        Returns:
            Document outline
        """
        try:
            if not self.analyzer.is_ready:
                return None
            
            prompt = f"""Create an outline of the following document:

{content}

Use hierarchical structure with main topics and sub-topics."""
            
            outline = self.analyzer._call_ollama(prompt)
            
            if outline:
                logger.info("Document outline generated")
                return outline
            
            return None
        
        except Exception as e:
            logger.error(f"Error generating outline: {e}")
            return None
