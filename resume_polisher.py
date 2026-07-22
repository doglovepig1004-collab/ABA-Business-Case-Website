import os
from typing import Dict, List
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()


def extract_text_from_resume(file_path: str) -> str:
    """Extract plain text from a resume file. Supports PDF only."""
    try:
        from PyPDF2 import PdfReader
    except ImportError:
        raise RuntimeError('PyPDF2 is required to extract resume text from PDF files.')

    reader = PdfReader(file_path)
    text = []
    for page in reader.pages:
        page_text = page.extract_text() or ''
        text.append(page_text)
    return '\n'.join(text).strip()


def generate_resume_feedback(resume_text: str, target_position: str) -> str:
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError('GEMINI_API_KEY environment variable not set')

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('models/gemini-2.5-flash')

    prompt = f"""You are an AI resume reviewer for banking career applicants.

Resume Text:
{resume_text}

Target Position: {target_position}

Provide:
1. Three concrete ways to improve this resume for the target role.
2. Three likely interview questions tailored to the target position and this candidate's background.
3. One short recommendation on strengths to highlight.

Keep the response professional, practical, and under 300 words."""

    response = model.generate_content(prompt)
    if hasattr(response, 'text'):
        return response.text
    if isinstance(response, dict):
        return response.get('output', '') or response.get('text', '') or str(response)
    return str(response)
