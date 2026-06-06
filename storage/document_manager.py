"""
Document manager for handling document operations
"""

from pathlib import Path
from typing import Optional, List, Dict
from storage.database import DatabaseManager
from utils.logger import get_logger

logger = get_logger(__name__)


class DocumentManager:
    """Manages document operations and storage"""
    
    def __init__(self, db_path: str = "./data/documents.db"):
        """
        Initialize document manager
        
        Args:
            db_path: Path to SQLite database
        """
        self.db = DatabaseManager(db_path)
        self.storage_path = Path("./documents")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        logger.info("DocumentManager initialized")
    
    def create_document(self, title: str, content: str, language: str = "en", 
                       image_path: str = "", ocr_confidence: float = 0.0, 
                       summary: str = "") -> Optional[int]:
        """
        Create and save a new document
        
        Args:
            title: Document title
            content: OCR extracted text
            language: Document language
            image_path: Path to scanned image
            ocr_confidence: OCR confidence score
            summary: Document summary
        
        Returns:
            Document ID or None if failed
        """
        try:
            doc_id = self.db.save_document(
                title=title,
                content=content,
                language=language,
                image_path=image_path,
                ocr_confidence=ocr_confidence,
                summary=summary
            )
            
            if doc_id:
                logger.info(f"Document created: {title} (ID: {doc_id})")
            
            return doc_id
        except Exception as e:
            logger.error(f"Error creating document: {e}")
            return None
    
    def get_document(self, doc_id: int) -> Optional[Dict]:
        """
        Get document by ID
        
        Args:
            doc_id: Document ID
        
        Returns:
            Document dictionary or None
        """
        try:
            return self.db.load_document(doc_id)
        except Exception as e:
            logger.error(f"Error getting document: {e}")
            return None
    
    def update_document(self, doc_id: int, title: str = None, content: str = None,
                       summary: str = None) -> bool:
        """
        Update document
        
        Args:
            doc_id: Document ID
            title: New title
            content: New content
            summary: New summary
        
        Returns:
            True if successful
        """
        try:
            success = self.db.update_document(
                doc_id=doc_id,
                title=title,
                content=content,
                summary=summary
            )
            
            if success:
                logger.info(f"Document {doc_id} updated")
            
            return success
        except Exception as e:
            logger.error(f"Error updating document: {e}")
            return False
    
    def delete_document(self, doc_id: int, delete_image: bool = False) -> bool:
        """
        Delete document
        
        Args:
            doc_id: Document ID
            delete_image: Whether to delete associated image file
        
        Returns:
            True if successful
        """
        try:
            doc = self.db.load_document(doc_id)
            
            if delete_image and doc and doc['image_path']:
                try:
                    image_path = Path(doc['image_path'])
                    if image_path.exists():
                        image_path.unlink()
                        logger.info(f"Deleted image: {doc['image_path']}")
                except Exception as e:
                    logger.warning(f"Could not delete image: {e}")
            
            success = self.db.delete_document(doc_id)
            
            if success:
                logger.info(f"Document {doc_id} deleted")
            
            return success
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            return False
    
    def list_all_documents(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        List all documents
        
        Args:
            limit: Maximum number of results
            offset: Results to skip
        
        Returns:
            List of documents
        """
        try:
            return self.db.list_documents(limit=limit, offset=offset)
        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            return []
    
    def search_documents(self, query: str) -> List[Dict]:
        """
        Search documents
        
        Args:
            query: Search query
        
        Returns:
            List of matching documents
        """
        try:
            return self.db.search_documents(query)
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []
    
    def get_statistics(self) -> Dict:
        """
        Get document statistics
        
        Returns:
            Statistics dictionary
        """
        try:
            return self.db.get_storage_stats()
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}
    
    def get_total_documents(self) -> int:
        """Get total document count"""
        try:
            return self.db.get_document_count()
        except Exception as e:
            logger.error(f"Error getting document count: {e}")
            return 0
    
    def export_document_text(self, doc_id: int) -> Optional[str]:
        """
        Get document text for export
        
        Args:
            doc_id: Document ID
        
        Returns:
            Document content or None
        """
        try:
            doc = self.db.load_document(doc_id)
            if doc:
                return doc.get('content', '')
            return None
        except Exception as e:
            logger.error(f"Error getting document text: {e}")
            return None
    
    def close(self):
        """Close database connection"""
        try:
            self.db.disconnect()
        except Exception as e:
            logger.error(f"Error closing document manager: {e}")
