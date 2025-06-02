import openai
import os
from openai import OpenAI
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from weasyprint import HTML


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
