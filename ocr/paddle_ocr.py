"""
PaddleOCR wrapper for offline text extraction
"""

import cv2
import numpy as np
from typing import Optional, Dict, List
from utils.logger import get_logger

logger = get_logger(__name__)


class PaddleOCREngine:
    """PaddleOCR engine for text recognition"""
    
    def __init__(self, languages: List[str] = None, use_gpu: bool = False):
        """
        Initialize PaddleOCR engine
        
        Args:
            languages: List of language codes (e.g., ['en', 'sw', 'fr'])
            use_gpu: Whether to use GPU acceleration
        """
        self.languages = languages or ['en']
        self.use_gpu = use_gpu
        self.ocr = None
        self.confidence_threshold = 0.3
        
        try:
            from paddleocr import PaddleOCR
            logger.info(f"Initializing PaddleOCR with languages: {self.languages}, GPU: {use_gpu}")
            
            self.ocr = PaddleOCR(
                use_angle_cls=True,
                lang=self.languages,
                use_gpu=use_gpu,
                show_log=False
            )
            logger.info("PaddleOCR initialized successfully")
        except ImportError:
            logger.error("PaddleOCR not installed. Run: pip install paddleocr")
        except Exception as e:
            logger.error(f"Error initializing PaddleOCR: {e}")
    
    def extract_text(self, image: np.ndarray) -> Optional[Dict]:
        """
        Extract text from image
        
        Args:
            image: Input image (BGR numpy array)
        
        Returns:
            Dictionary with 'text', 'confidence', and 'language' or None if extraction fails
        """
        try:
            if self.ocr is None:
                logger.error("PaddleOCR not initialized")
                return None
            
            # Run OCR
            results = self.ocr.ocr(image, cls=True)
            
            if not results or not results[0]:
                logger.warning("No text detected in image")
                return {
                    "text": "",
                    "confidence": 0.0,
                    "language": "unknown",
                    "details": []
                }
            
            # Extract text and confidence
            full_text = ""
            avg_confidence = 0.0
            details = []
            
            for line in results[0]:
                for item in line:
                    text = item[1]
                    confidence = float(item[2])
                    
                    if confidence >= self.confidence_threshold:
                        full_text += text + " "
                        avg_confidence += confidence
                        details.append({
                            "text": text,
                            "confidence": confidence
                        })
            
            if details:
                avg_confidence /= len(details)
            
            result = {
                "text": full_text.strip(),
                "confidence": avg_confidence,
                "language": self._detect_language(full_text),
                "details": details,
                "engine": "paddle"
            }
            
            logger.info(f"Text extracted: {len(full_text)} chars, confidence: {avg_confidence:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Error extracting text with PaddleOCR: {e}")
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
            lang = blob.detect_language()
            return lang
        except:
            # Fallback: simple heuristics
            if any('\u0600' <= c <= '\u06FF' for c in text):
                return 'ar'
            elif any('\u0E00' <= c <= '\u0E7F' for c in text):
                return 'th'
            elif any('\u3040' <= c <= '\u309F' or '\u30A0' <= c <= '\u30FF' for c in text):
                return 'ja'
            else:
                return 'en'
    
    def set_confidence_threshold(self, threshold: float):
        """
        Set minimum confidence threshold for text recognition
        
        Args:
            threshold: Confidence threshold (0.0 to 1.0)
        """
        self.confidence_threshold = max(0.0, min(1.0, threshold))
        logger.info(f"Confidence threshold set to {self.confidence_threshold}")
    
    def get_languages(self) -> List[str]:
        """
        Get supported languages
        
        Returns:
            List of language codes
        """
        return self.languages
    
    def is_ready(self) -> bool:
        """
        Check if OCR engine is ready
        
        Returns:
            True if ready, False otherwise
        """
        return self.ocr is not None
