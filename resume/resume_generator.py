import openai
import os
from openai import OpenAI
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from weasyprint import HTML
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import re


# Initialize OpenAI client
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def generate_resume(name, phone, email, job_title, experience):
    prompt = f"""
    Create a professional resume for the role of {job_title}.
    Include:
    - A PROFESSIONAL SUMMARY
    - SKILLS (bulleted)
    - WORK EXPERIENCE (bulleted with job titles and years)
    - EDUCATION (bulleted)

    Use plain text sections so it can be inserted into HTML blocks.
    """
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def build_template_resume(name, contact, resume_text):
    sections = resume_text.split("\n\n")
    section_blocks = ""

    for section in sections:
        lines = section.strip().split("\n")
        if not lines:
            continue
        title = lines[0]
        content = ""
        if len(lines) > 1:
            if all(line.startswith("•") or line.startswith("-") for line in lines[1:]):
                content += "<ul>"
                for item in lines[1:]:
                    content += f"<li>{item[1:].strip()}</li>"
                content += "</ul>"
            else:
                for line in lines[1:]:
                    content += f"<p>{line.strip()}</p>"
        section_blocks += f"<div class='section'><h2>{title}</h2>{content}</div>"

    html = f"""
    <html>
    <head>
    <style>
    body {{ font-family: Arial, sans-serif; margin: 40px; }}
    .header {{ text-align: center; margin-bottom: 30px; }}
    .name {{ font-size: 28px; font-weight: bold; }}
    .contact {{ font-size: 14px; color: #555; }}
    .section {{ margin-bottom: 25px; }}
    h2 {{ background-color: #f0f0f0; padding: 8px; color: #2c3e50; border-left: 4px solid #3498db; }}
    ul {{ margin-top: 0; padding-left: 20px; }}
    li {{ margin-bottom: 4px; }}
    </style>
    </head>
    <body>
        <div class="header">
            <div class="name">{name}</div>
            <div class="contact">{contact}</div>
        </div>
        {section_blocks}
    </body>
    </html>
    """
    return html

def generate_cover_letter(name, email, job_title, description):
    prompt = f"""
    Write a professional cover letter for {name} applying to a {job_title} position.
    The cover letter should highlight relevant skills and refer to the following job description:
    {description}
    """
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def generate_interview_qa(job_title):
    prompt = f"""
    Generate a list of common interview questions and answers for a {job_title} position. Provide at least 5 questions and model answers.
    """
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content    


def analyze_job_posting(job_url):
    """
    Analyze a job posting URL and extract key information
    Returns: dict with company, title, requirements
    """
    try:
        # Multiple strategies to handle different job sites and anti-bot measures
        return analyze_job_with_fallback_strategies(job_url)
        
    except Exception as e:
        return {
            'error': f'Failed to analyze job posting: {str(e)}',
            'company': 'Company',
            'title': 'Position',
            'requirements': 'Could not analyze job requirements. Please paste the job description manually for better analysis.'
        }

def analyze_job_with_fallback_strategies(job_url):
    """
    Try multiple strategies to fetch job posting content
    """
    strategies = [
        fetch_with_enhanced_headers,
        fetch_with_session,
        parse_job_url_info
    ]
    
    for strategy in strategies:
        try:
            text_content = strategy(job_url)
            if text_content and len(text_content) > 100:  # Valid content threshold
                return analyze_with_ai(text_content, job_url)
        except Exception as e:
            print(f"Strategy failed: {e}")
            continue
    
    # If all strategies fail, return helpful guidance
    return {
        'error': 'Job posting could not be accessed automatically',
        'company': 'Company',
        'title': 'Position', 
        'requirements': 'This job site blocks automated access. Please copy and paste the job description manually for optimal resume tailoring.',
        'suggestion': 'Copy the job description text and paste it into the additional requirements field for better analysis.'
    }

def fetch_with_enhanced_headers(job_url):
    """Strategy 1: Enhanced browser headers with session simulation"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0'
    }
    
    response = requests.get(job_url, headers=headers, timeout=15, allow_redirects=True)
    response.raise_for_status()
    return extract_text_from_html(response.text)

def fetch_with_session(job_url):
    """Strategy 2: Use session with cookies and referrer"""
    session = requests.Session()
    
    # First, visit the main site to get cookies
    parsed_url = urlparse(job_url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    
    session.get(base_url, timeout=10)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        'Referer': base_url,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    response = session.get(job_url, headers=headers, timeout=15)
    response.raise_for_status()
    return extract_text_from_html(response.text)

def parse_job_url_info(job_url):
    """Strategy 3: Extract info from URL and provide guidance"""
    parsed = urlparse(job_url)
    
    # Extract basic info from URL if possible
    job_info = ""
    if 'indeed.com' in parsed.netloc:
        job_info = "Indeed job posting - "
    elif 'linkedin.com' in parsed.netloc:
        job_info = "LinkedIn job posting - "
    elif 'glassdoor.com' in parsed.netloc:
        job_info = "Glassdoor job posting - "
    
    # This strategy doesn't actually fetch content, but provides guidance
    return f"{job_info}Please copy and paste the job description manually for optimal analysis."

def extract_text_from_html(html_content):
    """Extract clean text from HTML content"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove script and style elements
    for script in soup(["script", "style", "nav", "footer", "header"]):
        script.decompose()
    
    # Try to find job-specific content areas
    job_content_selectors = [
        '[data-testid="jobsearch-JobComponent-description"]',  # Indeed
        '.jobs-description-content__text',  # LinkedIn
        '.jobDescriptionContent',  # Glassdoor
        '.job-description',
        '.description',
        '[class*="description"]',
        '[id*="description"]'
    ]
    
    job_content = None
    for selector in job_content_selectors:
        elements = soup.select(selector)
        if elements:
            job_content = elements[0]
            break
    
    # If no specific job content found, use the whole page
    if not job_content:
        job_content = soup
    
    # Extract text content
    text_content = job_content.get_text()
    
    # Clean up the text
    lines = (line.strip() for line in text_content.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    clean_text = ' '.join(chunk for chunk in chunks if chunk)
    
    return clean_text

def analyze_with_ai(text_content, job_url):
    """Use AI to analyze the extracted job posting content"""
    # Limit content to avoid token limits
    content_for_analysis = text_content[:4000]
    
    analysis_prompt = f"""
    Analyze this job posting and extract key information. Return a structured response with:
    - company: Company name
    - title: Job title
    - requirements: A concise summary of key requirements, skills, and qualifications
    
    Job posting content:
    {content_for_analysis}
    
    Return the response in this exact format:
    Company: [company name]
    Title: [job title] 
    Requirements: [key requirements and skills in 2-3 sentences]
    """
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": analysis_prompt}],
        max_tokens=300
    )
    
    analysis = response.choices[0].message.content
    
    # Parse the AI response
    result = {
        'company': 'Company',
        'title': 'Position',
        'requirements': 'Requirements analysis in progress...'
    }
    
    for line in analysis.split('\n'):
        line = line.strip()
        if line.startswith('Company:'):
            result['company'] = line.replace('Company:', '').strip()
        elif line.startswith('Title:'):
            result['title'] = line.replace('Title:', '').strip()
        elif line.startswith('Requirements:'):
            result['requirements'] = line.replace('Requirements:', '').strip()
    
    return result


def tailor_resume_to_job(experience, job_url, job_title):
    """
    Tailor resume content to match job requirements from a job posting URL
    """
    try:
        # Analyze the job posting
        job_analysis = analyze_job_posting(job_url)
        
        if 'error' in job_analysis:
            # If job analysis fails, return original experience
            return experience
        
        # Use AI to tailor the resume content
        tailoring_prompt = f"""
        Tailor this resume content to match the job requirements. 
        
        Job Title: {job_title}
        Company: {job_analysis.get('company', 'Target Company')}
        Job Requirements: {job_analysis.get('requirements', '')}
        
        Original Resume Content:
        {experience}
        
        Instructions:
        1. Keep all factual information accurate
        2. Emphasize relevant skills and experiences that match the job requirements
        3. Use keywords from the job posting naturally
        4. Reorganize content to highlight most relevant qualifications first
        5. Maintain professional tone and formatting
        6. Do not add false information or experiences
        
        Return the tailored resume content:
        """
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": tailoring_prompt}],
            max_tokens=1500
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        # If tailoring fails, return original content
        return experience


def export_pdf_from_html(html_string, filename="styled_resume.pdf"):
    HTML(string=html_string).write_pdf(filename)
    print(f"✅ Resume created: {filename}")

if __name__ == "__main__":
    job_title = "Systems Designer"
    experience = (
        "Led a team of 10 engineers in designing scalable systems in finance and healthcare. "
        "Increased performance by 30%. Experienced in agile development and cross-functional collaboration."
    )
    name = {name}
    contact = {email} + " | " + {phone} + " | www.reallygreatsite.com"

    resume_text = generate_resume(name, phone, email, job_title, experience)
    html_resume = build_template_resume(name, contact, resume_text)
    export_pdf_from_html(html_resume)
