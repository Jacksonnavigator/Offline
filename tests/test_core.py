"""
Unit tests for core modules
"""

import pytest
import cv2
import numpy as np
from pathlib import Path
from utils.image_utils import ImageUtils
from utils.logger import get_logger
from storage.database import DatabaseManager
from ocr.ocr_engine import OCREngine
from storage.search_engine import SearchEngine

logger = get_logger(__name__)


class TestImageUtils:
    """Test image utilities"""
    
    def test_grayscale_conversion(self):
        """Test converting image to grayscale"""
        # Create dummy BGR image
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        gray = ImageUtils.convert_to_grayscale(image)
        assert len(gray.shape) == 2
        assert gray.shape == (100, 100)
    
    def test_image_resize(self):
        """Test image resizing"""
        image = np.zeros((1000, 1500, 3), dtype=np.uint8)
        resized = ImageUtils.resize_image(image, width=500, height=300)
        assert resized.shape[0] <= 300
        assert resized.shape[1] <= 500
    
    def test_blur_application(self):
        """Test blur application"""
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        blurred = ImageUtils.apply_blur(image, kernel_size=5)
        assert blurred.shape == image.shape
    
    def test_edge_detection(self):
        """Test edge detection"""
        image = np.zeros((100, 100), dtype=np.uint8)
        edges = ImageUtils.apply_edge_detection(image)
        assert edges.shape == image.shape
    
    def test_thresholding(self):
        """Test binary thresholding"""
        image = np.random.randint(0, 256, (100, 100), dtype=np.uint8)
        binary = ImageUtils.apply_thresholding(image, threshold=127)
        unique_values = np.unique(binary)
        assert len(unique_values) <= 2  # Should only be 0 and 255


class TestDatabase:
    """Test database operations"""
    
    @pytest.fixture
    def db(self):
        """Create test database"""
        db = DatabaseManager(db_path=":memory:")
        yield db
        db.disconnect()
    
    def test_save_document(self, db):
        """Test saving document"""
        doc_id = db.save_document(
            title="Test Document",
            content="This is test content",
            language="en",
            image_path="/path/to/image.jpg"
        )
        assert doc_id is not None
    
    def test_load_document(self, db):
        """Test loading document"""
        # Save a document
        doc_id = db.save_document(
            title="Test",
            content="Content",
            language="en",
            image_path=""
        )
        
        # Load it back
        doc = db.load_document(doc_id)
        assert doc is not None
        assert doc['title'] == "Test"
        assert doc['content'] == "Content"
    
    def test_update_document(self, db):
        """Test updating document"""
        doc_id = db.save_document(
            title="Original",
            content="Original content",
            language="en",
            image_path=""
        )
        
        db.update_document(doc_id, title="Updated", content="Updated content")
        doc = db.load_document(doc_id)
        assert doc['title'] == "Updated"
        assert doc['content'] == "Updated content"
    
    def test_delete_document(self, db):
        """Test deleting document"""
        doc_id = db.save_document(
            title="To Delete",
            content="Content",
            language="en",
            image_path=""
        )
        
        db.delete_document(doc_id)
        doc = db.load_document(doc_id)
        assert doc is None
    
    def test_list_documents(self, db):
        """Test listing documents"""
        # Add multiple documents
        for i in range(3):
            db.save_document(
                title=f"Doc {i}",
                content=f"Content {i}",
                language="en",
                image_path=""
            )
        
        docs = db.list_documents(limit=100)
        assert len(docs) == 3


class TestSearchEngine:
    """Test search functionality"""
    
    @pytest.fixture
    def search_engine(self):
        """Create test search engine with in-memory database"""
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            engine = SearchEngine(db_path=f.name)
            yield engine
    
    def test_keyword_extraction(self, search_engine):
        """Test keyword extraction"""
        content = "This is a test document with important keywords"
        keywords = search_engine._extract_keywords(content)
        assert len(keywords) > 0
        assert "test" in keywords
        assert "document" in keywords
    
    def test_index_document(self, search_engine):
        """Test document indexing"""
        content = "Python is a programming language"
        success = search_engine.index_document(1, content)
        assert success is True


class TestOCREngine:
    """Test OCR functionality"""
    
    def test_ocr_engine_initialization(self):
        """Test OCR engine initialization"""
        ocr = OCREngine(engine="paddle")
        # Should initialize without error
        assert ocr is not None
        assert ocr.get_primary_engine_name() == "paddle"


class TestLogger:
    """Test logging functionality"""
    
    def test_logger_creation(self):
        """Test logger creation"""
        test_logger = get_logger("test_module")
        assert test_logger is not None
        
        # Log a message
        test_logger.info("Test log message")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
