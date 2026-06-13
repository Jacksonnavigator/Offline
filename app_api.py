"""
REST API Server for Portable Offline AI Document Reader
Provides web interface for headless Raspberry Pi deployment
"""

from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
from pathlib import Path
import json
import logging
from functools import wraps
from app_headless import HeadlessApp
from utils.logger import get_logger
from speech.tts_engine import speak_text

logger = get_logger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max
app.config['UPLOAD_FOLDER'] = './uploads'
Path(app.config['UPLOAD_FOLDER']).mkdir(exist_ok=True)

# Initialize headless app
headless_app = HeadlessApp()

# Simple API key authentication
API_KEY = "your-api-key-change-me"


def require_api_key(f):
    """Decorator to require API key"""
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get('X-API-Key')
        if not key or key != API_KEY:
            return jsonify({"error": "Invalid or missing API key"}), 401
        return f(*args, **kwargs)
    return decorated


# ============= Health & Info =============

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "version": "1.0.0",
        "service": "Portable Offline AI Document Reader"
    })


@app.route('/api/stats', methods=['GET'])
@require_api_key
def stats():
    """Get application statistics"""
    try:
        stats = headless_app.get_stats()
        return jsonify({"success": True, "data": stats})
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({"error": str(e)}), 500


# ============= Document Operations =============

@app.route('/api/documents', methods=['GET'])
@require_api_key
def list_documents():
    """List all documents"""
    try:
        limit = request.args.get('limit', 20, type=int)
        docs = headless_app.list_documents(limit=limit)
        return jsonify({
            "success": True,
            "count": len(docs),
            "documents": docs
        })
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/documents/<int:doc_id>', methods=['GET'])
@require_api_key
def get_document(doc_id):
    """Get specific document"""
    try:
        doc = headless_app.get_document(doc_id)
        if "error" in doc:
            return jsonify(doc), 404
        return jsonify({"success": True, "document": doc})
    except Exception as e:
        logger.error(f"Error getting document: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/documents/<int:doc_id>', methods=['DELETE'])
@require_api_key
def delete_document(doc_id):
    """Delete document"""
    try:
        headless_app.doc_manager.delete_document(doc_id)
        return jsonify({"success": True, "message": f"Document {doc_id} deleted"})
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        return jsonify({"error": str(e)}), 500


# ============= Scanning & OCR =============

@app.route('/api/scan', methods=['POST'])
@require_api_key
def scan_document():
    """Scan document from uploaded image"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        filename = secure_filename(file.filename)
        filepath = Path(app.config['UPLOAD_FOLDER']) / filename
        file.save(str(filepath))
        
        title = request.form.get('title', 'Document')
        result = headless_app.scan_document(str(filepath), title)
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error scanning: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/capture', methods=['POST'])
@require_api_key
def capture_from_camera():
    """Capture from camera"""
    try:
        title = request.json.get('title', 'Document') if request.json else 'Document'
        frames = request.json.get('frames', 5) if request.json else 5
        
        result = headless_app.capture_from_camera(title, frames)
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error capturing: {e}")
        return jsonify({"error": str(e)}), 500


# ============= Search =============

@app.route('/api/search', methods=['GET'])
@require_api_key
def search_documents():
    """Search documents"""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({"error": "No query provided"}), 400
        
        results = headless_app.search(query)
        return jsonify({
            "success": True,
            "query": query,
            "count": len(results),
            "results": results
        })
    
    except Exception as e:
        logger.error(f"Error searching: {e}")
        return jsonify({"error": str(e)}), 500


# ============= AI Operations =============

@app.route('/api/documents/<int:doc_id>/analyze', methods=['POST'])
@require_api_key
def analyze_document(doc_id):
    """Analyze document"""
    try:
        result = headless_app.analyze_document(doc_id)
        if "error" in result:
            return jsonify(result), 400
        return jsonify({"success": True, "analysis": result})
    except Exception as e:
        logger.error(f"Error analyzing: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/documents/<int:doc_id>/summarize', methods=['POST'])
@require_api_key
def summarize_document(doc_id):
    """Summarize document"""
    try:
        result = headless_app.summarize_document(doc_id)
        if "error" in result:
            return jsonify(result), 400
        return jsonify({"success": True, "summary": result.get('summary')})
    except Exception as e:
        logger.error(f"Error summarizing: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/documents/<int:doc_id>/ask', methods=['POST'])
@require_api_key
def ask_question(doc_id):
    """Ask question about document"""
    try:
        if not request.json or 'question' not in request.json:
            return jsonify({"error": "No question provided"}), 400
        
        question = request.json['question']
        result = headless_app.ask_question(doc_id, question)
        
        if "error" in result:
            return jsonify(result), 400
        return jsonify({"success": True, "answer": result})
    
    except Exception as e:
        logger.error(f"Error answering question: {e}")
        return jsonify({"error": str(e)}), 500



@app.route('/api/documents/<int:doc_id>/read', methods=['POST'])
@require_api_key
def read_document(doc_id):
    """Read a document aloud using the configured TTS engine"""
    try:
        doc = headless_app.get_document(doc_id)
        if not doc or 'error' in doc:
            return jsonify({"error": "Document not found"}), 404

        text = doc.get('content', '') or ''
        if not text.strip():
            return jsonify({"error": "Document has no text to read"}), 400

        # Use headless_app config for voice/rate
        cfg = getattr(headless_app, 'config', {})
        voice = cfg.get('speech', {}).get('voice') if isinstance(cfg, dict) else None
        rate = float(cfg.get('speech', {}).get('rate', 1.0)) if isinstance(cfg, dict) else 1.0

        played = speak_text(text, voice=voice, rate=rate)
        if played:
            return jsonify({"success": True, "message": "Playback started"})
        else:
            return jsonify({"error": "Playback failed"}), 500

    except Exception as e:
        logger.error(f"Error reading document: {e}")
        return jsonify({"error": str(e)}), 500


# ============= Export =============

@app.route('/api/documents/<int:doc_id>/export', methods=['GET'])
@require_api_key
def export_document(doc_id):
    """Export document"""
    try:
        format = request.args.get('format', 'txt')
        result = headless_app.export_document(doc_id, format)
        
        if "error" in result:
            return jsonify(result), 400
        
        filepath = result.get('path')
        if filepath and Path(filepath).exists():
            return send_file(
                filepath,
                as_attachment=True,
                download_name=f"document_{doc_id}.{format}"
            )
        
        return jsonify({"error": "Export failed"}), 500
    
    except Exception as e:
        logger.error(f"Error exporting: {e}")
        return jsonify({"error": str(e)}), 500


# ============= Web Interface =============

@app.route('/', methods=['GET'])
def index():
    """Serve web dashboard"""
    return serve_web_interface()


@app.route('/dashboard', methods=['GET'])
def dashboard():
    """Serve web dashboard"""
    return serve_web_interface()


def serve_web_interface():
    """Serve simple web interface"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Document Reader</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #1e1e1e; color: #e0e0e0; }
            header { background: #2d2d2d; padding: 20px; text-align: center; border-bottom: 2px solid #0078d4; }
            nav { background: #252525; padding: 15px; display: flex; gap: 10px; overflow-x: auto; }
            nav button { padding: 10px 20px; background: #0078d4; color: white; border: none; cursor: pointer; border-radius: 4px; }
            nav button:hover { background: #106ebe; }
            .container { max-width: 1200px; margin: 20px auto; padding: 0 20px; }
            .section { background: #2d2d2d; padding: 20px; margin: 20px 0; border-radius: 8px; }
            input, textarea { width: 100%; padding: 10px; margin: 10px 0; background: #3d3d3d; border: 1px solid #555; color: #e0e0e0; border-radius: 4px; }
            button { padding: 10px 20px; background: #0078d4; color: white; border: none; cursor: pointer; border-radius: 4px; }
            button:hover { background: #106ebe; }
            .result { background: #3d3d3d; padding: 15px; margin: 10px 0; border-radius: 4px; border-left: 3px solid #0078d4; }
            .error { border-left-color: #d13438; }
            h2 { margin: 20px 0 10px 0; color: #0078d4; }
            .doc-list { display: grid; gap: 10px; }
            .doc-item { background: #3d3d3d; padding: 15px; border-radius: 4px; border-left: 3px solid #0078d4; }
            .doc-item h3 { margin-bottom: 5px; }
            .doc-item p { font-size: 0.9em; color: #aaa; }
        </style>
    </head>
    <body>
        <header>
            <h1>🤖 Portable Offline AI Document Reader</h1>
            <p>Raspberry Pi Edition - Headless Interface</p>
        </header>
        
        <nav>
            <button onclick="showSection('home')">📊 Dashboard</button>
            <button onclick="showSection('scan')">📷 Scan</button>
            <button onclick="showSection('documents')">📄 Documents</button>
            <button onclick="showSection('search')">🔍 Search</button>
            <button onclick="showSection('ai')">🤖 AI</button>
        </nav>
        
        <div class="container">
            <!-- Dashboard -->
            <div id="home" class="section">
                <h2>Dashboard</h2>
                <div id="stats">Loading...</div>
                <button onclick="loadStats()">Refresh Stats</button>
            </div>
            
            <!-- Scan -->
            <div id="scan" class="section" style="display:none;">
                <h2>Scan Document</h2>
                <input type="file" id="scanFile" accept="image/*">
                <input type="text" id="scanTitle" placeholder="Document title" value="Document">
                <button onclick="scanDocument()">Scan Image</button>
                <div id="scanResult"></div>
            </div>
            
            <!-- Documents -->
            <div id="documents" class="section" style="display:none;">
                <h2>Documents</h2>
                <button onclick="loadDocuments()">Load Documents</button>
                <div id="docList" class="doc-list"></div>
            </div>
            
            <!-- Search -->
            <div id="search" class="section" style="display:none;">
                <h2>Search</h2>
                <input type="text" id="searchQuery" placeholder="Enter search query">
                <button onclick="searchDocuments()">Search</button>
                <div id="searchResult"></div>
            </div>
            
            <!-- AI -->
            <div id="ai" class="section" style="display:none;">
                <h2>AI Assistant</h2>
                <input type="number" id="aiDocId" placeholder="Document ID">
                <textarea id="aiQuestion" placeholder="Ask a question..." rows="4"></textarea>
                <button onclick="askQuestion()">Ask</button>
                <div id="aiResult"></div>
            </div>
        </div>
        
        <script>
            const API_KEY = "your-api-key-change-me";
            
            function showSection(id) {
                document.querySelectorAll('.section').forEach(s => s.style.display = 'none');
                document.getElementById(id).style.display = 'block';
            }
            
            async function apiCall(endpoint, method='GET', data=null) {
                const options = {
                    method,
                    headers: {'X-API-Key': API_KEY, 'Content-Type': 'application/json'}
                };
                if (data) options.body = JSON.stringify(data);
                
                const response = await fetch(`/api${endpoint}`, options);
                return response.json();
            }
            
            async function loadStats() {
                const result = await apiCall('/stats');
                document.getElementById('stats').innerHTML = `<pre>${JSON.stringify(result, null, 2)}</pre>`;
            }
            
            async function scanDocument() {
                const file = document.getElementById('scanFile').files[0];
                if (!file) return alert('Select a file');
                
                const formData = new FormData();
                formData.append('file', file);
                formData.append('title', document.getElementById('scanTitle').value);
                
                const response = await fetch('/api/scan', {
                    method: 'POST',
                    headers: {'X-API-Key': API_KEY},
                    body: formData
                });
                const result = await response.json();
                document.getElementById('scanResult').innerHTML = `<div class="result"><pre>${JSON.stringify(result, null, 2)}</pre></div>`;
            }
            
            async function loadDocuments() {
                const result = await apiCall('/documents');
                const html = result.documents.map(doc => `
                    <div class="doc-item">
                            <h3>${doc.title}</h3>
                            <p>ID: ${doc.id} | Language: ${doc.language}</p>
                            <p>${doc.content.substring(0, 100)}...</p>
                            <button onclick="readDocument(${doc.id})">🔊 Read</button>
                    </div>
                `).join('');
                document.getElementById('docList').innerHTML = html || 'No documents found';
            }
            
            async function searchDocuments() {
                const query = document.getElementById('searchQuery').value;
                const result = await apiCall(`/search?q=${encodeURIComponent(query)}`);
                document.getElementById('searchResult').innerHTML = `<div class="result"><pre>${JSON.stringify(result, null, 2)}</pre></div>`;
            }
            
            async function askQuestion() {
                const docId = document.getElementById('aiDocId').value;
                const question = document.getElementById('aiQuestion').value;
                const result = await apiCall(`/documents/${docId}/ask`, 'POST', {question});
                document.getElementById('aiResult').innerHTML = `<div class="result"><pre>${JSON.stringify(result, null, 2)}</pre></div>`;
            }

            async function readDocument(docId) {
                const response = await fetch(`/api/documents/${docId}/read`, {
                    method: 'POST',
                    headers: {'X-API-Key': API_KEY}
                });
                const result = await response.json();
                alert(JSON.stringify(result, null, 2));
            }
            
            // Load stats on page load
            loadStats();
        </script>
    </body>
    </html>
    """
    return html, 200, {'Content-Type': 'text/html'}


# ============= Error Handlers =============

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal error: {error}")
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    logger.info("Starting REST API Server")
    app.run(host='0.0.0.0', port=5000, debug=False)
