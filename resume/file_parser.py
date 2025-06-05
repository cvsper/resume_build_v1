"""
File parsing utilities for resume uploads
Supports PDF, DOC, and DOCX files
"""

import os
import tempfile
import fitz  # PyMuPDF
from PyPDF2 import PdfReader
from docx import Document
import logging
import re

def extract_text_from_pdf(file_path):
    """Extract text from PDF using PyMuPDF (more reliable)"""
    try:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text.strip()
    except Exception as e:
        logging.error(f"Error extracting text from PDF with PyMuPDF: {e}")
        # Fallback to PyPDF2
        try:
            with open(file_path, 'rb') as file:
                reader = PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
                return text.strip()
        except Exception as e2:
            logging.error(f"Error extracting text from PDF with PyPDF2: {e2}")
            return None

def extract_text_from_docx(file_path):
    """Extract text from DOCX file"""
    try:
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    except Exception as e:
        logging.error(f"Error extracting text from DOCX: {e}")
        return None

def extract_text_from_doc(file_path):
    """Extract text from DOC file (limited support)"""
    # Note: python-docx doesn't support .doc files directly
    # This is a placeholder - in production, you might want to use python-docx2txt
    # or convert .doc to .docx first
    logging.warning(f"DOC file parsing not fully supported: {file_path}")
    return "DOC file uploaded. Please manually enter your resume content below."

def parse_resume_file(file_obj, filename):
    """
    Parse uploaded resume file and extract text content
    Returns structured resume data
    """
    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as temp_file:
        file_obj.save(temp_file.name)
        temp_path = temp_file.name
    
    try:
        # Determine file type and extract text
        file_ext = filename.lower().split('.')[-1]
        
        if file_ext == 'pdf':
            raw_text = extract_text_from_pdf(temp_path)
        elif file_ext == 'docx':
            raw_text = extract_text_from_docx(temp_path)
        elif file_ext == 'doc':
            raw_text = extract_text_from_doc(temp_path)
        else:
            raw_text = None
        
        if raw_text:
            # Parse the extracted text into structured data
            parsed_data = parse_resume_text(raw_text)
            return parsed_data
        else:
            return {
                'title': f"Uploaded Resume - {filename}",
                'content': "Unable to extract text from file. Please enter your resume content manually.",
                'raw_text': "",
                'contact_info': {},
                'sections': []
            }
    
    except Exception as e:
        logging.error(f"Error parsing resume file: {e}")
        return {
            'title': f"Uploaded Resume - {filename}",
            'content': "Error processing file. Please enter your resume content manually.",
            'raw_text': "",
            'contact_info': {},
            'sections': []
        }
    
    finally:
        # Clean up temporary file
        try:
            os.unlink(temp_path)
        except:
            pass

def parse_resume_text(text):
    """
    Parse raw resume text and extract structured information
    Returns organized resume data
    """
    lines = text.split('\n')
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    
    # Extract basic info
    contact_info = extract_contact_info(text)
    sections = extract_sections(non_empty_lines)
    
    # Create title from filename or first line
    if contact_info.get('name'):
        title = f"Resume - {contact_info['name']}"
    elif non_empty_lines:
        title = f"Resume - {non_empty_lines[0][:50]}"
    else:
        title = "Uploaded Resume"
    
    # Format content for editing
    formatted_content = format_resume_content(sections, contact_info)
    
    return {
        'title': title,
        'content': formatted_content,
        'raw_text': text,
        'contact_info': contact_info,
        'sections': sections
    }

def extract_contact_info(text):
    """Extract contact information from resume text"""
    contact_info = {}
    
    # Email pattern
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text, re.IGNORECASE)
    if emails:
        contact_info['email'] = emails[0]
    
    # Phone pattern (various formats)
    phone_pattern = r'(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}|\+\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9})'
    phones = re.findall(phone_pattern, text)
    if phones:
        contact_info['phone'] = phones[0]
    
    # LinkedIn profile
    linkedin_pattern = r'linkedin\.com/in/[\w-]+'
    linkedin = re.findall(linkedin_pattern, text, re.IGNORECASE)
    if linkedin:
        contact_info['linkedin'] = linkedin[0]
    
    # Name extraction (first few lines that look like names)
    lines = text.split('\n')[:5]  # Check first 5 lines
    for line in lines:
        line = line.strip()
        if (len(line.split()) >= 2 and 
            len(line.split()) <= 4 and 
            line.replace(' ', '').replace('.', '').isalpha() and
            '@' not in line and
            len(line) < 50):
            contact_info['name'] = line
            break
    
    return contact_info

def extract_sections(lines):
    """Extract different sections from resume lines"""
    sections = []
    current_section = None
    current_content = []
    
    # Common section headers
    section_keywords = [
        'experience', 'work experience', 'employment', 'professional experience',
        'education', 'academic background', 'qualifications',
        'skills', 'technical skills', 'core competencies', 'expertise',
        'summary', 'professional summary', 'profile', 'objective',
        'projects', 'achievements', 'accomplishments',
        'certifications', 'licenses', 'awards'
    ]
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if this line is a section header
        is_section_header = False
        for keyword in section_keywords:
            if keyword in line.lower() and len(line) < 50:
                is_section_header = True
                break
        
        if is_section_header:
            # Save previous section
            if current_section and current_content:
                sections.append({
                    'title': current_section,
                    'content': '\n'.join(current_content)
                })
            
            # Start new section
            current_section = line
            current_content = []
        else:
            # Add to current section
            if current_section:
                current_content.append(line)
            else:
                # If no section yet, this might be summary/header content
                if not sections:
                    sections.append({
                        'title': 'Professional Summary',
                        'content': line
                    })
    
    # Add last section
    if current_section and current_content:
        sections.append({
            'title': current_section,
            'content': '\n'.join(current_content)
        })
    
    return sections

def format_resume_content(sections, contact_info):
    """Format extracted content for editing"""
    content_parts = []
    
    # Add contact info if available
    if contact_info:
        contact_parts = []
        if contact_info.get('name'):
            contact_parts.append(f"Name: {contact_info['name']}")
        if contact_info.get('email'):
            contact_parts.append(f"Email: {contact_info['email']}")
        if contact_info.get('phone'):
            contact_parts.append(f"Phone: {contact_info['phone']}")
        if contact_info.get('linkedin'):
            contact_parts.append(f"LinkedIn: {contact_info['linkedin']}")
        
        if contact_parts:
            content_parts.append("CONTACT INFORMATION")
            content_parts.extend(contact_parts)
            content_parts.append("")
    
    # Add sections
    for section in sections:
        content_parts.append(section['title'].upper())
        content_parts.append(section['content'])
        content_parts.append("")
    
    return '\n'.join(content_parts)
