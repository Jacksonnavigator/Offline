"""
Main OCR engine that manages both PaddleOCR and Tesseract
Provides fallback mechanism and language support
"""

import cv2
import numpy as np
from typing import Optional, Dict, List
from ocr.paddle_ocr import PaddleOCREngine
from ocr.tesseract_ocr import TesseractOCREngine
from utils.logger import get_logger

logger = get_logger(__name__)


class OCREngine:
    """
    Main OCR engine that manages multiple OCR backends
    Supports PaddleOCR (primary) with Tesseract fallback
    """
    
    def __init__(self, engine: str = "paddle", languages: List[str] = None, use_gpu: bool = False):
        """
        Initialize OCR engine
        
        Args:
            engine: Primary engine ('paddle' or 'tesseract')
            languages: List of supported languages
            use_gpu: Whether to use GPU for PaddleOCR
        """
        self.engine_type = engine
        self.languages = languages or ['en']
        self.use_gpu = use_gpu
        self.primary_engine = None
        self.fallback_engine = None
        
        self._initialize_engines()
    
    def _initialize_engines(self):
        """Initialize primary and fallback OCR engines"""
        try:
            if self.engine_type == "paddle":
                logger.info("Initializing PaddleOCR as primary engine")
                self.primary_engine = PaddleOCREngine(
                    languages=self.languages,
                    use_gpu=self.use_gpu
                )
                self.fallback_engine = TesseractOCREngine(
                    languages=self._map_languages_to_tesseract()
                )
            else:
                logger.info("Initializing Tesseract as primary engine")
                self.primary_engine = TesseractOCREngine(
                    languages=self._map_languages_to_tesseract()
                )
                self.fallback_engine = PaddleOCREngine(
                    languages=self.languages,
                    use_gpu=self.use_gpu
                )
            
            logger.info(f"OCR engines initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing OCR engines: {e}")
    
    def extract_text(self, image: np.ndarray, use_fallback: bool = True) -> Optional[Dict]:
        """
        Extract text from image
        
        Args:
            image: Input image (BGR numpy array)
            use_fallback: Whether to use fallback engine if primary fails
        
        Returns:
            Dictionary with 'text', 'confidence', 'language' and 'engine' or None
        """
        try:
            if self.primary_engine is None or not self.primary_engine.is_ready():
                logger.warning("Primary OCR engine not ready")
                if use_fallback and self.fallback_engine:
                    logger.info("Switching to fallback OCR engine")
                    return self.extract_text_with_fallback(image)
                return None
            
            # Try primary engine
            result = self.primary_engine.extract_text(image)
            
            if result and result['text']:
                return result
            
            # If primary fails or returns empty, try fallback
            if use_fallback and self.fallback_engine:
                logger.info("Primary engine returned empty result, trying fallback")
                return self.extract_text_with_fallback(image)
            
            return result
            
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            if use_fallback and self.fallback_engine:
                logger.info("Primary engine failed, trying fallback")
                return self.extract_text_with_fallback(image)
            return None
    
    def extract_text_with_fallback(self, image: np.ndarray) -> Optional[Dict]:
        """
        Extract text using fallback engine
        
        Args:
            image: Input image
        
        Returns:
            OCR result dictionary
        """
        try:
            if self.fallback_engine is None or not self.fallback_engine.is_ready():
                logger.error("Fallback OCR engine not available")
                return None
            
            return self.fallback_engine.extract_text(image)
        except Exception as e:
            logger.error(f"Error with fallback OCR engine: {e}")
            return None
    
    def extract_text_from_file(self, image_path: str) -> Optional[Dict]:
        """
        Extract text from image file
        
        Args:
            image_path: Path to image file
        
        Returns:
            OCR result dictionary or None
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"Failed to load image: {image_path}")
                return None
            
            return self.extract_text(image)
        except Exception as e:
            logger.error(f"Error extracting text from file: {e}")
            return None
    
    def _map_languages_to_tesseract(self) -> List[str]:
        """
        Map language codes to Tesseract format
        
        Args:
            None (uses self.languages)
        
        Returns:
            List of Tesseract language codes
        """
        mapping = {
            'en': 'eng',
            'sw': 'swa',
            'fr': 'fra',
            'ar': 'ara',
            'es': 'spa'
        }
        return [mapping.get(lang, 'eng') for lang in self.languages]
    
    def get_primary_engine_name(self) -> str:
        """Get primary engine name"""
        return self.engine_type
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages"""
        return self.languages
    
    def set_confidence_threshold(self, threshold: float):
        """
        Set confidence threshold for both engines
        
        Args:
            threshold: Confidence threshold (0.0 to 1.0)
        """
        if self.primary_engine:
            self.primary_engine.set_confidence_threshold(threshold)
        if self.fallback_engine:
            self.fallback_engine.set_confidence_threshold(threshold)
    
    def detect_language(self, text: str) -> str:
        """
        Detect language of text
        
        Args:
            text: Input text
        
        Returns:
            Language code
        """
        try:
            if self.primary_engine:
                return self.primary_engine._detect_language(text)
            return 'en'
        except Exception as e:
            logger.error(f"Error detecting language: {e}")
            return 'en'
    
    def is_ready(self) -> bool:
        """
        Check if OCR engine is ready
        
        Returns:
            True if primary engine is ready, False otherwise
        """
        return self.primary_engine is not None and self.primary_engine.is_ready()
