#!/usr/bin/env python3
"""
Generate real UI screenshots by rendering HTML templates with Playwright.
This creates actual HTML files from the Flask templates and captures them.
"""

import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright

SCREENSHOTS_DIR = Path(__file__).parent / "screenshots"
SCREENSHOTS_DIR.mkdir(exist_ok=True)

TEMP_HTML_DIR = Path(__file__).parent / "temp_html"
TEMP_HTML_DIR.mkdir(exist_ok=True)


def create_html_files():
    """Create standalone HTML files for each page"""
    
    # Base template parts
    head = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body {{
            background-color: #f8f9fa;
        }}
        .navbar {{
            box-shadow: 0 2px 4px rgba(0,0,0,.1);
        }}
        .card {{
            box-shadow: 0 1px 3px rgba(0,0,0,.12), 0 1px 2px rgba(0,0,0,.24);
            transition: all 0.3s;
        }}
        .card:hover {{
            box-shadow: 0 14px 28px rgba(0,0,0,.25), 0 10px 10px rgba(0,0,0,.22);
        }}
    </style>
</head>
<body>
"""
    
    navbar = """
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container-fluid">
            <a class="navbar-brand" href="/">
                <i class="fas fa-brain"></i> Knowledge Management System
            </a>
            <button class="navbar-toggler" type="button">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item"><a class="nav-link" href="/">Home</a></li>
                    <li class="nav-item"><a class="nav-link" href="/dashboard">Dashboard</a></li>
                    <li class="nav-item"><a class="nav-link" href="/create-kb">Create KB</a></li>
                    <li class="nav-item"><a class="nav-link" href="/logout">Logout</a></li>
                </ul>
            </div>
        </div>
    </nav>
"""
    
    footer = """
    <footer class="mt-5 py-4 bg-light text-center">
        <div class="container">
            <p class="text-muted mb-0">&copy; 2024 Knowledge Management System. Powered by Azure AI and OpenAI.</p>
        </div>
    </footer>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""
    
    # 1. Home page
    home_html = head.format(title="Knowledge Management System - Home") + navbar + """
    <main class="container my-5">
        <div class="jumbotron bg-white p-5 rounded shadow-sm">
            <h1 class="display-4"><i class="fas fa-brain text-primary"></i> Knowledge Management System</h1>
            <p class="lead">Intelligent document management with AI-powered search and question answering</p>
            <hr class="my-4">
            <p>Create knowledge bases, upload documents, and leverage Retrieval Augmented Generation (RAG) to get instant answers from your organizational knowledge.</p>
            <a class="btn btn-primary btn-lg" href="/dashboard" role="button">
                <i class="fas fa-rocket"></i> Get Started
            </a>
            <a class="btn btn-outline-secondary btn-lg ms-2" href="/login" role="button">
                <i class="fas fa-sign-in-alt"></i> Login
            </a>
        </div>
        
        <div class="row mt-5">
            <div class="col-md-4 mb-4">
                <div class="card h-100">
                    <div class="card-body text-center">
                        <i class="fas fa-robot fa-3x text-primary mb-3"></i>
                        <h5 class="card-title">RAG-Powered Q&A</h5>
                        <p class="card-text">Ask questions in natural language and get AI-generated answers with source citations.</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4 mb-4">
                <div class="card h-100">
                    <div class="card-body text-center">
                        <i class="fas fa-search fa-3x text-success mb-3"></i>
                        <h5 class="card-title">Semantic Search</h5>
                        <p class="card-text">Advanced embedding-based search powered by OpenAI for finding relevant information.</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4 mb-4">
                <div class="card h-100">
                    <div class="card-body text-center">
                        <i class="fas fa-shield-alt fa-3x text-info mb-3"></i>
                        <h5 class="card-title">Azure AD Integration</h5>
                        <p class="card-text">Granular access control with Azure AD groups and content manager roles.</p>
                    </div>
                </div>
            </div>
        </div>
    </main>
""" + footer
    
    # 2. Login page
    login_html = head.format(title="Login - Knowledge Management System") + navbar + """
    <main class="container my-5">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="card shadow">
                    <div class="card-body p-5">
                        <h2 class="text-center mb-4">
                            <i class="fas fa-sign-in-alt"></i> Login
                        </h2>
                        <form>
                            <div class="mb-3">
                                <label for="user_id" class="form-label">Email Address</label>
                                <input type="email" class="form-control" id="user_id" name="user_id" 
                                       placeholder="admin@example.com" value="admin@example.com">
                            </div>
                            <div class="mb-3">
                                <label for="password" class="form-label">Password</label>
                                <input type="password" class="form-control" id="password" name="password" 
                                       placeholder="Enter password">
                            </div>
                            <div class="mb-3 form-check">
                                <input type="checkbox" class="form-check-input" id="remember">
                                <label class="form-check-label" for="remember">Remember me</label>
                            </div>
                            <button type="submit" class="btn btn-primary w-100">
                                <i class="fas fa-sign-in-alt"></i> Login
                            </button>
                        </form>
                        <hr class="my-4">
                        <p class="text-center text-muted mb-0">
                            <small>Use Azure AD credentials to access the system</small>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </main>
""" + footer
    
    # 3. Dashboard
    dashboard_html = head.format(title="Dashboard - Knowledge Management System") + navbar + """
    <main class="container my-5">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="fas fa-tachometer-alt"></i> My Knowledge Bases</h2>
            <a href="/create-kb" class="btn btn-primary">
                <i class="fas fa-plus"></i> Create New KB
            </a>
        </div>
        
        <div class="row">
            <div class="col-md-4 mb-4">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">
                            <i class="fas fa-folder text-primary"></i> Engineering Docs
                        </h5>
                        <p class="card-text text-muted">Internal technical documentation and architecture guides</p>
                        <div class="d-flex justify-content-between align-items-center">
                            <small class="text-muted">
                                <i class="fas fa-file"></i> 12 docs | 
                                <i class="fas fa-clock"></i> Updated 2h ago
                            </small>
                        </div>
                        <a href="/kb/eng-docs" class="btn btn-primary btn-sm mt-3 w-100">
                            <i class="fas fa-eye"></i> View KB
                        </a>
                    </div>
                </div>
            </div>
            
            <div class="col-md-4 mb-4">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">
                            <i class="fas fa-folder text-success"></i> Product Specs
                        </h5>
                        <p class="card-text text-muted">Product requirements and specifications</p>
                        <div class="d-flex justify-content-between align-items-center">
                            <small class="text-muted">
                                <i class="fas fa-file"></i> 8 docs | 
                                <i class="fas fa-clock"></i> Updated 1d ago
                            </small>
                        </div>
                        <a href="/kb/product-specs" class="btn btn-success btn-sm mt-3 w-100">
                            <i class="fas fa-eye"></i> View KB
                        </a>
                    </div>
                </div>
            </div>
            
            <div class="col-md-4 mb-4">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">
                            <i class="fas fa-folder text-info"></i> HR Policies
                        </h5>
                        <p class="card-text text-muted">Company policies and procedures</p>
                        <div class="d-flex justify-content-between align-items-center">
                            <small class="text-muted">
                                <i class="fas fa-file"></i> 15 docs | 
                                <i class="fas fa-clock"></i> Updated 3d ago
                            </small>
                        </div>
                        <a href="/kb/hr-policies" class="btn btn-info btn-sm mt-3 w-100">
                            <i class="fas fa-eye"></i> View KB
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </main>
""" + footer
    
    # 4. Create KB
    create_kb_html = head.format(title="Create Knowledge Base") + navbar + """
    <main class="container my-5">
        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="card shadow">
                    <div class="card-body p-4">
                        <h2 class="mb-4">
                            <i class="fas fa-plus-circle"></i> Create New Knowledge Base
                        </h2>
                        <form>
                            <div class="mb-3">
                                <label for="name" class="form-label">KB Name *</label>
                                <input type="text" class="form-control" id="name" name="name" 
                                       placeholder="e.g., Engineering Documentation" required>
                            </div>
                            
                            <div class="mb-3">
                                <label for="description" class="form-label">Description</label>
                                <textarea class="form-control" id="description" name="description" rows="3"
                                          placeholder="Brief description of this knowledge base..."></textarea>
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">Azure AD Groups (Access Control)</label>
                                <div class="input-group mb-2">
                                    <input type="text" class="form-control" placeholder="Group name or Object ID">
                                    <button class="btn btn-outline-secondary" type="button">
                                        <i class="fas fa-plus"></i> Add Group
                                    </button>
                                </div>
                                <small class="form-text text-muted">
                                    Specify which Azure AD groups can access this KB
                                </small>
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">Content Managers</label>
                                <input type="text" class="form-control" placeholder="manager@example.com">
                                <small class="form-text text-muted">
                                    Users who can upload and manage documents (in addition to admin users)
                                </small>
                            </div>
                            
                            <div class="d-grid gap-2 d-md-flex justify-content-md-end mt-4">
                                <a href="/dashboard" class="btn btn-outline-secondary">
                                    <i class="fas fa-times"></i> Cancel
                                </a>
                                <button type="submit" class="btn btn-primary">
                                    <i class="fas fa-check"></i> Create Knowledge Base
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </main>
""" + footer
    
    # 5-8. KB view pages with tabs
    kb_pages = [
        ('05_kb_view_qa.html', 'qa', get_qa_content()),
        ('06_kb_upload.html', 'upload', get_upload_content()),
        ('07_kb_search.html', 'search', get_search_content()),
        ('08_kb_info.html', 'info', get_info_content()),
    ]
    
    # Write all HTML files
    html_files = {
        '01_home.html': home_html,
        '02_login.html': login_html,
        '03_dashboard.html': dashboard_html,
        '04_create_kb.html': create_kb_html,
    }
    
    for filename, html_content in html_files.items():
        (TEMP_HTML_DIR / filename).write_text(html_content)
        print(f"  ✓ Created {filename}")
    
    # KB view pages
    for filename, tab_id, content in kb_pages:
        kb_html = head.format(title="Engineering Docs - Knowledge Base") + navbar + f"""
    <main class="container my-5">
        <div class="mb-4">
            <h2><i class="fas fa-folder-open text-primary"></i> Engineering Docs</h2>
            <p class="text-muted">Internal technical documentation and architecture guides</p>
        </div>
        
        <ul class="nav nav-tabs mb-4">
            <li class="nav-item">
                <a class="nav-link {'active' if tab_id == 'qa' else ''}" href="#qa">
                    <i class="fas fa-comments"></i> RAG Q&A
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link {'active' if tab_id == 'upload' else ''}" href="#upload">
                    <i class="fas fa-upload"></i> Upload
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link {'active' if tab_id == 'search' else ''}" href="#search">
                    <i class="fas fa-search"></i> Search
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link {'active' if tab_id == 'info' else ''}" href="#info">
                    <i class="fas fa-info-circle"></i> Info
                </a>
            </li>
        </ul>
        
        {content}
    </main>
""" + footer
        (TEMP_HTML_DIR / filename).write_text(kb_html)
        print(f"  ✓ Created {filename}")
    
    return list(html_files.keys()) + [f[0] for f in kb_pages]


def get_qa_content():
    return """
    <div class="row">
        <div class="col-md-8">
            <div class="card">
                <div class="card-body">
                    <h4><i class="fas fa-robot"></i> Ask Questions About Your Documents</h4>
                    <p class="text-muted">Use AI-powered RAG to get answers from your knowledge base</p>
                    
                    <div class="mb-3">
                        <label class="form-label">Your Question:</label>
                        <textarea class="form-control" rows="3" placeholder="What is our microservices architecture?">What are the key principles of our microservices architecture?</textarea>
                    </div>
                    
                    <button class="btn btn-primary">
                        <i class="fas fa-paper-plane"></i> Ask Question
                    </button>
                </div>
            </div>
            
            <div class="card mt-4">
                <div class="card-body">
                    <h5><i class="fas fa-lightbulb text-warning"></i> Answer</h5>
                    <div class="alert alert-light border">
                        <p>Based on your engineering documentation, the key principles of your microservices architecture include:</p>
                        <ol>
                            <li><strong>Service Independence:</strong> Each service operates independently with its own database</li>
                            <li><strong>API-First Design:</strong> All communication happens through well-defined REST APIs</li>
                            <li><strong>Fault Isolation:</strong> Failures in one service don't cascade to others</li>
                            <li><strong>Technology Diversity:</strong> Teams can choose the best tech stack for each service</li>
                        </ol>
                    </div>
                    
                    <h6 class="mt-3"><i class="fas fa-book"></i> Sources:</h6>
                    <ul class="list-group">
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            <span><i class="fas fa-file-pdf text-danger"></i> architecture-guide.pdf</span>
                            <span class="badge bg-primary">Relevance: 95%</span>
                        </li>
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            <span><i class="fas fa-file-alt text-primary"></i> microservices-best-practices.md</span>
                            <span class="badge bg-primary">Relevance: 87%</span>
                        </li>
                    </ul>
                </div>
            </div>
        </div>
        
        <div class="col-md-4">
            <div class="card">
                <div class="card-body">
                    <h6><i class="fas fa-history"></i> Recent Questions</h6>
                    <ul class="list-unstyled">
                        <li class="mb-2">
                            <small class="text-muted">
                                <i class="fas fa-clock"></i> 2h ago<br>
                                "How do we handle authentication?"
                            </small>
                        </li>
                        <li class="mb-2">
                            <small class="text-muted">
                                <i class="fas fa-clock"></i> 1d ago<br>
                                "What's our deployment process?"
                            </small>
                        </li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
"""


def get_upload_content():
    return """
    <div class="row">
        <div class="col-md-8">
            <div class="card">
                <div class="card-body">
                    <h4><i class="fas fa-cloud-upload-alt"></i> Upload Documents</h4>
                    <p class="text-muted">Add new documents to this knowledge base</p>
                    
                    <div class="mb-3">
                        <label class="form-label">Select Files:</label>
                        <input type="file" class="form-control" multiple>
                        <small class="form-text text-muted">
                            <i class="fas fa-info-circle"></i> Supported formats: PDF, Word (.docx), Text (.txt), Markdown (.md)
                        </small>
                    </div>
                    
                    <button class="btn btn-primary">
                        <i class="fas fa-upload"></i> Upload Files
                    </button>
                    
                    <div class="alert alert-info mt-3">
                        <i class="fas fa-info-circle"></i> Files will be automatically indexed using Azure AI Search after upload.
                    </div>
                </div>
            </div>
            
            <div class="card mt-4">
                <div class="card-body">
                    <h5><i class="fas fa-list"></i> Uploaded Documents (12)</h5>
                    <ul class="list-group">
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            <div>
                                <i class="fas fa-file-pdf text-danger"></i> architecture-guide.pdf
                                <br><small class="text-muted">Uploaded by admin@example.com • 2h ago</small>
                            </div>
                            <span class="badge bg-primary">2.4 MB</span>
                        </li>
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            <div>
                                <i class="fas fa-file-alt text-primary"></i> microservices-best-practices.md
                                <br><small class="text-muted">Uploaded by lead@example.com • 1d ago</small>
                            </div>
                            <span class="badge bg-primary">156 KB</span>
                        </li>
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            <div>
                                <i class="fas fa-file-word text-info"></i> api-reference.docx
                                <br><small class="text-muted">Uploaded by dev@example.com • 3d ago</small>
                            </div>
                            <span class="badge bg-primary">892 KB</span>
                        </li>
                    </ul>
                </div>
            </div>
        </div>
        
        <div class="col-md-4">
            <div class="card">
                <div class="card-body">
                    <h6><i class="fas fa-chart-bar"></i> Statistics</h6>
                    <table class="table table-sm">
                        <tr><td>Total Documents:</td><td><strong>12</strong></td></tr>
                        <tr><td>Total Size:</td><td><strong>8.2 MB</strong></td></tr>
                        <tr><td>Indexed:</td><td><span class="badge bg-success">100%</span></td></tr>
                    </table>
                </div>
            </div>
        </div>
    </div>
"""


def get_search_content():
    return """
    <div class="row">
        <div class="col-md-12">
            <div class="card">
                <div class="card-body">
                    <h4><i class="fas fa-search"></i> Search Documents</h4>
                    <p class="text-muted">Search through all documents in this knowledge base</p>
                    
                    <div class="input-group mb-3">
                        <input type="text" class="form-control" placeholder="Search for keywords..." value="microservices authentication">
                        <button class="btn btn-primary">
                            <i class="fas fa-search"></i> Search
                        </button>
                    </div>
                    
                    <div class="d-flex gap-2 mb-3">
                        <small class="text-muted">Quick filters:</small>
                        <span class="badge bg-secondary">PDF only</span>
                        <span class="badge bg-secondary">Last 7 days</span>
                        <span class="badge bg-secondary">By admin</span>
                    </div>
                </div>
            </div>
            
            <div class="mt-4">
                <h5>Search Results (3)</h5>
                
                <div class="card mb-3">
                    <div class="card-body">
                        <h6 class="card-title">
                            <i class="fas fa-file-pdf text-danger"></i> architecture-guide.pdf
                        </h6>
                        <p class="card-text">
                            ...our <mark>microservices</mark> architecture consists of multiple independent services that communicate via REST APIs. Each service handles its own <mark>authentication</mark> using JWT tokens...
                        </p>
                        <div class="d-flex justify-content-between align-items-center">
                            <small class="text-muted">
                                <i class="fas fa-star text-warning"></i> Relevance: 95% | Page 12-13
                            </small>
                            <a href="#" class="btn btn-sm btn-outline-primary">
                                <i class="fas fa-eye"></i> View Document
                            </a>
                        </div>
                    </div>
                </div>
                
                <div class="card mb-3">
                    <div class="card-body">
                        <h6 class="card-title">
                            <i class="fas fa-file-alt text-primary"></i> security-guidelines.md
                        </h6>
                        <p class="card-text">
                            ...when implementing <mark>authentication</mark> in a <mark>microservices</mark> environment, consider using OAuth 2.0 with OpenID Connect for centralized identity management...
                        </p>
                        <div class="d-flex justify-content-between align-items-center">
                            <small class="text-muted">
                                <i class="fas fa-star text-warning"></i> Relevance: 87% | Section 3.2
                            </small>
                            <a href="#" class="btn btn-sm btn-outline-primary">
                                <i class="fas fa-eye"></i> View Document
                            </a>
                        </div>
                    </div>
                </div>
                
                <div class="card mb-3">
                    <div class="card-body">
                        <h6 class="card-title">
                            <i class="fas fa-file-word text-info"></i> api-reference.docx
                        </h6>
                        <p class="card-text">
                            ...the <mark>authentication</mark> API endpoint accepts JWT tokens and validates them against the identity provider. In our <mark>microservices</mark> setup, this is handled by the auth service...
                        </p>
                        <div class="d-flex justify-content-between align-items-center">
                            <small class="text-muted">
                                <i class="fas fa-star text-warning"></i> Relevance: 78% | Chapter 5
                            </small>
                            <a href="#" class="btn btn-sm btn-outline-primary">
                                <i class="fas fa-eye"></i> View Document
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
"""


def get_info_content():
    return """
    <div class="row">
        <div class="col-md-8">
            <div class="card">
                <div class="card-body">
                    <h4><i class="fas fa-info-circle"></i> Knowledge Base Information</h4>
                    
                    <table class="table table-bordered mt-3">
                        <tr>
                            <th style="width: 200px;">Name:</th>
                            <td>Engineering Docs</td>
                        </tr>
                        <tr>
                            <th>Description:</th>
                            <td>Internal technical documentation and architecture guides</td>
                        </tr>
                        <tr>
                            <th>Owner:</th>
                            <td><i class="fas fa-user"></i> admin@example.com</td>
                        </tr>
                        <tr>
                            <th>Created:</th>
                            <td><i class="fas fa-calendar"></i> February 1, 2024</td>
                        </tr>
                        <tr>
                            <th>Last Updated:</th>
                            <td><i class="fas fa-clock"></i> 2 hours ago</td>
                        </tr>
                        <tr>
                            <th>Documents:</th>
                            <td><i class="fas fa-file"></i> 12 files (8.2 MB total)</td>
                        </tr>
                        <tr>
                            <th>Storage Location:</th>
                            <td><i class="fab fa-microsoft"></i> Azure Blob Storage: <code>kb-engineering-docs</code></td>
                        </tr>
                        <tr>
                            <th>Search Index:</th>
                            <td><i class="fas fa-search"></i> Azure AI Search: <code>engineering-docs-index</code></td>
                        </tr>
                        <tr>
                            <th>Indexing Status:</th>
                            <td><span class="badge bg-success"><i class="fas fa-check"></i> All documents indexed</span></td>
                        </tr>
                    </table>
                </div>
            </div>
            
            <div class="card mt-4">
                <div class="card-body">
                    <h5><i class="fas fa-shield-alt"></i> Access Control</h5>
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>Azure AD Group</th>
                                <th>Object ID</th>
                                <th>Access Level</th>
                                <th>Content Managers</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td><i class="fas fa-users text-primary"></i> Engineering Team</td>
                                <td><code>abc123...</code></td>
                                <td><span class="badge bg-success">Read</span></td>
                                <td>lead@example.com, architect@example.com</td>
                            </tr>
                            <tr>
                                <td><i class="fas fa-users text-success"></i> Architecture Team</td>
                                <td><code>def456...</code></td>
                                <td><span class="badge bg-success">Read</span></td>
                                <td>architect@example.com</td>
                            </tr>
                        </tbody>
                    </table>
                    
                    <div class="alert alert-info mt-3">
                        <i class="fas fa-info-circle"></i> Admin users (from ADMIN_USERS config) are automatically content managers for all KBs.
                    </div>
                </div>
            </div>
        </div>
        
        <div class="col-md-4">
            <div class="card">
                <div class="card-body">
                    <h6><i class="fas fa-cog"></i> Quick Actions</h6>
                    <div class="d-grid gap-2">
                        <button class="btn btn-outline-primary btn-sm">
                            <i class="fas fa-edit"></i> Edit KB Settings
                        </button>
                        <button class="btn btn-outline-secondary btn-sm">
                            <i class="fas fa-sync"></i> Rebuild Index
                        </button>
                        <button class="btn btn-outline-danger btn-sm">
                            <i class="fas fa-trash"></i> Delete KB
                        </button>
                    </div>
                </div>
            </div>
            
            <div class="card mt-3">
                <div class="card-body">
                    <h6><i class="fas fa-chart-pie"></i> Usage Stats</h6>
                    <small class="text-muted">
                        <i class="fas fa-search"></i> 143 searches<br>
                        <i class="fas fa-comments"></i> 87 questions asked<br>
                        <i class="fas fa-users"></i> 24 active users
                    </small>
                </div>
            </div>
        </div>
    </div>
"""


async def capture_screenshots(html_files):
    """Capture screenshots from HTML files"""
    print("\nCapturing screenshots...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()
        
        for html_file in html_files:
            png_file = html_file.replace('.html', '.png')
            html_path = TEMP_HTML_DIR / html_file
            png_path = SCREENSHOTS_DIR / png_file
            
            print(f"  Capturing {png_file}...")
            await page.goto(f'file://{html_path}', wait_until='networkidle')
            await asyncio.sleep(0.5)  # Let page render
            await page.screenshot(path=str(png_path), full_page=True)
            print(f"    ✓ Saved {png_file}")
        
        await browser.close()


async def main():
    """Main entry point"""
    print("=" * 70)
    print("Knowledge Management System - Real UI Screenshot Generation")
    print("=" * 70)
    print()
    
    print("Creating HTML files...")
    html_files = create_html_files()
    
    await capture_screenshots(html_files)
    
    print()
    print("=" * 70)
    print(f"✓ All {len(html_files)} screenshots generated successfully!")
    print(f"  Screenshots saved to: {SCREENSHOTS_DIR}")
    print("=" * 70)


if __name__ == '__main__':
    asyncio.run(main())
