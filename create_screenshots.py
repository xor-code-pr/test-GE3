#!/usr/bin/env python3
"""
Generate screenshot mockups for the Knowledge Management System UI.
Creates visual representations of the 8 UI screens documented.
"""

from PIL import Image, ImageDraw, ImageFont
import os


def create_screenshot(filename, title, content_lines, width=1920, height=1080):
    """Create a mockup screenshot with title and content."""
    # Create image with light gray background
    img = Image.new('RGB', (width, height), color='#f5f5f5')
    draw = ImageDraw.Draw(img)
    
    # Try to use a default font, fall back to default if not available
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        header_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
        text_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    except:
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Draw header bar (Bootstrap primary color)
    draw.rectangle([0, 0, width, 100], fill='#0d6efd')
    
    # Draw navigation items
    nav_items = ['Dashboard', 'Knowledge Bases', 'Search', 'Profile']
    nav_x = width - 600
    for item in nav_items:
        draw.text((nav_x, 35), item, fill='white', font=small_font)
        nav_x += 140
    
    # Draw title in header
    draw.text((50, 30), title, fill='white', font=title_font)
    
    # Draw main content area with white background
    draw.rectangle([40, 130, width-40, height-40], fill='white', outline='#dee2e6', width=2)
    
    # Draw content
    y_position = 170
    for line in content_lines:
        if line.startswith('## '):
            # Section header
            draw.rectangle([60, y_position-5, width-60, y_position+45], fill='#e9ecef')
            draw.text((80, y_position), line[3:], fill='#212529', font=header_font)
            y_position += 70
        elif line.startswith('- '):
            # Bullet point
            draw.ellipse([100, y_position+5, 115, y_position+20], fill='#0d6efd')
            draw.text((130, y_position), line[2:], fill='#495057', font=text_font)
            y_position += 45
        elif line.startswith('[') and line.endswith(']'):
            # Button
            btn_text = line[1:-1]
            btn_width = len(btn_text) * 15 + 40
            draw.rectangle([80, y_position, 80+btn_width, y_position+45], fill='#0d6efd', outline='#0a58ca', width=2)
            draw.text((100, y_position+10), btn_text, fill='white', font=text_font)
            y_position += 65
        elif line.startswith('Input:') or line.startswith('Question:') or line.startswith('Search:'):
            # Input field
            draw.text((80, y_position), line, fill='#212529', font=text_font)
            y_position += 35
            draw.rectangle([80, y_position, width-100, y_position+50], fill='white', outline='#ced4da', width=2)
            y_position += 70
        elif line.strip() == '':
            y_position += 20
        elif line.startswith('Card:'):
            # Card component
            draw.rectangle([80, y_position, width-100, y_position+150], fill='#ffffff', outline='#dee2e6', width=2)
            draw.rectangle([80, y_position, width-100, y_position+50], fill='#0d6efd')
            draw.text((100, y_position+10), line[6:], fill='white', font=header_font)
            y_position += 170
        else:
            # Regular text
            draw.text((80, y_position), line, fill='#495057', font=text_font)
            y_position += 40
    
    # Draw footer
    draw.rectangle([0, height-50, width, height], fill='#343a40')
    draw.text((50, height-35), '© 2024 Knowledge Management System | Powered by Azure & OpenAI', fill='#adb5bd', font=small_font)
    
    # Save image
    filepath = os.path.join('screenshots', filename)
    img.save(filepath, 'PNG')
    print(f"✓ Created: {filepath}")


def main():
    """Generate all UI screenshots."""
    print("=" * 80)
    print("Generating UI Screenshot Mockups")
    print("=" * 80)
    
    # 1. Home Page
    create_screenshot(
        '01_home.png',
        'Knowledge Management System',
        [
            '## Welcome to AI-Powered Knowledge Management',
            '',
            'Leverage RAG technology for intelligent document search and Q&A',
            '',
            '## Key Features',
            '- Create and manage knowledge bases with granular access control',
            '- AI-powered semantic search using OpenAI embeddings',
            '- GPT-4 powered question answering with source citations',
            '- Secure Azure infrastructure with managed identity',
            '- Automatic document indexing and chunking',
            '',
            '[Get Started]',
            '[View Documentation]'
        ]
    )
    
    # 2. Login Page
    create_screenshot(
        '02_login.png',
        'Login - Knowledge Management System',
        [
            '## Login to Your Account',
            '',
            'Input: User ID',
            '',
            'Input: Email Address',
            '',
            '[Login]',
            '',
            'This system uses Azure AD authentication in production.',
            'Demo mode allows login with any user ID and email.'
        ]
    )
    
    # 3. Dashboard
    create_screenshot(
        '03_dashboard.png',
        'Dashboard - Knowledge Management System',
        [
            '## Your Knowledge Bases',
            '',
            '[+ Create New Knowledge Base]',
            '',
            'Card: Engineering Documentation',
            'Card: Product Specifications',
            'Card: Training Materials',
            '',
            '## Recent Activity',
            '- Document uploaded to Engineering Documentation (2 hours ago)',
            '- New KB created: Training Materials (Yesterday)',
            '- 15 questions answered today'
        ]
    )
    
    # 4. Create KB
    create_screenshot(
        '04_create_kb.png',
        'Create Knowledge Base',
        [
            '## Create New Knowledge Base',
            '',
            'Input: Knowledge Base Name',
            '',
            'Input: Description (Optional)',
            '',
            '## Access Control',
            'Configure Azure AD groups and content managers',
            '',
            '[Create Knowledge Base]',
            '[Cancel]'
        ]
    )
    
    # 5. KB View - RAG Q&A
    create_screenshot(
        '05_kb_view_qa.png',
        'Engineering Docs - Ask Question (RAG)',
        [
            '## Ask a Question',
            'Get AI-powered answers based on your documents',
            '',
            'Question: What is our microservices architecture?',
            '',
            '[Ask Question]',
            '',
            '## Answer (Generated by GPT-4)',
            'Based on the documentation, the microservices architecture',
            'uses Docker containers orchestrated by Kubernetes. Each',
            'service is independently deployable and scalable...',
            '',
            '## Sources',
            '- architecture-overview.pdf (Confidence: 0.95)',
            '- deployment-guide.md (Confidence: 0.87)'
        ]
    )
    
    # 6. KB View - Upload
    create_screenshot(
        '06_kb_upload.png',
        'Engineering Docs - Upload Documents',
        [
            '## Upload Documents',
            'Documents are automatically indexed for RAG',
            '',
            '[Choose Files]',
            '[Upload Selected Files]',
            '',
            'Supported: PDF, DOCX, TXT, MD, PPTX, XLSX',
            '',
            '## Recent Uploads',
            '- architecture.pdf (2.4 MB) - Uploaded successfully',
            '- api-docs.md (124 KB) - Uploaded successfully',
            '- deployment-guide.docx (1.8 MB) - Processing...'
        ]
    )
    
    # 7. KB View - Search
    create_screenshot(
        '07_kb_search.png',
        'Engineering Docs - Search',
        [
            '## Search Documents',
            '',
            'Search: microservices deployment',
            '',
            '## Search Results',
            '',
            'Card: architecture-overview.pdf',
            'Card: deployment-guide.md',
            'Card: kubernetes-setup.docx',
            '',
            'Found 3 documents matching your query'
        ]
    )
    
    # 8. KB View - Information
    create_screenshot(
        '08_kb_info.png',
        'Engineering Docs - Information',
        [
            '## Knowledge Base Information',
            '',
            'KB ID: kb-f3d8a9b2c1e0',
            'Name: Engineering Documentation',
            'Owner: admin@example.com',
            'Created: 2024-02-04',
            '',
            '## Storage Details',
            'Blob Container: kb-f3d8a9b2c1e0',
            'Search Index: kb-index-f3d8a9b2c1e0',
            'Total Documents: 24',
            'Total Size: 45.8 MB',
            '',
            '## Access Policies',
            '- Engineering Team (Read)',
            '  Content Managers: lead@example.com'
        ]
    )
    
    print("\n" + "=" * 80)
    print("Screenshot mockups generated successfully!")
    print("Location: ./screenshots/")
    print("=" * 80)


if __name__ == '__main__':
    main()
