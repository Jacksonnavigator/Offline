"""
SQLite database management for document storage
"""

import sqlite3
import threading
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from datetime import datetime
from utils.logger import get_logger

logger = get_logger(__name__)


class DatabaseManager:
    """Manages SQLite database for document storage"""
    
    def __init__(self, db_path: str = "./data/documents.db"):
        """
        Initialize database manager
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = None
        self._lock = threading.Lock()
        
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database and create tables if they don't exist"""
        try:
            self.connect()
            self._create_tables()
            logger.info(f"Database initialized at {self.db_path}")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
    
    def connect(self):
        """Connect to database"""
        try:
            # Allow access from multiple threads; serialize operations with a lock
            self.connection = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
            logger.info("Connected to database")
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            raise
    
    def disconnect(self):
        """Disconnect from database"""
        try:
            if self.connection:
                self.connection.close()
            logger.info("Disconnected from database")
        except Exception as e:
            logger.error(f"Error disconnecting from database: {e}")
    
    def _create_tables(self):
        """Create necessary database tables"""
        try:
            cursor = self.connection.cursor()
            
            # Documents table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT,
                    language TEXT,
                    image_path TEXT,
                    date_created TEXT NOT NULL,
                    date_modified TEXT NOT NULL,
                    word_count INTEGER DEFAULT 0,
                    character_count INTEGER DEFAULT 0,
                    summary TEXT,
                    search_index TEXT,
                    ocr_confidence REAL DEFAULT 0.0,
                    metadata TEXT
                )
            ''')
            
            # Search index table for faster searching
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS search_index (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id INTEGER NOT NULL,
                    keyword TEXT NOT NULL,
                    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
                )
            ''')
            
            # Create index on keyword for faster searches
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_keyword ON search_index(keyword)
            ''')
            
            # Settings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            ''')
            
            self.connection.commit()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            raise
    
    def execute_query(self, query: str, params: Tuple = ()) -> List[Dict]:
        """
        Execute a SELECT query
        
        Args:
            query: SQL query
            params: Query parameters
        
        Returns:
            List of result rows as dictionaries
        """
        try:
            with self._lock:
                cursor = self.connection.cursor()
                cursor.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return []
    
    def execute_update(self, query: str, params: Tuple = ()) -> bool:
        """
        Execute INSERT, UPDATE, or DELETE query
        
        Args:
            query: SQL query
            params: Query parameters
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with self._lock:
                cursor = self.connection.cursor()
                cursor.execute(query, params)
                self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"Error executing update: {e}")
            try:
                with self._lock:
                    self.connection.rollback()
            except Exception:
                pass
            return False
    
    def save_document(self, title: str, content: str, language: str, image_path: str, 
                     ocr_confidence: float = 0.0, summary: str = "") -> Optional[int]:
        """
        Save document to database
        
        Args:
            title: Document title
            content: OCR extracted text
            language: Document language
            image_path: Path to scanned image
            ocr_confidence: OCR confidence score
            summary: Document summary
        
        Returns:
            Document ID if successful, None otherwise
        """
        try:
            now = datetime.now().isoformat()
            word_count = len(content.split()) if content else 0
            character_count = len(content) if content else 0

            query = '''
                INSERT INTO documents 
                (title, content, language, image_path, date_created, date_modified, 
                 word_count, character_count, summary, ocr_confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''

            with self._lock:
                cursor = self.connection.cursor()
                cursor.execute(query, (
                    title, content, language, image_path,
                    now, now, word_count, character_count, summary, ocr_confidence
                ))
                self.connection.commit()
                doc_id = cursor.lastrowid

            logger.info(f"Document saved with ID: {doc_id}")
            return doc_id
        except Exception as e:
            logger.error(f"Error saving document: {e}")
            try:
                with self._lock:
                    self.connection.rollback()
            except Exception:
                pass
            return None
    
    def load_document(self, doc_id: int) -> Optional[Dict]:
        """
        Load document from database
        
        Args:
            doc_id: Document ID
        
        Returns:
            Document dictionary or None if not found
        """
        try:
            query = 'SELECT * FROM documents WHERE id = ?'
            results = self.execute_query(query, (doc_id,))
            
            if results:
                logger.info(f"Document {doc_id} loaded")
                return results[0]
            else:
                logger.warning(f"Document {doc_id} not found")
                return None
        except Exception as e:
            logger.error(f"Error loading document: {e}")
            return None
    
    def update_document(self, doc_id: int, title: str = None, content: str = None, 
                       summary: str = None) -> bool:
        """
        Update document in database
        
        Args:
            doc_id: Document ID
            title: New title (optional)
            content: New content (optional)
            summary: New summary (optional)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            updates = []
            params = []
            
            if title is not None:
                updates.append("title = ?")
                params.append(title)
            
            if content is not None:
                updates.append("content = ?")
                params.append(content)
                updates.append("word_count = ?")
                params.append(len(content.split()))
                updates.append("character_count = ?")
                params.append(len(content))
            
            if summary is not None:
                updates.append("summary = ?")
                params.append(summary)
            
            updates.append("date_modified = ?")
            params.append(datetime.now().isoformat())
            
            params.append(doc_id)
            
            query = f"UPDATE documents SET {', '.join(updates)} WHERE id = ?"
            success = self.execute_update(query, tuple(params))
            
            if success:
                logger.info(f"Document {doc_id} updated")
            
            return success
        except Exception as e:
            logger.error(f"Error updating document: {e}")
            return False
    
    def delete_document(self, doc_id: int) -> bool:
        """
        Delete document from database
        
        Args:
            doc_id: Document ID
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Delete from search index first (FK constraint)
            self.execute_update("DELETE FROM search_index WHERE document_id = ?", (doc_id,))
            
            # Delete document
            success = self.execute_update("DELETE FROM documents WHERE id = ?", (doc_id,))
            
            if success:
                logger.info(f"Document {doc_id} deleted")
            
            return success
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            return False
    
    def list_documents(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        List all documents
        
        Args:
            limit: Maximum number of results
            offset: Number of results to skip
        
        Returns:
            List of documents
        """
        try:
            query = '''
                SELECT id, title, language, date_created, word_count, 
                       character_count, ocr_confidence
                FROM documents
                ORDER BY date_modified DESC
                LIMIT ? OFFSET ?
            '''
            return self.execute_query(query, (limit, offset))
        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            return []
    
    def get_document_count(self) -> int:
        """Get total document count"""
        try:
            query = "SELECT COUNT(*) as count FROM documents"
            result = self.execute_query(query)
            return result[0]['count'] if result else 0
        except Exception as e:
            logger.error(f"Error getting document count: {e}")
            return 0
    
    def search_documents(self, query_text: str) -> List[Dict]:
        """
        Search documents by title or content
        
        Args:
            query_text: Search query
        
        Returns:
            List of matching documents
        """
        try:
            search_pattern = f"%{query_text}%"
            query = '''
                SELECT * FROM documents
                WHERE title LIKE ? OR content LIKE ?
                ORDER BY date_modified DESC
            '''
            return self.execute_query(query, (search_pattern, search_pattern))
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []
    
    def get_storage_stats(self) -> Dict:
        """Get storage statistics"""
        try:
            stats = {
                'total_documents': self.get_document_count(),
                'total_words': 0,
                'total_characters': 0,
                'average_confidence': 0.0
            }
            
            query = '''
                SELECT SUM(word_count) as total_words,
                       SUM(character_count) as total_chars,
                       AVG(ocr_confidence) as avg_confidence
                FROM documents
            '''
            result = self.execute_query(query)
            
            if result and result[0]:
                stats['total_words'] = result[0].get('total_words', 0) or 0
                stats['total_characters'] = result[0].get('total_chars', 0) or 0
                stats['average_confidence'] = result[0].get('avg_confidence', 0.0) or 0.0
            
            return stats
        except Exception as e:
            logger.error(f"Error getting storage stats: {e}")
            return {}
    
    def __del__(self):
        """Cleanup on object deletion"""
        self.disconnect()
