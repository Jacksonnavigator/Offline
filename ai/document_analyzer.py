"""
Document analyzer using Ollama for AI-powered analysis
"""

import requests
import json
from typing import Optional, Dict
from utils.logger import get_logger

logger = get_logger(__name__)


class DocumentAnalyzer:
    """Analyzes documents using Ollama local models"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "neural-chat", timeout: int = 30):
        """
        Initialize document analyzer
        
        Args:
            base_url: Ollama API base URL
            model: Model name to use
            timeout: Request timeout in seconds
        """
        self.base_url = base_url
        self.model = model
        self.timeout = timeout
        self.is_ready = self._check_connection()
        
        logger.info(f"DocumentAnalyzer initialized: {base_url}, model: {model}")
    
    def _check_connection(self) -> bool:
        """
        Check if Ollama is running and accessible
        
        Returns:
            True if connection successful
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                logger.info("Ollama connection successful")
                return True
        except Exception as e:
            logger.warning(f"Ollama not available: {e}")
        
        return False
    
    def analyze_document(self, content: str) -> Optional[Dict]:
        """
        Analyze document content
        
        Args:
            content: Document text
        
        Returns:
            Analysis result with key points
        """
        try:
            if not self.is_ready:
                logger.error("Ollama not available")
                return None
            
            prompt = f"""Analyze the following document and provide:
1. Main topic
2. Key points (up to 5)
3. Sentiment (positive/negative/neutral)
4. Recommended action (if any)

Document:
{content}

Please provide a structured analysis."""
            
            result = self._call_ollama(prompt)
            
            if result:
                return {
                    "analysis": result,
                    "model": self.model,
                    "success": True
                }
            
            return None
        
        except Exception as e:
            logger.error(f"Error analyzing document: {e}")
            return None
    
    def identify_document_type(self, content: str, title: str = "") -> Optional[str]:
        """
        Identify type of document
        
        Args:
            content: Document content
            title: Document title
        
        Returns:
            Document type or None
        """
        try:
            if not self.is_ready:
                return None
            
            prompt = f"""Identify the type of this document. Categories: Invoice, Receipt, Contract, Letter, Report, Email, Form, Other.

Title: {title}
Content: {content[:500]}...

Respond with just the category name."""
            
            doc_type = self._call_ollama(prompt)
            if doc_type:
                logger.info(f"Document type identified: {doc_type}")
                return doc_type.strip()
            
            return None
        
        except Exception as e:
            logger.error(f"Error identifying document type: {e}")
            return None
    
    def extract_entities(self, content: str) -> Optional[Dict]:
        """
        Extract named entities from document
        
        Args:
            content: Document content
        
        Returns:
            Dictionary with extracted entities
        """
        try:
            if not self.is_ready:
                return None
            
            prompt = f"""Extract the following information from the text:
- Names (people, organizations)
- Dates
- Amounts/Money
- Locations
- Email addresses
- Phone numbers

Text: {content[:1000]}

Format as JSON."""
            
            result = self._call_ollama(prompt)
            
            if result:
                try:
                    return json.loads(result)
                except:
                    return {"raw": result}
            
            return None
        
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return None
    
    def validate_document_quality(self, content: str) -> Dict:
        """
        Validate OCR quality
        
        Args:
            content: OCR extracted text
        
        Returns:
            Quality assessment
        """
        try:
            if not self.is_ready:
                return {"quality": "unknown", "issues": []}
            
            prompt = f"""Assess the quality of this OCR text. Look for:
- Obvious OCR errors or garbled text
- Readable completeness
- Logic and coherence

Text sample: {content[:500]}

Respond with: QUALITY: [Good/Fair/Poor] and list any detected issues."""
            
            result = self._call_ollama(prompt)
            
            return {
                "assessment": result,
                "quality": self._parse_quality(result)
            }
        
        except Exception as e:
            logger.error(f"Error validating document: {e}")
            return {"quality": "unknown"}
    
    def _call_ollama(self, prompt: str) -> Optional[str]:
        """
        Call Ollama API
        
        Args:
            prompt: Prompt text
        
        Returns:
            Model response or None
        """
        try:
            url = f"{self.base_url}/api/generate"
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
            
            response = requests.post(url, json=payload, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "").strip()
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return None
        
        except requests.Timeout:
            logger.error("Ollama request timeout")
            return None
        except Exception as e:
            logger.error(f"Error calling Ollama: {e}")
            return None
    
    def _parse_quality(self, response: str) -> str:
        """
        Parse quality assessment response
        
        Args:
            response: Response text
        
        Returns:
            Quality level
        """
        response_upper = response.upper()
        if "GOOD" in response_upper:
            return "good"
        elif "FAIR" in response_upper:
            return "fair"
        elif "POOR" in response_upper:
            return "poor"
        return "unknown"
    
    def set_model(self, model: str) -> bool:
        """
        Set model to use
        
        Args:
            model: Model name
        
        Returns:
            True if set successfully
        """
        try:
            self.model = model
            logger.info(f"Model set to: {model}")
            return True
        except Exception as e:
            logger.error(f"Error setting model: {e}")
            return False
