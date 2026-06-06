"""
Search engine for full-text search across documents
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Optional
from storage.database import DatabaseManager
from utils.logger import get_logger

logger = get_logger(__name__)


class SearchEngine:
    """Full-text search engine for documents"""
    
    def __init__(self, db_path: str = "./data/documents.db"):
        """
        Initialize search engine
        
        Args:
            db_path: Path to SQLite database
        """
        self.db = DatabaseManager(db_path)
        logger.info("SearchEngine initialized")
    
    def index_document(self, doc_id: int, content: str) -> bool:
        """
        Index document for searching
        
        Args:
            doc_id: Document ID
            content: Document content
        
        Returns:
            True if successful
        """
        try:
            # Extract keywords from content
            keywords = self._extract_keywords(content)
            
            # Clear old index
            self.db.execute_update("DELETE FROM search_index WHERE document_id = ?", (doc_id,))
            
            # Add new keywords
            for keyword in keywords:
                query = "INSERT INTO search_index (document_id, keyword) VALUES (?, ?)"
                self.db.execute_update(query, (doc_id, keyword.lower()))
            
            logger.info(f"Document {doc_id} indexed with {len(keywords)} keywords")
            return True
        
        except Exception as e:
            logger.error(f"Error indexing document: {e}")
            return False
    
    def search(self, query: str, limit: int = 50) -> List[Dict]:
        """
        Search documents
        
        Args:
            query: Search query
            limit: Maximum results
        
        Returns:
            List of matching documents
        """
        try:
            # Split query into keywords
            keywords = query.lower().split()
            
            if not keywords:
                return []
            
            # Build search query
            placeholders = ','.join(['?' for _ in keywords])
            sql_query = f'''
                SELECT DISTINCT d.*, COUNT(si.id) as match_count
                FROM documents d
                LEFT JOIN search_index si ON d.id = si.document_id
                WHERE si.keyword IN ({placeholders})
                GROUP BY d.id
                ORDER BY match_count DESC, d.date_modified DESC
                LIMIT ?
            '''
            
            results = self.db.execute_query(sql_query, (*keywords, limit))
            logger.info(f"Search found {len(results)} results for: {query}")
            return results
        
        except Exception as e:
            logger.error(f"Error searching: {e}")
            return []
    
    def search_exact(self, query: str) -> List[Dict]:
        """
        Search for exact phrase
        
        Args:
            query: Exact phrase
        
        Returns:
            List of matching documents
        """
        try:
            pattern = f"%{query}%"
            sql_query = '''
                SELECT * FROM documents
                WHERE content LIKE ? OR title LIKE ?
                ORDER BY date_modified DESC
            '''
            
            results = self.db.execute_query(sql_query, (pattern, pattern))
            logger.info(f"Exact search found {len(results)} results for: {query}")
            return results
        
        except Exception as e:
            logger.error(f"Error in exact search: {e}")
            return []
    
    def search_by_language(self, language: str) -> List[Dict]:
        """
        Search documents by language
        
        Args:
            language: Language code (e.g., 'en', 'fr')
        
        Returns:
            List of documents in that language
        """
        try:
            query = "SELECT * FROM documents WHERE language = ? ORDER BY date_modified DESC"
            results = self.db.execute_query(query, (language,))
            logger.info(f"Found {len(results)} documents in language: {language}")
            return results
        
        except Exception as e:
            logger.error(f"Error searching by language: {e}")
            return []
    
    def search_by_date_range(self, start_date: str, end_date: str) -> List[Dict]:
        """
        Search documents by date range
        
        Args:
            start_date: Start date (ISO format)
            end_date: End date (ISO format)
        
        Returns:
            List of documents in date range
        """
        try:
            query = '''
                SELECT * FROM documents
                WHERE date_created BETWEEN ? AND ?
                ORDER BY date_modified DESC
            '''
            results = self.db.execute_query(query, (start_date, end_date))
            logger.info(f"Found {len(results)} documents between {start_date} and {end_date}")
            return results
        
        except Exception as e:
            logger.error(f"Error searching by date: {e}")
            return []
    
    def rebuild_index(self) -> bool:
        """
        Rebuild search index for all documents
        
        Returns:
            True if successful
        """
        try:
            # Clear existing index
            self.db.execute_update("DELETE FROM search_index")
            
            # Get all documents
            documents = self.db.execute_query("SELECT id, content FROM documents")
            
            # Reindex each document
            for doc in documents:
                self.index_document(doc['id'], doc['content'])
            
            logger.info(f"Search index rebuilt for {len(documents)} documents")
            return True
        
        except Exception as e:
            logger.error(f"Error rebuilding index: {e}")
            return False
    
    def get_search_suggestions(self, partial_query: str, limit: int = 10) -> List[str]:
        """
        Get search suggestions based on partial query
        
        Args:
            partial_query: Partial search term
            limit: Maximum suggestions
        
        Returns:
            List of suggestions
        """
        try:
            pattern = f"{partial_query.lower()}%"
            query = '''
                SELECT DISTINCT keyword FROM search_index
                WHERE keyword LIKE ?
                GROUP BY keyword
                ORDER BY COUNT(*) DESC
                LIMIT ?
            '''
            
            results = self.db.execute_query(query, (pattern, limit))
            suggestions = [r['keyword'] for r in results]
            return suggestions
        
        except Exception as e:
            logger.error(f"Error getting suggestions: {e}")
            return []
    
    def _extract_keywords(self, content: str, min_length: int = 3) -> List[str]:
        """
        Extract keywords from content
        
        Args:
            content: Document content
            min_length: Minimum keyword length
        
        Returns:
            List of keywords
        """
        try:
            # Simple keyword extraction: split by whitespace and punctuation
            import re
            
            # Convert to lowercase and split
            words = re.findall(r'\b\w+\b', content.lower())
            
            # Filter by length and remove common stopwords
            stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                        'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being'}
            
            keywords = [w for w in words if len(w) >= min_length and w not in stopwords]
            
            # Remove duplicates while preserving order
            seen = set()
            unique_keywords = []
            for kw in keywords:
                if kw not in seen:
                    seen.add(kw)
                    unique_keywords.append(kw)
            
            return unique_keywords[:100]  # Limit to 100 keywords
        
        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
            return []
