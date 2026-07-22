import re
import os
from typing import Dict, List, Optional
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()


def score_job_for_profile(job: Dict, major: str, grade: str, personality_traits: List[str]) -> float:
    score = 0.0

    if major and major in job.get('suitable_major', []):
        score += 40
    elif major and major == 'Any Major':
        score += 20

    job_grade = job.get('suitable_grade', '').lower()
    user_grade = grade.lower()
    if user_grade and user_grade in job_grade:
        score += 30
    elif 'preferred' in job_grade and 'graduate' in user_grade:
        score += 20
    elif 'graduate' in user_grade and 'graduate' in job_grade:
        score += 25
    elif 'senior' in user_grade and 'senior' in job_grade:
        score += 25

    matched_traits = 0
    for trait in personality_traits:
        if trait in job.get('personality', []):
            matched_traits += 1
    if job.get('personality'):
        score += (matched_traits / len(job['personality'])) * 30

    return min(score, 100)


def get_relevant_jobs(user_profile: Dict, jobs_list: List[Dict], count: int = 5) -> List[Dict]:
    major = user_profile.get('major', '')
    grade = user_profile.get('grade', '')
    personality = user_profile.get('personality', [])

    scored_jobs = []
    for job in jobs_list:
        score = score_job_for_profile(job, major, grade, personality)
        job_copy = dict(job)
        job_copy['match_score'] = score
        scored_jobs.append(job_copy)

    scored_jobs.sort(key=lambda x: x['match_score'], reverse=True)
    return scored_jobs[:count]


def generate_advice(user_profile: Dict, question: str, relevant_jobs: List[Dict]) -> str:
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    
    major = user_profile.get('major', 'an interest area')
    grade = user_profile.get('grade', 'your level')
    personality = user_profile.get('personality', [])
    personality_list = ', '.join(personality) if personality else 'a diverse mix of strengths'
    
    # Build job recommendations summary
    jobs_info = "Top recommended roles for you:\n"
    for job in relevant_jobs:
        jobs_info += f"- {job['name']} ({job['department']}): {job['salary']}, Match score: {job['match_score']:.0f}%\n"
    
    prompt = f"""You are an AI career advisor helping a student explore banking careers.

Student Profile:
- Major: {major}
- Level/Grade: {grade}
- Personality Traits: {personality_list}

{jobs_info}

Student Question: {question.strip()}

Based on this profile and question, provide personalized, practical career advice. Keep the response concise (200-300 words), professional, and directly address their question. Include specific insights about how their background matches these roles and actionable next steps."""
    
    try:
        response = model.generate_content(prompt)
        # Some SDKs return the content differently; attempt common access patterns
        if hasattr(response, 'text'):
            return response.text
        if isinstance(response, dict):
            # Try common keys
            return response.get('output', '') or response.get('text', '') or str(response)
        return str(response)
    except Exception as e:
        # Log and produce a local fallback so the user still gets useful advice
        print(f"Gemini API error: {e}")
        return _local_fallback_advice(user_profile, question, relevant_jobs)


def _local_fallback_advice(user_profile: Dict, question: str, relevant_jobs: List[Dict]) -> str:
    """Simple rule-based fallback advice when Gemini API is unavailable."""
    major = user_profile.get('major', 'your field')
    grade = user_profile.get('grade', 'your level')
    personality = user_profile.get('personality', [])

    lines = [f"Fallback Advisor — based on {major}, level: {grade}."]
    if relevant_jobs:
        lines.append('Top recommended roles:')
        for job in relevant_jobs:
            lines.append(f"- {job.get('name')} ({job.get('department')}), match {job.get('match_score',0):.0f}%")
    else:
        lines.append('No strong role matches found for your profile yet.')

    q = (question or '').lower()
    if any(k in q for k in ('skill', 'skills', 'competency')):
        # aggregate skills from jobs
        skills = []
        for job in relevant_jobs:
            for s in job.get('skills', []):
                if s not in skills:
                    skills.append(s)
        if skills:
            lines.append('\nKey skills to highlight: ' + ', '.join(skills))
        else:
            lines.append('\nKey skills to highlight: communication, analysis, Excel/SQL (if relevant)')
        lines.append('\nAction: add project examples and measurable outcomes to your resume.')
    elif any(k in q for k in ('interview', 'resume', 'prepare', 'application')):
        lines.append('\nPreparation tips: tailor your resume to the job, use challenge-action-result stories for interviews, and practice short explanations of projects.')
    elif any(k in q for k in ('career', 'path', 'growth', 'transition')):
        lines.append('\nCareer tip: start in roles that build technical skills and stakeholder exposure; seek mentors and small stretch projects.')
    else:
        lines.append('\nGeneral advice: emphasize relevant coursework, internships, and concrete examples showing impact. Ask a follow-up for specific role guidance.')

    return "\n".join(lines)


