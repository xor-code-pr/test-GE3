#!/usr/bin/env python3
"""
Generate screenshot mockups for the Knowledge Management System UI.
Creates visual representations of the 8 UI screens documented.
"""

from PIL import Image, ImageDraw, ImageFont
import os


def create_screenshot(filename, title, content_lines, width=1920, height=1080):
    """Create a mockup screenshot with title and content."""
    # Create image with white background
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a default font, fall back to default if not available
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        header_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
        text_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
    except:
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
    
    # Draw header bar (Bootstrap primary color)
    draw.rectangle([0, 0, width, 100], fill='#0d6efd')
    
    # Draw title in header
    draw.text((50, 30), title, fill='white', font=title_font)
    
    # Draw content
    y_position = 150
    for line in content_lines:
        if line.startswith('## '):
            # Section header
            draw.text((50, y_position), line[3:], fill='#212529', font=header_font)
            y_position += 60
        elif line.startswith('- '):
            # Bullet point
            draw.text((80, y_position), '• ' + line[2:], fill='#495057', font=text_font)
            y_position += 40
        elif line.strip() == '':
            y_position += 20
        else:
            # Regular text
            draw.text((50, y_position), line, fill='#212529', font=text_font)
            y_position += 40
    
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
        'Knowledge Management System - Home',
        [
            '## Welcome to Knowledge Management System',
            '',
            'RAG-Powered Knowledge Base with Azure Integration',
            '',
            '## Features',
            '- Create Knowledge Bases with granular access control',
            '- AI-Powered Q&A using GPT-4 and semantic search',
            '- Secure & Scalable Azure infrastructure',
            '- Automatic document indexing',
            '- Content manager roles and permissions',
            '',
            '[Get Started]   [Learn More]'
        ]
    )
    
    # 2. Login Page
    create_screenshot(
        '02_login.png',
        'Knowledge Management System - Login',
        [
            '## Login',
            '',
            'User ID: [________________]',
            '',
            'Email:   [________________]',
            '',
            '[Login Button]',
            '',
            'Demo Mode: Enter any user ID and email to login.',
            'In production, this uses Azure AD authentication.'
        ]
    )
    
    # 3. Dashboard
    create_screenshot(
        '03_dashboard.png',
        'Knowledge Management System - Dashboard',
        [
            '## Dashboard',
            'Welcome, testuser!  [Admin Badge]',
            '',
            '[+ Create New Knowledge Base]',
            '',
            '## Your Knowledge Bases',
            '',
            '┌─────────────────────────────────────┐',
            '│ Engineering Documentation           │',
            '│ Documentation for engineering team  │',
            '│ Owner: admin@example.com            │',
            '│ Created: 2024-02-04                 │',
            '│ [View]                              │',
            '└─────────────────────────────────────┘'
        ]
    )
    
    # 4. Create KB
    create_screenshot(
        '04_create_kb.png',
        'Knowledge Management System - Create KB',
        [
            '## Create New Knowledge Base',
            '',
            'Knowledge Base Name:',
            '[_________________________________]',
            '',
            'Description:',
            '[_________________________________]',
            '[_________________________________]',
            '[_________________________________]',
            '',
            'Access Control:',
            'As the owner, you have full access.',
            'Configure additional access policies after creation.',
            '',
            '[Create Knowledge Base]  [Cancel]'
        ]
    )
    
    # 5. KB View - RAG Q&A
    create_screenshot(
        '05_kb_view_qa.png',
        'KB: Engineering Docs - Ask Question (RAG)',
        [
            '## Ask a Question',
            'Get AI-powered answers based on documents in this knowledge base.',
            '',
            'Question:',
            '[_________________________________________________]',
            '[_________________________________________________]',
            '',
            '[Ask]',
            '',
            '## Answer:',
            'Based on the documentation, the microservices architecture',
            'uses Docker containers orchestrated by Kubernetes...',
            '',
            '## Sources:',
            '• Source 1: architecture-overview.pdf (Chunk 3)',
            '• Source 2: deployment-guide.md (Chunk 7)',
            '',
            'Confidence: 0.95'
        ]
    )
    
    # 6. KB View - Upload
    create_screenshot(
        '06_kb_upload.png',
        'KB: Engineering Docs - Upload Documents',
        [
            '## Upload Documents',
            'Upload documents to this knowledge base.',
            'They will be automatically indexed.',
            '',
            'Select Files:',
            '[Choose Files]  [Upload]',
            '',
            'Supported formats: PDF, DOCX, TXT, MD, PPTX, XLSX',
            '',
            'Progress:',
            '[████████████████████░░░░░░░] 75%',
            '',
            '✓ Successfully uploaded: architecture.pdf',
            '✓ Successfully uploaded: deployment-guide.md',
            '⏳ Uploading: api-documentation.docx...'
        ]
    )
    
    # 7. KB View - Search
    create_screenshot(
        '07_kb_search.png',
        'KB: Engineering Docs - Search',
        [
            '## Search Documents',
            '',
            'Search Query: [microservices________] [Search]',
            '',
            '## Search Results:',
            '',
            '┌─────────────────────────────────────┐',
            '│ architecture-overview.pdf           │',
            '│ Score: 0.95                         │',
            '│ Document ID: doc-12345              │',
            '└─────────────────────────────────────┘',
            '',
            '┌─────────────────────────────────────┐',
            '│ deployment-guide.md                 │',
            '│ Score: 0.87                         │',
            '│ Document ID: doc-12346              │',
            '└─────────────────────────────────────┘'
        ]
    )
    
    # 8. KB View - Information
    create_screenshot(
        '08_kb_info.png',
        'KB: Engineering Docs - Information',
        [
            '## Knowledge Base Information',
            '',
            'KB ID:              kb-f3d8a9b2c1e0',
            'Name:               Engineering Documentation',
            'Description:        Documentation for engineering team',
            'Owner:              admin@example.com',
            'Blob Container:     kb-f3d8a9b2c1e0',
            'Search Index:       kb-index-f3d8a9b2c1e0',
            'Created:            2024-02-04 10:30:00',
            'Last Updated:       2024-02-04 15:45:00',
            '',
            '## Access Policies:',
            '- Engineering Team (Read access)',
            '  Content Managers: lead@example.com'
        ]
    )
    
    print("\n" + "=" * 80)
    print("Screenshot mockups generated successfully!")
    print("Location: ./screenshots/")
    print("=" * 80)


if __name__ == '__main__':
    main()
