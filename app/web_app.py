"""
Web application for Knowledge Management System with RAG.
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
import logging
from functools import wraps

from .main import KnowledgeManagementApp
from .config import load_config_from_env
from .rag_service import RAGService, Chunk

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize KM app
try:
    km_app = KnowledgeManagementApp()
    rag_service = None
    
    # Initialize RAG service if OpenAI is configured
    if km_app.config.openai:
        rag_service = RAGService(km_app.config.openai)
        logger.info("RAG service initialized")
except Exception as e:
    logger.error(f"Error initializing application: {e}")
    km_app = None
    rag_service = None


# Simple authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    """Home page."""
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page."""
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        email = request.form.get('email')
        
        if user_id and email:
            # Simple login - in production, use proper authentication
            session['user_id'] = user_id
            session['email'] = email
            session['is_admin'] = user_id in km_app.config.admin_users
            
            flash(f'Welcome, {user_id}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Please provide user ID and email.', 'danger')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Logout."""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard page."""
    user_id = session['user_id']
    
    # Get accessible knowledge bases
    kbs = km_app.list_knowledge_bases(user_id)
    
    return render_template('dashboard.html', 
                         knowledge_bases=kbs,
                         is_admin=session.get('is_admin', False))


@app.route('/kb/create', methods=['GET', 'POST'])
@login_required
def create_kb():
    """Create knowledge base page."""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        if name and description:
            try:
                kb = km_app.create_knowledge_base(
                    name=name,
                    description=description,
                    owner_id=session['user_id']
                )
                flash(f'Knowledge base "{name}" created successfully!', 'success')
                return redirect(url_for('view_kb', kb_id=kb.kb_id))
            except Exception as e:
                flash(f'Error creating knowledge base: {str(e)}', 'danger')
        else:
            flash('Please provide name and description.', 'danger')
    
    return render_template('create_kb.html')


@app.route('/kb/<kb_id>')
@login_required
def view_kb(kb_id):
    """View knowledge base page."""
    kb = km_app.kb_manager.get_knowledge_base(kb_id)
    
    if not kb:
        flash('Knowledge base not found.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Check access
    accessible_kbs = km_app.list_knowledge_bases(session['user_id'])
    if kb not in accessible_kbs:
        flash('You do not have access to this knowledge base.', 'danger')
        return redirect(url_for('dashboard'))
    
    is_content_manager = km_app.kb_manager.is_content_manager(kb_id, session['user_id'])
    
    return render_template('view_kb.html', 
                         kb=kb, 
                         is_content_manager=is_content_manager,
                         rag_enabled=rag_service is not None)


@app.route('/kb/<kb_id>/upload', methods=['POST'])
@login_required
def upload_document(kb_id):
    """Upload document to knowledge base."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        file_data = file.read()
        content_type = file.content_type or 'application/octet-stream'
        
        try:
            doc = km_app.upload_document(
                kb_id=kb_id,
                filename=filename,
                file_data=file_data,
                content_type=content_type,
                uploaded_by=session['user_id']
            )
            
            return jsonify({
                'message': 'File uploaded successfully',
                'document_id': doc.document_id,
                'filename': doc.filename
            }), 200
        except Exception as e:
            logger.error(f"Error uploading document: {e}")
            return jsonify({'error': str(e)}), 500


@app.route('/kb/<kb_id>/ask', methods=['POST'])
@login_required
def ask_question(kb_id):
    """Ask a question using RAG."""
    if not rag_service:
        return jsonify({'error': 'RAG service not available. Please configure OpenAI API key.'}), 503
    
    data = request.get_json()
    question = data.get('question')
    
    if not question:
        return jsonify({'error': 'No question provided'}), 400
    
    try:
        # In a real implementation, retrieve document chunks from the KB
        # For now, we'll return a placeholder response
        
        # Placeholder: Create mock chunks (in production, get from storage)
        chunks = []  # Would fetch from KB storage
        
        if not chunks:
            return jsonify({
                'answer': 'No documents found in this knowledge base. Please upload documents first.',
                'sources': [],
                'confidence': 0.0
            }), 200
        
        # Process query with RAG
        response = rag_service.process_query(question, chunks, top_k=km_app.config.top_k_results)
        
        return jsonify({
            'answer': response.answer,
            'sources': response.sources,
            'confidence': response.confidence
        }), 200
    except Exception as e:
        logger.error(f"Error processing question: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/kb/<kb_id>/search', methods=['POST'])
@login_required
def search_kb(kb_id):
    """Search knowledge base."""
    data = request.get_json()
    query = data.get('query')
    
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    try:
        results = km_app.search(kb_id, query, session['user_id'])
        
        return jsonify({
            'results': [
                {
                    'document_id': r.document_id,
                    'filename': r.filename,
                    'score': r.score,
                    'highlights': r.highlights
                }
                for r in results
            ]
        }), 200
    except Exception as e:
        logger.error(f"Error searching: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'app_initialized': km_app is not None,
        'rag_enabled': rag_service is not None
    }), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
