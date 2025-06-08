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
        # Set headers to mimic a real browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        # Fetch the job posting
        response = requests.get(job_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Extract text content
        text_content = soup.get_text()
        
        # Clean up the text
        lines = (line.strip() for line in text_content.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text_content = ' '.join(chunk for chunk in chunks if chunk)
        
        # Use AI to analyze the job posting
        analysis_prompt = f"""
        Analyze this job posting and extract key information. Return a JSON-like response with:
        - company: Company name
        - title: Job title
        - requirements: A concise summary of key requirements, skills, and qualifications
        
        Job posting content:
        {text_content[:4000]}
        
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
            if line.startswith('Company:'):
                result['company'] = line.replace('Company:', '').strip()
            elif line.startswith('Title:'):
                result['title'] = line.replace('Title:', '').strip()
            elif line.startswith('Requirements:'):
                result['requirements'] = line.replace('Requirements:', '').strip()
        
        return result
        
    except Exception as e:
        return {
            'error': f'Failed to analyze job posting: {str(e)}',
            'company': 'Company',
            'title': 'Position',
            'requirements': 'Could not analyze job requirements'
        }


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
