"""
Tesseract OCR wrapper for offline text extraction (fallback)
"""

import cv2
import numpy as np
from typing import Optional, Dict, List
from utils.logger import get_logger

logger = get_logger(__name__)


class TesseractOCREngine:
    """Tesseract OCR engine for text recognition (fallback)"""
    
    def __init__(self, languages: List[str] = None):
        """
        Initialize Tesseract OCR engine
        
        Args:
            languages: List of language codes (e.g., ['eng', 'swa', 'fra'])
        """
        self.languages = languages or ['eng']
        self.pytesseract = None
        self.confidence_threshold = 0.3
        
        try:
            import pytesseract
            self.pytesseract = pytesseract
            logger.info(f"Tesseract OCR initialized with languages: {self.languages}")
        except ImportError:
            logger.error("pytesseract not installed. Run: pip install pytesseract")
        except Exception as e:
            logger.error(f"Error initializing Tesseract: {e}")
    
    def extract_text(self, image: np.ndarray) -> Optional[Dict]:
        """
        Extract text from image using Tesseract
        
        Args:
            image: Input image (BGR numpy array)
        
        Returns:
            Dictionary with 'text', 'confidence', and 'language' or None if extraction fails
        """
        try:
            if self.pytesseract is None:
                logger.error("Tesseract OCR not initialized")
                return None
            
            # Convert BGR to RGB for Tesseract
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Preprocess image for better OCR accuracy
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            enhanced = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            # Run OCR
            config = '--psm 1 --oem 3'  # PSM 1: automatic page orientation and script detection
            text_data = self.pytesseract.image_to_data(
                enhanced, lang='+'.join(self.languages), config=config, output_type=self.pytesseract.Output.DICT
            )
            
            # Extract text and confidence
            full_text = ""
            confidences = []
            details = []
            
            for i, conf in enumerate(text_data['conf']):
                text = text_data['text'][i]
                confidence = int(conf) / 100.0  # Convert to 0-1 range
                
                if text.strip() and confidence >= self.confidence_threshold:
                    full_text += text + " "
                    confidences.append(confidence)
                    details.append({
                        "text": text,
                        "confidence": confidence
                    })
            
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            result = {
                "text": full_text.strip(),
                "confidence": avg_confidence,
                "language": self._detect_language(full_text),
                "details": details,
                "engine": "tesseract"
            }
            
            logger.info(f"Text extracted (Tesseract): {len(full_text)} chars, confidence: {avg_confidence:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Error extracting text with Tesseract: {e}")
            return None
    
    def extract_text_from_file(self, image_path: str) -> Optional[Dict]:
        """
        Extract text from image file
        
        Args:
            image_path: Path to image file
        
        Returns:
            Dictionary with OCR results or None if extraction fails
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"Failed to load image: {image_path}")
                return None
            
            return self.extract_text(image)
        except Exception as e:
            logger.error(f"Error extracting text from file {image_path}: {e}")
            return None
    
    def _detect_language(self, text: str) -> str:
        """
        Simple language detection based on character patterns
        
        Args:
            text: Input text
        
        Returns:
            Detected language code
        """
        try:
            from textblob import TextBlob
            blob = TextBlob(text)
            lang_code = blob.detect_language()
            
            # Map to Tesseract language codes
            mapping = {
                'en': 'eng',
                'sw': 'swa',
                'fr': 'fra',
                'ar': 'ara',
                'es': 'spa'
            }
            return mapping.get(lang_code, 'eng')
        except:
            # Fallback: simple heuristics
            if any('\u0600' <= c <= '\u06FF' for c in text):
                return 'ara'
            else:
                return 'eng'
    
    def set_confidence_threshold(self, threshold: float):
        """
        Set minimum confidence threshold
        
        Args:
            threshold: Confidence threshold (0.0 to 1.0)
        """
        self.confidence_threshold = max(0.0, min(1.0, threshold))
        logger.info(f"Tesseract confidence threshold set to {self.confidence_threshold}")
    
    def is_ready(self) -> bool:
        """
        Check if OCR engine is ready
        
        Returns:
            True if ready, False otherwise
        """
        return self.pytesseract is not None
