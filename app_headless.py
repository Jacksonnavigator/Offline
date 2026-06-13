"""
Portable Offline AI Document Reader - Headless/CLI Mode
For Raspberry Pi and systems without display
"""

import sys
import argparse
from pathlib import Path
from storage.document_manager import DocumentManager
from storage.search_engine import SearchEngine
from ocr.ocr_engine import OCREngine
from camera.capture import CameraCapture
from ai.document_analyzer import DocumentAnalyzer
from ai.document_summarizer import DocumentSummarizer
from ai.question_answering import QuestionAnswering
from utils.export import ExportEngine
from utils.logger import get_logger, load_config
from speech.tts_engine import speak_text

logger = get_logger(__name__)


class HeadlessApp:
    """Headless application for CLI/API operation"""
    
    def __init__(self):
        """Initialize headless app"""
        self.config = load_config()
        self.doc_manager = DocumentManager()
        self.search_engine = SearchEngine()
        self.ocr = OCREngine(engine=self.config.get('ocr', {}).get('engine', 'tesseract'))
        self.analyzer = DocumentAnalyzer()
        self.summarizer = DocumentSummarizer()
        self.qa = QuestionAnswering()
        self.export = ExportEngine()
        self.camera = None
        
        logger.info("Headless application initialized")
    
    def scan_document(self, image_path: str, title: str = "Document") -> dict:
        """
        Scan and process a document from file
        
        Args:
            image_path: Path to image file
            title: Document title
        
        Returns:
            Processing result
        """
        try:
            import cv2
            from camera.document_detection import DocumentDetector
            from utils.image_utils import ImageUtils
            
            logger.info(f"Processing document: {image_path}")
            
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                return {"success": False, "error": "Could not load image"}
            
            # Detect document
            detector = DocumentDetector()
            contour = detector.detect_document(image)
            
            if contour is not None:
                flattened = detector.flatten_document(image, contour)
                if flattened is not None:
                    # Enhance image
                    enhanced = ImageUtils.enhance_contrast(flattened)
                    enhanced = ImageUtils.remove_noise(enhanced)
                    
                    # Run OCR
                    ocr_result = self.ocr.extract_text(enhanced)
                    
                    if ocr_result:
                        # Save document
                        doc_id = self.doc_manager.create_document(
                            title=title,
                            content=ocr_result.get('text', ''),
                            language=ocr_result.get('language', 'en'),
                            image_path=image_path,
                            ocr_confidence=ocr_result.get('confidence', 0.0)
                        )

                        # Optionally speak the extracted text
                        try:
                            if self.config.get('features', {}).get('enable_speech', False):
                                voice = self.config.get('speech', {}).get('voice')
                                rate = float(self.config.get('speech', {}).get('rate', 1.0))
                                text = ocr_result.get('text', '') or ''
                                if text.strip():
                                    logger.info('Speaking extracted text...')
                                    # speak_text blocks until playback completes
                                    speak_text(text, voice=voice, rate=rate)
                        except Exception as e:
                            logger.warning(f"TTS playback failed: {e}")
                        
                        return {
                            "success": True,
                            "doc_id": doc_id,
                            "text": ocr_result.get('text', ''),
                            "confidence": ocr_result.get('confidence', 0.0),
                            "language": ocr_result.get('language', 'en')
                        }
            
            return {"success": False, "error": "Could not detect document"}
        
        except Exception as e:
            logger.error(f"Error scanning document: {e}")
            return {"success": False, "error": str(e)}
    
    def capture_from_camera(self, title: str = "Document", num_frames: int = 5) -> dict:
        """
        Capture and process from camera
        
        Args:
            title: Document title
            num_frames: Number of frames to capture
        
        Returns:
            Processing result
        """
        try:
            if self.camera is None:
                self.camera = CameraCapture()
                self.camera.start_camera()
            
            logger.info("Capturing from camera...")
            images = []
            
            for i in range(num_frames):
                frame = self.camera.capture_frame()
                if frame is not None:
                    images.append(frame)
                    print(f"Captured frame {i+1}/{num_frames}")
            
            # Use best frame (middle one)
            if images:
                best_frame = images[len(images)//2]
                image_path = "./images/capture.jpg"
                import cv2
                Path("./images").mkdir(exist_ok=True)
                cv2.imwrite(image_path, best_frame)
                
                return self.scan_document(image_path, title)
            
            return {"success": False, "error": "No frames captured"}
        
        except Exception as e:
            logger.error(f"Error capturing: {e}")
            return {"success": False, "error": str(e)}
    
    def list_documents(self, limit: int = 20) -> list:
        """List all documents"""
        try:
            docs = self.doc_manager.list_all_documents(limit=limit)
            logger.info(f"Listed {len(docs)} documents")
            return docs
        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            return []
    
    def search(self, query: str) -> list:
        """
        Search documents
        
        Args:
            query: Search query
        
        Returns:
            List of matching documents
        """
        try:
            results = self.search_engine.search(query)
            logger.info(f"Search found {len(results)} results")
            return results
        except Exception as e:
            logger.error(f"Error searching: {e}")
            return []
    
    def get_document(self, doc_id: int) -> dict:
        """Get document by ID"""
        try:
            doc = self.doc_manager.get_document(doc_id)
            return doc if doc else {"error": "Document not found"}
        except Exception as e:
            logger.error(f"Error getting document: {e}")
            return {"error": str(e)}
    
    def analyze_document(self, doc_id: int) -> dict:
        """Analyze document"""
        try:
            doc = self.doc_manager.get_document(doc_id)
            if not doc:
                return {"error": "Document not found"}
            
            result = self.analyzer.analyze_document(doc['content'])
            logger.info(f"Document {doc_id} analyzed")
            return result if result else {"error": "Analysis failed"}
        except Exception as e:
            logger.error(f"Error analyzing: {e}")
            return {"error": str(e)}
    
    def summarize_document(self, doc_id: int) -> dict:
        """Summarize document"""
        try:
            doc = self.doc_manager.get_document(doc_id)
            if not doc:
                return {"error": "Document not found"}
            
            result = self.summarizer.generate_short_summary(doc['content'])
            logger.info(f"Document {doc_id} summarized")
            return {"summary": result} if result else {"error": "Summarization failed"}
        except Exception as e:
            logger.error(f"Error summarizing: {e}")
            return {"error": str(e)}
    
    def ask_question(self, doc_id: int, question: str) -> dict:
        """Ask question about document"""
        try:
            doc = self.doc_manager.get_document(doc_id)
            if not doc:
                return {"error": "Document not found"}
            
            result = self.qa.answer_question(doc['content'], question)
            logger.info(f"Question answered for document {doc_id}")
            return result if result else {"error": "Q&A failed"}
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return {"error": str(e)}
    
    def export_document(self, doc_id: int, format: str = "txt") -> dict:
        """Export document"""
        try:
            doc = self.doc_manager.get_document(doc_id)
            if not doc:
                return {"error": "Document not found"}
            
            filename = f"document_{doc_id}"
            
            if format == "txt":
                path = self.export.export_to_txt(doc['content'], filename)
            elif format == "pdf":
                path = self.export.export_to_pdf(doc['content'], filename, doc['title'])
            elif format == "docx":
                path = self.export.export_to_docx(doc['content'], filename, doc['title'])
            elif format == "md":
                path = self.export.export_to_markdown(doc['content'], filename, doc['title'])
            else:
                return {"error": f"Unknown format: {format}"}
            
            if path:
                logger.info(f"Document {doc_id} exported to {format}")
                return {"success": True, "path": path}
            else:
                return {"error": f"Export to {format} failed"}
        
        except Exception as e:
            logger.error(f"Error exporting: {e}")
            return {"error": str(e)}
    
    def get_stats(self) -> dict:
        """Get application statistics"""
        try:
            stats = self.doc_manager.get_statistics()
            logger.info("Statistics retrieved")
            return stats
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            if self.camera:
                self.camera.stop_camera()
            self.doc_manager.close()
            logger.info("Cleanup complete")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="Portable Offline AI Document Reader - Headless Mode"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Scan command
    scan_parser = subparsers.add_parser("scan", help="Scan document from file")
    scan_parser.add_argument("image_path", help="Path to image file")
    scan_parser.add_argument("--title", default="Document", help="Document title")
    
    # Capture command
    capture_parser = subparsers.add_parser("capture", help="Capture from camera")
    capture_parser.add_argument("--title", default="Document", help="Document title")
    capture_parser.add_argument("--frames", type=int, default=5, help="Number of frames")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List documents")
    list_parser.add_argument("--limit", type=int, default=20, help="Max documents")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search documents")
    search_parser.add_argument("query", help="Search query")
    
    # Get command
    get_parser = subparsers.add_parser("get", help="Get document")
    get_parser.add_argument("doc_id", type=int, help="Document ID")
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze document")
    analyze_parser.add_argument("doc_id", type=int, help="Document ID")
    
    # Summarize command
    summarize_parser = subparsers.add_parser("summarize", help="Summarize document")
    summarize_parser.add_argument("doc_id", type=int, help="Document ID")
    
    # Ask command
    ask_parser = subparsers.add_parser("ask", help="Ask question about document")
    ask_parser.add_argument("doc_id", type=int, help="Document ID")
    ask_parser.add_argument("question", help="Question to ask")
    
    # Export command
    export_parser = subparsers.add_parser("export", help="Export document")
    export_parser.add_argument("doc_id", type=int, help="Document ID")
    export_parser.add_argument("--format", default="txt", help="Export format")
    
    # Stats command
    subparsers.add_parser("stats", help="Get statistics")
    
    args = parser.parse_args()
    
    app = HeadlessApp()
    
    try:
        if args.command == "scan":
            result = app.scan_document(args.image_path, args.title)
            print_result(result)
        
        elif args.command == "capture":
            result = app.capture_from_camera(args.title, args.frames)
            print_result(result)
        
        elif args.command == "list":
            docs = app.list_documents(args.limit)
            print_result({"count": len(docs), "documents": docs})
        
        elif args.command == "search":
            results = app.search(args.query)
            print_result({"count": len(results), "results": results})
        
        elif args.command == "get":
            doc = app.get_document(args.doc_id)
            print_result(doc)
        
        elif args.command == "analyze":
            result = app.analyze_document(args.doc_id)
            print_result(result)
        
        elif args.command == "summarize":
            result = app.summarize_document(args.doc_id)
            print_result(result)
        
        elif args.command == "ask":
            result = app.ask_question(args.doc_id, args.question)
            print_result(result)
        
        elif args.command == "export":
            result = app.export_document(args.doc_id, args.format)
            print_result(result)
        
        elif args.command == "stats":
            stats = app.get_stats()
            print_result(stats)
        
        else:
            parser.print_help()
    
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"Error: {e}")
    
    finally:
        app.cleanup()


def print_result(data):
    """Pretty print result"""
    import json
    print(json.dumps(data, indent=2, default=str))


if __name__ == "__main__":
    logger.info("Starting Headless Application")
    main()
