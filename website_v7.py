# %%
# Notebook setup: pip install flask flask-ngrok

# %%
from flask import Flask, render_template_string, request, redirect, url_for, send_from_directory
from flask_ngrok import run_with_ngrok
from werkzeug.utils import secure_filename
from datetime import datetime, timezone
import json
import sys
import os
import tempfile
import uuid
import ai_advisor
import resume_polisher

# %%
app = Flask(__name__)
# run_with_ngrok(app)  # Comment this out if running locally

@app.route('/background1.jpg')
def background_image():
    """Serve the site background image from the project folder."""
    return send_from_directory(notebook_path, 'background1.jpg')

@app.route('/banking-future-logo.svg')
def banking_future_logo():
    """Serve the Banking on the Future logo from the project folder."""
    return send_from_directory(notebook_path, 'banking_future_logo.svg')

# %%
# Get the current notebook directory
notebook_path = os.getcwd()
ABA_SUBMISSION_DIR = os.path.join(notebook_path, 'aba_resume_submissions')
ABA_SUBMISSION_METADATA = os.path.join(ABA_SUBMISSION_DIR, 'submissions.jsonl')
ABA_ALLOWED_RESUME_EXTENSIONS = {'.pdf', '.doc', '.docx', '.txt'}
ABA_MAX_RESUME_SIZE = 5 * 1024 * 1024

# Load the expanded entry-level banking role and salary dataset.
try:
    from website_data_role_specific_examples import DATASET_METADATA, jobs_list
    print(f"✅ Successfully imported {len(jobs_list)} jobs from website_data_role_specific_examples.py")
except ImportError:
    print("❌ website_data_role_specific_examples.py not found")
    print("Please make sure website_data_role_specific_examples.py is in the same folder as this application")
    DATASET_METADATA = {}
    jobs_list = []  # Empty list as fallback
except Exception as e:
    print(f"❌ Error loading website_data_role_specific_examples.py: {e}")
    DATASET_METADATA = {}
    jobs_list = []

# %%
def get_all_majors():
    """Extract all unique majors from the job database"""
    majors = set()
    for job in jobs_list:
        for major in job["suitable_major"]:
            if not major.lower().startswith("varies;"):
                majors.add(major)
    return sorted(list(majors))

# %%
def get_all_personality():
    """Extract all unique personality traits from the job database"""
    traits = set()
    for job in jobs_list:
        for trait in job["personality"]:
            traits.add(trait)
    return sorted(list(traits))

# %%
def calculate_match_score(job, major, grade, personality_traits):
    """
    Calculate match score between a job and user profile
    Returns a score from 0 to 100
    """
    score = 0
    
    # Major match (max 40 points)
    if major in job["suitable_major"]:
        score += 40
    elif "Any Major" in job["suitable_major"]:
        score += 30
    elif any(item.lower().startswith("varies;") for item in job["suitable_major"]):
        score += 30
    
    # Career-stage match (max 30 points). User stages are mutually exclusive,
    # while job eligibility labels may contain several compatible stages.
    job_level = job["suitable_grade"].lower()
    user_stage = grade.lower()
    if "depending on level" in job_level:
        score += 26
    elif "undergraduate (years 1-2)" in user_stage:
        if "fresh graduate" in job_level or "junior" in job_level:
            score += 18
    elif "undergraduate (years 3-4)" in user_stage:
        if "fresh graduate" in job_level or "recent graduate" in job_level or "junior" in job_level:
            score += 27
        elif "senior" in job_level:
            score += 18
    elif "graduate student" in user_stage:
        if "graduate student" in job_level:
            score += 30
        elif "fresh graduate" in job_level or "junior" in job_level:
            score += 22
    elif "recent graduate (0-1 years)" in user_stage:
        if "fresh graduate" in job_level or "recent graduate" in job_level:
            score += 30
        elif "junior" in job_level:
            score += 25
    elif "early career professional (1-3 years)" in user_stage:
        if "junior" in job_level:
            score += 30
        elif "fresh graduate" in job_level or "recent graduate" in job_level:
            score += 24
        elif "senior" in job_level:
            score += 18
    elif "experienced professional (3+ years)" in user_stage:
        if "senior" in job_level or "experienced" in job_level:
            score += 30
        elif "junior" in job_level:
            score += 15
    
    # Personality match (max 30 points)
    matched_traits = 0
    for trait in personality_traits:
        if trait in job["personality"]:
            matched_traits += 1
    
    if len(job["personality"]) > 0:
        score += (matched_traits / len(job["personality"])) * 30
    
    # Ensure score doesn't exceed 100
    return min(score, 100)

# %%
favorite_script = '''
<script>
    (() => {
        const storageKey = 'bankingCareerFavorites';

        function readFavorites() {
            try {
                const saved = JSON.parse(localStorage.getItem(storageKey) || '[]');
                return Array.isArray(saved) ? saved.map(String) : [];
            } catch (error) {
                return [];
            }
        }

        function writeFavorites(ids) {
            try {
                localStorage.setItem(storageKey, JSON.stringify([...ids]));
            } catch (error) {
                // The controls still work for the current page when storage is unavailable.
            }
        }

        function updateFavoriteUI() {
            const favorites = new Set(readFavorites());

            document.querySelectorAll('[data-favorite-count]').forEach((element) => {
                element.textContent = favorites.size;
            });

            document.querySelectorAll('[data-favorite-button]').forEach((button) => {
                const isSaved = favorites.has(String(button.dataset.jobId));
                button.classList.toggle('is-favorite', isSaved);
                button.setAttribute('aria-pressed', String(isSaved));
                button.textContent = isSaved ? 'Saved' : 'Save Job';
            });

            if (document.body.dataset.page === 'favorites') {
                let visibleCards = 0;
                document.querySelectorAll('[data-favorite-card]').forEach((card) => {
                    const isVisible = favorites.has(String(card.dataset.jobId));
                    card.classList.toggle('d-none', !isVisible);
                    if (isVisible) visibleCards += 1;
                });
                const emptyState = document.querySelector('[data-favorites-empty]');
                if (emptyState) emptyState.hidden = visibleCards > 0;
            }
        }

        document.addEventListener('click', (event) => {
            const button = event.target.closest('[data-favorite-button]');
            if (!button) return;

            const favorites = new Set(readFavorites());
            const jobId = String(button.dataset.jobId);
            favorites.has(jobId) ? favorites.delete(jobId) : favorites.add(jobId);
            writeFavorites(favorites);
            updateFavoriteUI();
        });

        updateFavoriteUI();
    })();
</script>
'''

# %%
index_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Banking on the Future</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&display=swap" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(rgba(245, 247, 250, 0.82), rgba(245, 247, 250, 0.82)), url('/background1.jpg') center / cover fixed no-repeat;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .navbar { background: #0a1628 !important; }
        .navbar-brand { color: #ffffff !important; font-family: 'Cormorant Garamond', Georgia, serif; font-size: 1.65rem; font-weight: 700; letter-spacing: 0.015em; line-height: 1; display: inline-flex; align-items: center; gap: 11px; }
        .brand-icon { display: inline-grid; place-items: center; width: 38px; height: 38px; border: 1px solid rgba(248, 200, 66, 0.72); border-radius: 10px; background: linear-gradient(145deg, rgba(248, 200, 66, 0.2), rgba(248, 200, 66, 0.05)); box-shadow: inset 0 0 0 1px rgba(255,255,255,0.05); font-size: 1.05rem; }
        .brand-highlight { color: #f8c842; font-weight: 600; }
        .brand-logo { display: block; width: 42px; height: 42px; flex: 0 0 auto; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.14); }
        .brand-copy { display: flex; flex-direction: column; gap: 4px; }
        .brand-title { line-height: 0.9; }
        .brand-attribution { color: rgba(255,255,255,0.72); font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; font-size: 0.56rem; font-weight: 700; letter-spacing: 0.12em; line-height: 1; text-transform: uppercase; }
        .nav-actions { display: flex; flex-wrap: wrap; justify-content: flex-end; gap: 10px; }
        .nav-button { padding: 8px 18px; border: 1px solid transparent; border-radius: 999px; font-weight: 600; text-decoration: none; transition: background-color 0.2s, color 0.2s, transform 0.2s; }
        .nav-button:hover { transform: translateY(-1px); }
        .nav-button:focus-visible { outline: none; box-shadow: 0 0 0 3px rgba(248, 200, 66, 0.4); }
        .nav-home { color: white; border-color: rgba(255,255,255,0.7); }
        .nav-home:hover { color: #0a1628; background: white; }
        .nav-favorites { color: white; border-color: rgba(255,255,255,0.7); }
        .nav-favorites:hover { color: #0a1628; background: white; }
        .nav-match { color: #0a1628; background: #f8c842; border-color: #f8c842; }
        .nav-match:hover { color: #0a1628; background: #e6b83a; border-color: #e6b83a; }
        .card { border: none; border-radius: 16px; box-shadow: 0 6px 20px rgba(0,0,0,0.08); transition: transform 0.3s; }
        .card:hover { transform: translateY(-6px); }
        .job-card { height: 100%; }
        .job-card .job-description { flex-grow: 1; }
        .job-card h5, .job-card h6 { overflow-wrap: anywhere; }
        .job-meta { display: flex; flex-wrap: wrap; gap: 0.45rem; margin-top: 0.5rem; }
        .meta-pill { display: inline-flex; align-items: center; max-width: 100%; padding: 0.38rem 0.62rem; border-radius: 9px; font-size: 0.75rem; font-weight: 700; line-height: 1.3; overflow-wrap: anywhere; }
        .salary-pill { background: #e7f5ec; color: #17653a; }
        .level-pill { background: #e6f4f8; color: #174f63; }
        .role-path-panel { margin: 0 0 3rem; padding: 2rem; border: 1px solid rgba(10, 22, 40, 0.1); border-radius: 20px; background: rgba(255,255,255,0.94); box-shadow: 0 10px 30px rgba(10,22,40,0.08); }
        .role-path-panel h2 { color: #0a1628; font-weight: 750; }
        .role-path-options { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1rem; margin-top: 1.5rem; }
        .role-path-button { display: flex; align-items: center; gap: 1rem; min-height: 112px; padding: 1.25rem 1.4rem; border: 2px solid transparent; border-radius: 16px; color: #0a1628; text-align: left; text-decoration: none; transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s; }
        .role-path-button:hover { color: #0a1628; transform: translateY(-3px); box-shadow: 0 10px 24px rgba(10,22,40,0.13); }
        .role-path-button:focus-visible { outline: none; box-shadow: 0 0 0 4px rgba(248,200,66,0.45); }
        .role-path-banking { background: linear-gradient(135deg, #eaf2fb, #ffffff); border-color: #cbdced; }
        .role-path-markets { background: linear-gradient(135deg, #eef7ef, #ffffff); border-color: #cfe4d2; }
        .role-path-controls { background: linear-gradient(135deg, #fff6d9, #ffffff); border-color: #efd77d; }
        .role-path-innovation { background: linear-gradient(135deg, #f2edfb, #ffffff); border-color: #d9ccef; }
        .role-path-icon { display: grid; flex: 0 0 48px; place-items: center; width: 48px; height: 48px; border-radius: 14px; background: #0a1628; color: #f8c842; font-size: 1.35rem; }
        .role-path-label { display: block; font-size: 1.05rem; font-weight: 750; line-height: 1.25; }
        .role-path-description { display: block; margin-top: 0.35rem; color: #5d6878; font-size: 0.88rem; line-height: 1.4; }
        .role-category { scroll-margin-top: 1.5rem; margin-top: 3rem; padding: 1.8rem; border-radius: 20px; background: rgba(255,255,255,0.75); }
        .role-category-heading { color: #0a1628; font-weight: 750; }
        .role-count { display: inline-block; margin-left: 0.45rem; padding: 0.25rem 0.65rem; border-radius: 999px; background: #f8c842; color: #0a1628; font-size: 0.8rem; vertical-align: middle; }
        .office-section { margin-top: 2.5rem; }
        .office-heading { border-left: 5px solid #f8c842; padding-left: 12px; color: #0a1628; }
        .job-title { color: #0a1628; font-weight: 700; text-decoration: none; }
        .job-title:hover { color: #f8c842; }
        .favorite-button { border-color: #d4a900; color: #725b00; font-weight: 600; }
        .favorite-button:hover, .favorite-button.is-favorite { background: #f8c842; border-color: #f8c842; color: #0a1628; }
        .hero { background: linear-gradient(135deg, #0a1628, #1a2a4a); color: white; padding: 60px 0; border-radius: 20px; margin-bottom: 40px; }
        .hero-title { display: inline-block; position: relative; margin-bottom: 1.25rem; font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; font-size: clamp(2.4rem, 6vw, 4.6rem); font-weight: 700; line-height: 1.08; letter-spacing: -0.045em; background: linear-gradient(100deg, #ffffff 18%, #f8c842 82%); -webkit-background-clip: text; background-clip: text; color: transparent; text-shadow: 0 8px 30px rgba(0,0,0,0.18); }
        .hero-title::after { content: ''; position: absolute; left: 50%; bottom: -14px; width: 76px; height: 3px; border-radius: 999px; background: #f8c842; transform: translateX(-50%); box-shadow: 0 0 16px rgba(248, 200, 66, 0.45); }
        .btn-match { background: #f8c842; color: #0a1628; font-weight: 600; border: none; padding: 12px 30px; border-radius: 30px; }
        .btn-match:hover { background: #e6b83a; color: #0a1628; }
        .footer { background: #0a1628; color: white; padding: 20px 0; margin-top: 40px; border-radius: 20px 20px 0 0; }
        :root { --aba-blue: #005a8c; --aba-gray: #58595b; --aba-gold: #dc9f1d; --aba-slate: #4e7c9c; --aba-sans: "Helvetica Neue", Helvetica, Arial, sans-serif; --aba-serif: "Minion Pro", "Times New Roman", Times, serif; }
        body { color: var(--aba-gray); font-family: var(--aba-sans); }
        .navbar, .footer { background: var(--aba-blue) !important; }
        .brand-highlight { color: var(--aba-gold); }
        .brand-icon { border-color: rgba(220,159,29,0.75); background: rgba(220,159,29,0.14); }
        .nav-button:focus-visible, .role-path-button:focus-visible { box-shadow: 0 0 0 4px rgba(220,159,29,0.35); }
        .nav-home:hover, .nav-favorites:hover { color: var(--aba-blue); }
        .nav-match, .btn-match { background: var(--aba-gold); border-color: var(--aba-gold); color: #ffffff; }
        .nav-match:hover, .btn-match:hover { background: #bd8413; border-color: #bd8413; color: #ffffff; }
        .hero { background: linear-gradient(135deg, var(--aba-blue), var(--aba-slate)); }
        .hero-title { background: linear-gradient(100deg, #ffffff 18%, #f0c45b 82%); -webkit-background-clip: text; background-clip: text; }
        .hero-title::after, .role-count { background: var(--aba-gold); }
        .role-path-icon { background: var(--aba-blue); color: var(--aba-gold); }
        .office-heading { border-left-color: var(--aba-gold); color: var(--aba-blue); }
        .job-title { color: var(--aba-blue); }
        .job-title:hover { color: #9b6b08; }
        .favorite-button { border-color: var(--aba-gold); color: #765300; }
        .favorite-button:hover, .favorite-button.is-favorite { background: var(--aba-gold); border-color: var(--aba-gold); color: #ffffff; }
        .role-path-panel p, .role-category > p, .job-description { font-family: var(--aba-serif); }
        .role-path-banking { background: linear-gradient(135deg, #e7f2f8, #ffffff); border-color: #9fc2d6; }
        .role-path-markets { background: linear-gradient(135deg, #edf3f6, #ffffff); border-color: #b7ccd9; }
        .role-path-controls { background: linear-gradient(135deg, #fff6df, #ffffff); border-color: #e5c36d; }
        .role-path-innovation { background: linear-gradient(135deg, #edf3f7, #ffffff); border-color: var(--aba-slate); }
        @media (max-width: 767.98px) {
            .role-path-options { grid-template-columns: 1fr; }
            .role-path-panel, .role-category { padding: 1.25rem; }
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="/"><img class="brand-logo" src="/banking-future-logo.svg" alt="" width="42" height="42"><span class="brand-copy"><span class="brand-title">Banking on the <span class="brand-highlight">Future</span></span><span class="brand-attribution">American Bankers Association</span></span></a>
            <div class="nav-actions">
                <a class="nav-button nav-home" href="/">Home</a>
                <a class="nav-button nav-match" href="/match">Match</a>
                <a class="nav-button nav-match" href="/resume">Resume Review</a>
                <a class="nav-button nav-favorites" href="/favorites">Favorites (<span data-favorite-count>0</span>)</a>
            </div>
        </div>
    </nav>
    
    <div class="container mt-4 flex-grow-1">
        <div class="hero text-center">
            <h1 class="display-3 hero-title">Banking on the Future</h1>
            <p class="lead">Discover your perfect role in the banking industry</p>
            <a href="/match" class="btn btn-match btn-lg">Find My Match</a>
            <a href="/resume" class="btn btn-outline-light btn-lg ms-3">Resume Review</a>
        </div>
        
        <section class="role-path-panel" aria-labelledby="choose-role-path">
            <div class="text-center">
                <h2 id="choose-role-path" class="h3 mb-2">Where could you fit in banking?</h2>
                <p class="text-muted mb-0">The banking industry needs people with many different strengths. Use our website to explore the paths and discover where you could fit.</p>
            </div>
            <div class="role-path-options">
                {% for category in role_categories %}
                <a class="role-path-button {{ category.button_class }}" href="#{{ category.id }}">
                    <span class="role-path-icon" aria-hidden="true">{{ category.icon }}</span>
                    <span>
                        <span class="role-path-label">{{ category.name }}</span>
                        <span class="role-path-description">{{ category.button_description }}</span>
                    </span>
                </a>
                {% endfor %}
            </div>
        </section>

        {% for category in role_categories %}
        <section id="{{ category.id }}" class="role-category">
            <h3 class="role-category-heading">{{ category.name }}<span class="role-count">{{ category.job_count }} roles</span></h3>
            <p class="text-muted mb-0">{{ category.description }}</p>

            {% for group in category.groups %}
            <div class="office-section">
                <h4 class="office-heading">{{ group.name }}</h4>
                <p class="text-muted">{{ group.description }} · {{ group.jobs|length }} roles</p>
                <div class="row">
                    {% for job in group.jobs %}
                    <div class="col-md-6 col-lg-4 mb-4 d-flex">
                        <div class="card job-card p-3 d-flex flex-column w-100">
                            <h5><a href="/job/{{ job.id }}" class="job-title">{{ job.name }}</a></h5>
                            <h6 class="text-muted">{{ job.department }}</h6>
                            <p class="job-description text-muted small">{{ job.description[:120] }}...</p>
                            <div class="job-meta">
                                <span class="meta-pill salary-pill">💰 {{ job.salary }}</span>
                                <span class="meta-pill level-pill">🎓 {% if 'depending on level' in job.suitable_grade %}Multiple experience levels{% else %}{{ job.suitable_grade }}{% endif %}</span>
                            </div>
                            <div class="d-flex gap-2 mt-2">
                                <a href="/job/{{ job.id }}" class="btn btn-outline-dark btn-sm flex-grow-1">View Details</a>
                                <button type="button" class="btn favorite-button btn-sm" data-favorite-button data-job-id="{{ job.id }}" aria-pressed="false">Save Job</button>
                            </div>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endfor %}
        </section>
        {% endfor %}
    </div>
    
    <div class="footer">
        <div class="container text-center">
            <p class="mb-0">🏦 Banking on the Future © 2026</p>
        </div>
    </div>
    {{ favorite_script | safe }}
</body>
</html>
'''

# %%
detail_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ job.name }} - Banking on the Future</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&display=swap" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(rgba(245, 247, 250, 0.82), rgba(245, 247, 250, 0.82)), url('/background1.jpg') center / cover fixed no-repeat;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .navbar { background: #0a1628 !important; }
        .navbar-brand { color: #ffffff !important; font-family: 'Cormorant Garamond', Georgia, serif; font-size: 1.65rem; font-weight: 700; letter-spacing: 0.015em; line-height: 1; display: inline-flex; align-items: center; gap: 11px; }
        .brand-icon { display: inline-grid; place-items: center; width: 38px; height: 38px; border: 1px solid rgba(248, 200, 66, 0.72); border-radius: 10px; background: linear-gradient(145deg, rgba(248, 200, 66, 0.2), rgba(248, 200, 66, 0.05)); box-shadow: inset 0 0 0 1px rgba(255,255,255,0.05); font-size: 1.05rem; }
        .brand-highlight { color: #f8c842; font-weight: 600; }
        .brand-logo { display: block; width: 42px; height: 42px; flex: 0 0 auto; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.14); }
        .brand-copy { display: flex; flex-direction: column; gap: 4px; }
        .brand-title { line-height: 0.9; }
        .brand-attribution { color: rgba(255,255,255,0.72); font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; font-size: 0.56rem; font-weight: 700; letter-spacing: 0.12em; line-height: 1; text-transform: uppercase; }
        .nav-actions { display: flex; flex-wrap: wrap; justify-content: flex-end; gap: 10px; }
        .nav-button { padding: 8px 18px; border: 1px solid transparent; border-radius: 999px; font-weight: 600; text-decoration: none; transition: background-color 0.2s, color 0.2s, transform 0.2s; }
        .nav-button:hover { transform: translateY(-1px); }
        .nav-button:focus-visible { outline: none; box-shadow: 0 0 0 3px rgba(248, 200, 66, 0.4); }
        .nav-home { color: white; border-color: rgba(255,255,255,0.7); }
        .nav-home:hover { color: #0a1628; background: white; }
        .nav-favorites { color: white; border-color: rgba(255,255,255,0.7); }
        .nav-favorites:hover { color: #0a1628; background: white; }
        .nav-match { color: #0a1628; background: #f8c842; border-color: #f8c842; }
        .nav-match:hover { color: #0a1628; background: #e6b83a; border-color: #e6b83a; }
        .btn-match { background: #f8c842; color: #0a1628; font-weight: 600; border: none; padding: 12px 30px; border-radius: 30px; }
        .btn-match:hover { background: #e6b83a; }
        .favorite-button { border-color: #d4a900; color: #725b00; font-weight: 600; }
        .favorite-button:hover, .favorite-button.is-favorite { background: #f8c842; border-color: #f8c842; color: #0a1628; }
        .detail-card { overflow: hidden; }
        .detail-pill { display: inline-block; max-width: 100%; padding: 0.48rem 0.72rem; border-radius: 10px; font-size: 0.86rem; font-weight: 700; line-height: 1.35; white-space: normal; overflow-wrap: anywhere; }
        .salary-detail { background: #daf1e3; color: #155d36; }
        .level-detail { background: #dff2f7; color: #174f63; }
        .compensation-note { margin-top: 0.55rem; color: #667085; font-size: 0.78rem; line-height: 1.45; }
        .tag-wrap { display: flex; flex-wrap: wrap; gap: 0.42rem; }
        .detail-tag { display: inline-block; max-width: 100%; padding: 0.34rem 0.56rem; border-radius: 8px; font-size: 0.75rem; font-weight: 700; line-height: 1.3; white-space: normal; overflow-wrap: anywhere; }
        .major-tag { background: #dce9ff; color: #17448a; }
        .trait-tag { background: #ece8f7; color: #544074; }
        .skill-tag { background: #e7eaf0; color: #263347; }
        .open-major-note { padding: 0.7rem; border-radius: 10px; background: #eaf2ff; color: #294d7a; font-size: 0.84rem; line-height: 1.45; }
        .fact-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0.75rem; margin-top: 1.25rem; }
        .fact-card { min-width: 0; padding: 0.8rem; border: 1px solid #e3e7ed; border-radius: 11px; background: #f8fafc; }
        .fact-label { display: block; margin-bottom: 0.25rem; color: #7a8493; font-size: 0.67rem; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; }
        .fact-value { display: block; color: #243248; font-size: 0.88rem; font-weight: 700; line-height: 1.35; overflow-wrap: anywhere; }
        .career-details { margin-top: 2rem; padding-top: 1.5rem; border-top: 1px solid #e3e7ed; }
        .career-path-box { padding: 1rem 1.15rem; border-left: 4px solid #f8c842; border-radius: 0 12px 12px 0; background: #fff9df; color: #25334a; }
        .interview-list { margin-bottom: 0; padding-left: 1.25rem; }
        .interview-list li { margin-bottom: 0.55rem; color: #475467; }
        .entry-snapshot { margin-top: 1.5rem; padding: 1.15rem; border-radius: 14px; background: linear-gradient(135deg, #edf5ff, #f8fbff); }
        .entry-snapshot p { margin-bottom: 0.55rem; color: #40516a; line-height: 1.55; }
        .info-disclosure { margin-top: 1rem; border: 1px solid #dfe5ed; border-radius: 13px; background: white; }
        .info-disclosure summary { padding: 1rem 1.1rem; color: #0a1628; font-weight: 800; cursor: pointer; list-style-position: inside; }
        .info-disclosure[open] summary { border-bottom: 1px solid #e5e9ef; }
        .disclosure-body { padding: 1rem 1.1rem; }
        .example-card { padding: 1rem; border: 1px solid #e4e8ee; border-radius: 12px; background: #fafbfc; }
        .example-card + .example-card { margin-top: 0.85rem; }
        .example-card h6 { overflow-wrap: anywhere; }
        .example-card ul { margin-bottom: 0.7rem; padding-left: 1.15rem; color: #596579; font-size: 0.86rem; }
        .source-link { color: #765d00; font-size: 0.82rem; font-weight: 700; }
        .footer { background: #0a1628; color: white; padding: 20px 0; margin-top: 40px; border-radius: 20px 20px 0 0; }
        :root { --aba-blue: #005a8c; --aba-gray: #58595b; --aba-gold: #dc9f1d; --aba-slate: #4e7c9c; --aba-sans: "Helvetica Neue", Helvetica, Arial, sans-serif; --aba-serif: "Minion Pro", "Times New Roman", Times, serif; }
        body { color: var(--aba-gray); font-family: var(--aba-sans); }
        .navbar, .footer { background: var(--aba-blue) !important; }
        .brand-highlight { color: var(--aba-gold); }
        .brand-icon { border-color: rgba(220,159,29,0.75); background: rgba(220,159,29,0.14); }
        .nav-button:focus-visible { box-shadow: 0 0 0 3px rgba(220,159,29,0.35); }
        .nav-home:hover, .nav-favorites:hover { color: var(--aba-blue); }
        .nav-match, .btn-match { background: var(--aba-gold); border-color: var(--aba-gold); color: #ffffff; }
        .nav-match:hover, .btn-match:hover { background: #bd8413; border-color: #bd8413; color: #ffffff; }
        .favorite-button { border-color: var(--aba-gold); color: #765300; }
        .favorite-button:hover, .favorite-button.is-favorite { background: var(--aba-gold); border-color: var(--aba-gold); color: #ffffff; }
        .career-path-box { border-left-color: var(--aba-gold); background: #fff7e5; }
        .major-tag { background: #e4f0f7; color: var(--aba-blue); }
        .trait-tag { background: #edf2f5; color: var(--aba-gray); }
        .skill-tag { background: #e8eef2; color: #364e5e; }
        .entry-snapshot { background: linear-gradient(135deg, #e8f3f8, #f7fafc); }
        .source-link { color: #9b6b08; }
        .lead, .career-path-box, .entry-snapshot p, .disclosure-body p, .example-card li, .interview-list li { font-family: var(--aba-serif); }
        @media (max-width: 767.98px) { .fact-grid { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="/"><img class="brand-logo" src="/banking-future-logo.svg" alt="" width="42" height="42"><span class="brand-copy"><span class="brand-title">Banking on the <span class="brand-highlight">Future</span></span><span class="brand-attribution">American Bankers Association</span></span></a>
            <div class="nav-actions">
                <a class="nav-button nav-home" href="/">Home</a>
                <a class="nav-button nav-match" href="/match">Match</a>
                <a class="nav-button nav-match" href="/resume">Resume Review</a>
                <a class="nav-button nav-favorites" href="/favorites">Favorites (<span data-favorite-count>0</span>)</a>
            </div>
        </div>
    </nav>
    
    <div class="container mt-4 flex-grow-1">
        <nav aria-label="breadcrumb">
            <ol class="breadcrumb">
                <li class="breadcrumb-item"><a href="/">Home</a></li>
                <li class="breadcrumb-item active">{{ job.name }}</li>
            </ol>
        </nav>
        
        <div class="card detail-card p-4">
            <div class="row">
                <div class="col-md-8">
                    <h1 class="display-6 fw-bold">{{ job.name }}</h1>
                    <h5 class="text-muted">{{ job.department }}</h5>
                    <hr>
                    <h5>Job Description</h5>
                    <p class="lead">{{ job.description }}</p>
                    
                    <div class="row mt-4">
                        <div class="col-md-6">
                            <h6>Salary Range</h6>
                            <span class="detail-pill salary-detail">{{ job.salary }}</span>
                        </div>
                        <div class="col-md-6">
                            <h6>Suitable Grade</h6>
                            <span class="detail-pill level-detail">{% if 'depending on level' in job.suitable_grade %}Multiple experience levels{% else %}{{ job.suitable_grade }}{% endif %}</span>
                        </div>
                    </div>

                    <div class="fact-grid">
                        {% if job.job_family %}<div class="fact-card"><span class="fact-label">Job Family</span><span class="fact-value">{{ job.job_family }}</span></div>{% endif %}
                        {% if job.function %}<div class="fact-card"><span class="fact-label">Function</span><span class="fact-value">{{ job.function }}</span></div>{% endif %}
                        {% if job.office %}<div class="fact-card"><span class="fact-label">Organizational Area</span><span class="fact-value">{{ job.office }}</span></div>{% endif %}
                        {% if job.salary_basis %}<div class="fact-card"><span class="fact-label">Salary Basis</span><span class="fact-value">{{ job.salary_basis }}{% if job.salary_as_of %} · {{ job.salary_as_of }}{% endif %}</span></div>{% endif %}
                    </div>
                </div>
                
                <div class="col-md-4">
                    <div class="bg-light p-3 rounded">
                        <h6>Recommended Majors</h6>
                        <div class="tag-wrap">
                            {% for major in job.suitable_major %}
                                {% if major[:7] == 'Varies;' %}
                                <div class="open-major-note">Open to many majors. Relevant coursework, skills, internships, and licenses may matter more than a specific major.</div>
                                {% else %}
                                <span class="detail-tag major-tag">{{ major }}</span>
                                {% endif %}
                            {% endfor %}
                        </div>
                        
                        <h6 class="mt-3">Ideal Personality Traits</h6>
                        <div class="tag-wrap">{% for trait in job.personality %}<span class="detail-tag trait-tag">{{ trait }}</span>{% endfor %}</div>
                        
                        <h6 class="mt-3">Key Skills</h6>
                        <div class="tag-wrap">{% for skill in job.skills %}<span class="detail-tag skill-tag">{{ skill }}</span>{% endfor %}</div>

                        {% if job.aliases %}
                        <h6 class="mt-3">Also Known As</h6>
                        <div class="tag-wrap">{% for alias in job.aliases %}<span class="detail-tag skill-tag">{{ alias }}</span>{% endfor %}</div>
                        {% endif %}
                    </div>
                </div>
            </div>

            {% if job.entry_level or job.entry_level_availability or job.entry_level_title_examples %}
            <section class="entry-snapshot">
                <h5>Entry-Level Snapshot</h5>
                {% if job.entry_level %}<p><strong>Availability:</strong> {{ job.entry_level }}</p>{% endif %}
                {% if job.entry_level_availability %}<p>{{ job.entry_level_availability }}</p>{% endif %}
                {% if job.entry_level_title_examples %}
                <div class="tag-wrap">{% for title in job.entry_level_title_examples %}<span class="detail-tag major-tag">{{ title }}</span>{% endfor %}</div>
                {% endif %}
            </section>
            {% endif %}

            {% if job.career_path %}
            <div class="career-details">
                <h5>Career Path</h5>
                <div class="career-path-box">{{ job.career_path }}</div>
            </div>
            {% endif %}

            {% if job.interview_questions %}
            <details class="info-disclosure">
                <summary>Practice Interview Questions ({{ job.interview_questions|length }})</summary>
                <div class="disclosure-body"><ol class="interview-list">{% for question in job.interview_questions %}<li>{{ question }}</li>{% endfor %}</ol></div>
            </details>
            {% endif %}

            {% if job.bank_types %}
            <details class="info-disclosure">
                <summary>Where This Role May Be Found</summary>
                <div class="disclosure-body">
                    <div class="tag-wrap">{% for bank_type in job.bank_types %}<span class="detail-tag skill-tag">{{ bank_type }}</span>{% endfor %}</div>
                    {% if job.bank_type_note %}<p class="text-muted small mt-3 mb-0">{{ job.bank_type_note }}</p>{% endif %}
                </div>
            </details>
            {% endif %}

            {% if job.real_job_examples %}
            <details class="info-disclosure">
                <summary>Official Employer Examples ({{ job.real_job_examples|length }})</summary>
                <div class="disclosure-body">
                    {% for example in job.real_job_examples %}
                    <article class="example-card">
                        <h6 class="mb-1">{{ example.example_title }}</h6>
                        <p class="text-muted small mb-2">{{ example.company }}</p>
                        {% if example.match_quality %}<p class="small mb-2"><strong>Example match:</strong> {{ example.match_quality }}</p>{% endif %}
                        {% set responsibilities = example.responsibility_summary or example.responsibilities %}
                        {% set requirements = example.representative_requirements or example.requirements %}
                        {% set verification = example.verification_note or example.fit_note %}
                        {% set source_url = example.source_url or example.url %}
                        {% if responsibilities %}<strong class="small">Example responsibilities</strong><ul>{% for item in responsibilities %}<li>{{ item }}</li>{% endfor %}</ul>{% endif %}
                        {% if requirements %}<strong class="small">Representative qualifications</strong><ul>{% for item in requirements %}<li>{{ item }}</li>{% endfor %}</ul>{% endif %}
                        {% if verification %}<p class="text-muted small">{{ verification }}</p>{% endif %}
                        {% if example.source_type or example.accessed %}<p class="text-muted small mb-2">{% if example.source_type %}{{ example.source_type }}{% endif %}{% if example.source_type and example.accessed %} · {% endif %}{% if example.accessed %}Reviewed {{ example.accessed }}{% endif %}</p>{% endif %}
                        {% if source_url %}<a class="source-link" href="{{ source_url }}" target="_blank" rel="noopener noreferrer">View official employer source ↗</a>{% endif %}
                    </article>
                    {% endfor %}
                </div>
            </details>
            {% endif %}

            {% if job.scope_note %}
            <details class="info-disclosure">
                <summary>Important Role and Salary Notes</summary>
                <div class="disclosure-body">
                    <p class="mb-2">{{ job.scope_note }}</p>
                    {% if job.salary_geography %}<p class="mb-2"><strong>Salary geography:</strong> {{ job.salary_geography }}</p>{% endif %}
                    {% if job.compensation_note %}<p class="text-muted small mb-0">{{ job.compensation_note }}</p>{% endif %}
                </div>
            </details>
            {% endif %}
        </div>
        
        <div class="mt-4">
            <button type="button" class="btn favorite-button" data-favorite-button data-job-id="{{ job.id }}" aria-pressed="false">Save Job</button>
            <a href="/match" class="btn btn-match">Find Similar Roles</a>
            <a href="/" class="btn btn-outline-dark">Back to All Jobs</a>
        </div>
    </div>
    
    <div class="footer">
        <div class="container text-center">
            <p class="mb-0">🏦 Banking on the Future © 2026</p>
        </div>
    </div>
    {{ favorite_script | safe }}
</body>
</html>
'''

# %%
match_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Career Match - Banking on the Future</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&display=swap" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(rgba(245, 247, 250, 0.82), rgba(245, 247, 250, 0.82)), url('/background1.jpg') center / cover fixed no-repeat;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .navbar { background: #0a1628 !important; }
        .navbar-brand { color: #ffffff !important; font-family: 'Cormorant Garamond', Georgia, serif; font-size: 1.65rem; font-weight: 700; letter-spacing: 0.015em; line-height: 1; display: inline-flex; align-items: center; gap: 11px; }
        .brand-icon { display: inline-grid; place-items: center; width: 38px; height: 38px; border: 1px solid rgba(248, 200, 66, 0.72); border-radius: 10px; background: linear-gradient(145deg, rgba(248, 200, 66, 0.2), rgba(248, 200, 66, 0.05)); box-shadow: inset 0 0 0 1px rgba(255,255,255,0.05); font-size: 1.05rem; }
        .brand-highlight { color: #f8c842; font-weight: 600; }
        .brand-logo { display: block; width: 42px; height: 42px; flex: 0 0 auto; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.14); }
        .brand-copy { display: flex; flex-direction: column; gap: 4px; }
        .brand-title { line-height: 0.9; }
        .brand-attribution { color: rgba(255,255,255,0.72); font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; font-size: 0.56rem; font-weight: 700; letter-spacing: 0.12em; line-height: 1; text-transform: uppercase; }
        .nav-actions { display: flex; flex-wrap: wrap; justify-content: flex-end; gap: 10px; }
        .nav-button { padding: 8px 18px; border: 1px solid transparent; border-radius: 999px; font-weight: 600; text-decoration: none; transition: background-color 0.2s, color 0.2s, transform 0.2s; }
        .nav-button:hover { transform: translateY(-1px); }
        .nav-button:focus-visible { outline: none; box-shadow: 0 0 0 3px rgba(248, 200, 66, 0.4); }
        .nav-home { color: white; border-color: rgba(255,255,255,0.7); }
        .nav-home:hover { color: #0a1628; background: white; }
        .nav-favorites { color: white; border-color: rgba(255,255,255,0.7); }
        .nav-favorites:hover { color: #0a1628; background: white; }
        .nav-match { color: #0a1628; background: #f8c842; border-color: #f8c842; }
        .nav-match:hover { color: #0a1628; background: #e6b83a; border-color: #e6b83a; }
        .btn-match { background: #f8c842; color: #0a1628; font-weight: 600; border: none; padding: 12px 30px; border-radius: 30px; }
        .btn-match:hover { background: #e6b83a; }
        .quiz-shell { overflow: hidden; border: 1px solid rgba(10,22,40,0.1); border-radius: 24px; background: rgba(255,255,255,0.97); box-shadow: 0 18px 50px rgba(10,22,40,0.14); }
        .quiz-header { padding: 1.6rem 2rem 1.25rem; background: linear-gradient(135deg, #0a1628, #1a2a4a); color: white; }
        .quiz-eyebrow { margin-bottom: 0.45rem; color: #f8c842; font-size: 0.76rem; font-weight: 800; letter-spacing: 0.13em; text-transform: uppercase; }
        .quiz-header h1 { margin: 0; font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; font-size: clamp(1.55rem, 4vw, 2.15rem); font-weight: 700; }
        .quiz-intro { max-width: 620px; margin: 0.7rem 0 0; color: rgba(255,255,255,0.78); }
        .quiz-progress-meta { display: flex; justify-content: space-between; gap: 1rem; margin-top: 1.35rem; color: rgba(255,255,255,0.76); font-size: 0.83rem; }
        .quiz-progress { overflow: hidden; height: 7px; margin-top: 0.45rem; border-radius: 999px; background: rgba(255,255,255,0.14); }
        .quiz-progress-bar { width: 12.5%; height: 100%; border-radius: inherit; background: linear-gradient(90deg, #f8c842, #ffe68b); transition: width 0.35s ease; }
        .quiz-form { padding: clamp(1.4rem, 4vw, 2.4rem); }
        .quiz-step { padding: 0.25rem; }
        .quiz-enhanced .quiz-step { display: none; }
        .quiz-enhanced .quiz-step.is-active { display: block; animation: quizFade 0.28s ease; }
        @keyframes quizFade { from { opacity: 0; transform: translateX(12px); } to { opacity: 1; transform: translateX(0); } }
        .quiz-question-number { color: #a47e00; font-size: 0.78rem; font-weight: 800; letter-spacing: 0.1em; text-transform: uppercase; }
        .quiz-question { margin: 0.45rem 0 0.45rem; color: #0a1628; font-size: clamp(1.35rem, 3vw, 1.85rem); font-weight: 750; }
        .quiz-helper { margin-bottom: 1.4rem; color: #687386; }
        .quiz-select { min-height: 58px; border: 2px solid #dce3ec; border-radius: 14px; padding: 0.85rem 1rem; font-size: 1rem; }
        .quiz-select:focus { border-color: #d4a900; box-shadow: 0 0 0 4px rgba(248,200,66,0.22); }
        .answer-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0.85rem; }
        .answer-option { position: relative; }
        .answer-option input { position: absolute; opacity: 0; pointer-events: none; }
        .answer-card { display: flex; align-items: flex-start; gap: 0.85rem; height: 100%; min-height: 92px; padding: 1rem; border: 2px solid #e1e6ed; border-radius: 15px; background: #fff; cursor: pointer; transition: border-color 0.18s, background-color 0.18s, transform 0.18s, box-shadow 0.18s; }
        .answer-card:hover { border-color: #d4b13c; transform: translateY(-2px); box-shadow: 0 8px 20px rgba(10,22,40,0.08); }
        .answer-option input:focus-visible + .answer-card { box-shadow: 0 0 0 4px rgba(248,200,66,0.32); }
        .answer-option input:checked + .answer-card { border-color: #d4a900; background: #fff9df; box-shadow: 0 8px 22px rgba(164,126,0,0.13); }
        .answer-icon { display: grid; flex: 0 0 38px; place-items: center; width: 38px; height: 38px; border-radius: 11px; background: #eef2f7; font-size: 1.1rem; }
        .answer-option input:checked + .answer-card .answer-icon { background: #f8c842; }
        .answer-title { display: block; color: #0a1628; font-weight: 750; line-height: 1.25; }
        .answer-detail { display: block; margin-top: 0.3rem; color: #6a7483; font-size: 0.83rem; line-height: 1.35; }
        .quiz-actions { display: flex; justify-content: space-between; gap: 1rem; margin-top: 1.75rem; }
        .quiz-back { border: 1px solid #ccd4df; border-radius: 999px; padding: 0.7rem 1.35rem; background: white; color: #344054; font-weight: 700; }
        .quiz-next { margin-left: auto; border: 0; border-radius: 999px; padding: 0.75rem 1.5rem; background: #0a1628; color: white; font-weight: 750; }
        .quiz-next:hover { background: #172b49; }
        .quiz-submit { background: #f8c842; color: #0a1628; }
        .quiz-submit:hover { background: #e6b83a; }
        .match-card { border-left: 5px solid #f8c842; background: white; }
        .match-card h5, .match-card p { overflow-wrap: anywhere; }
        .match-salary { display: inline-block; max-width: 100%; padding: 0.38rem 0.58rem; border-radius: 8px; background: #e2f3e8; color: #17633a; font-size: 0.76rem; font-weight: 700; line-height: 1.3; white-space: normal; overflow-wrap: anywhere; }
        .favorite-button { border-color: #d4a900; color: #725b00; font-weight: 600; }
        .favorite-button:hover, .favorite-button.is-favorite { background: #f8c842; border-color: #f8c842; color: #0a1628; }
        .footer { background: #0a1628; color: white; padding: 20px 0; margin-top: 40px; border-radius: 20px 20px 0 0; }
        :root { --aba-blue: #005a8c; --aba-gray: #58595b; --aba-gold: #dc9f1d; --aba-slate: #4e7c9c; --aba-sans: "Helvetica Neue", Helvetica, Arial, sans-serif; --aba-serif: "Minion Pro", "Times New Roman", Times, serif; }
        body { color: var(--aba-gray); font-family: var(--aba-sans); }
        .navbar, .footer { background: var(--aba-blue) !important; }
        .brand-highlight, .quiz-eyebrow { color: var(--aba-gold); }
        .brand-icon { border-color: rgba(220,159,29,0.75); background: rgba(220,159,29,0.14); }
        .nav-button:focus-visible { box-shadow: 0 0 0 3px rgba(220,159,29,0.35); }
        .nav-home:hover, .nav-favorites:hover { color: var(--aba-blue); }
        .nav-match, .btn-match { background: var(--aba-gold); border-color: var(--aba-gold); color: #ffffff; }
        .nav-match:hover, .btn-match:hover { background: #bd8413; border-color: #bd8413; color: #ffffff; }
        .quiz-header { background: linear-gradient(135deg, var(--aba-blue), var(--aba-slate)); }
        .quiz-progress-bar { background: linear-gradient(90deg, var(--aba-gold), #efc55e); }
        .quiz-question, .answer-title { color: var(--aba-blue); }
        .quiz-select:focus { border-color: var(--aba-gold); box-shadow: 0 0 0 4px rgba(220,159,29,0.2); }
        .answer-card:hover, .answer-option input:checked + .answer-card { border-color: var(--aba-gold); }
        .answer-option input:checked + .answer-card { background: #fff7e4; }
        .answer-option input:checked + .answer-card .answer-icon { background: var(--aba-gold); color: #ffffff; }
        .quiz-next { background: var(--aba-blue); }
        .quiz-next:hover { background: #00476f; }
        .quiz-submit { background: var(--aba-gold); color: #ffffff; }
        .quiz-submit:hover { background: #bd8413; }
        .match-card { border-left-color: var(--aba-gold); }
        .favorite-button { border-color: var(--aba-gold); color: #765300; }
        .favorite-button:hover, .favorite-button.is-favorite { background: var(--aba-gold); border-color: var(--aba-gold); color: #ffffff; }
        .quiz-intro, .quiz-helper, .answer-detail, .match-card p { font-family: var(--aba-serif); }
        @media (max-width: 767.98px) {
            .answer-grid { grid-template-columns: 1fr; }
            .quiz-header { padding: 1.4rem; }
            .quiz-form { padding: 1.2rem; }
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="/"><img class="brand-logo" src="/banking-future-logo.svg" alt="" width="42" height="42"><span class="brand-copy"><span class="brand-title">Banking on the <span class="brand-highlight">Future</span></span><span class="brand-attribution">American Bankers Association</span></span></a>
            <div class="nav-actions">
                <a class="nav-button nav-home" href="/">Home</a>
                <a class="nav-button nav-match" href="/match">Match</a>
                <a class="nav-button nav-match" href="/resume">Resume Review</a>
                <a class="nav-button nav-favorites" href="/favorites">Favorites (<span data-favorite-count>0</span>)</a>
            </div>
        </div>
    </nav>
    
    <div class="container mt-4 flex-grow-1">
        <div class="row">
            <div class="col-lg-8 mx-auto">
                {% if not results %}
                <div class="quiz-shell" id="careerQuiz">
                    <div class="quiz-header">
                        <div class="quiz-eyebrow">Career personality quiz</div>
                        <h1>Let’s find your place in banking</h1>
                        <p class="quiz-intro">Hi! I’ll ask eight quick questions about your background, interests, and how you like to work. There are no wrong answers.</p>
                        <div class="quiz-progress-meta">
                            <span id="quizStepLabel">Question 1 of 8</span>
                            <span>About 3 minutes</span>
                        </div>
                        <div class="quiz-progress" aria-hidden="true"><div class="quiz-progress-bar" id="quizProgressBar"></div></div>
                    </div>

                    <form method="POST" action="/match" class="quiz-form" id="careerQuizForm">
                        <section class="quiz-step is-active" data-quiz-step>
                            <div class="quiz-question-number">First, your background</div>
                            <h2 class="quiz-question">What are you studying—or what did you study?</h2>
                            <p class="quiz-helper">Not a finance major? Perfectly fine. Banks also need people in technology, communications, psychology, law, sustainability, and much more.</p>
                            <label class="visually-hidden" for="majorSelect">Your major</label>
                            <select id="majorSelect" name="major" class="form-select quiz-select" required>
                                <option value="">Choose your major...</option>
                                {% for major in all_majors %}
                                <option value="{{ major }}" {% if selected_major == major %}selected{% endif %}>{{ major }}</option>
                                {% endfor %}
                            </select>
                            <div class="quiz-actions">
                                <button type="button" class="quiz-next" data-quiz-next>Continue →</button>
                            </div>
                        </section>

                        <section class="quiz-step" data-quiz-step>
                            <div class="quiz-question-number">Where you are now</div>
                            <h2 class="quiz-question">Which stage best describes you?</h2>
                            <p class="quiz-helper">This helps us recommend roles with the right experience level.</p>
                            <div class="answer-grid">
                                {% set grade_options = [
                                    ('Undergraduate (Years 1-2)', '🌱', 'Undergraduate: years 1–2', 'I am beginning college and exploring possible career paths.'),
                                    ('Undergraduate (Years 3-4)', '🧭', 'Undergraduate: years 3–4', 'I am preparing for internships or my first full-time role.'),
                                    ('Graduate Student', '📚', 'Graduate student', 'I am currently pursuing a master’s, MBA, JD, PhD, or similar degree.'),
                                    ('Recent Graduate (0-1 years)', '🎓', 'Recent graduate', 'I graduated within the past year and am entering the workforce.'),
                                    ('Early Career Professional (1-3 years)', '🚀', 'Early-career professional', 'I have between one and three years of work experience.'),
                                    ('Experienced Professional (3+ years)', '🏆', 'Experienced professional', 'I have more than three years of professional experience.')
                                ] %}
                                {% for value, icon, title, detail in grade_options %}
                                <div class="answer-option">
                                    <input type="radio" name="grade" value="{{ value }}" id="grade_{{ loop.index }}" {% if selected_grade == value %}checked{% endif %} required>
                                    <label class="answer-card" for="grade_{{ loop.index }}"><span class="answer-icon">{{ icon }}</span><span><span class="answer-title">{{ title }}</span><span class="answer-detail">{{ detail }}</span></span></label>
                                </div>
                                {% endfor %}
                            </div>
                            <div class="quiz-actions"><button type="button" class="quiz-back" data-quiz-back>← Back</button><button type="button" class="quiz-next" data-quiz-next>Continue →</button></div>
                        </section>

                        <section class="quiz-step" data-quiz-step>
                            <div class="quiz-question-number">How you like to work</div>
                            <h2 class="quiz-question">Which kind of workday sounds most satisfying?</h2>
                            <p class="quiz-helper">Choose the one that feels most naturally like you.</p>
                            <div class="answer-grid">
                                {% set workday_options = [
                                    ('Analytical', '🧩', 'Cracking a complex puzzle', 'I enjoy patterns, numbers, evidence, and finding the answer.'),
                                    ('Client-focused', '🤝', 'Helping someone reach a goal', 'I like listening, building trust, and creating a solution.'),
                                    ('Organized', '⚙️', 'Making everything run smoothly', 'I enjoy creating order, improving a process, and staying on top of details.'),
                                    ('Creative', '💡', 'Turning a new idea into something real', 'I like imagining better experiences, products, or ways of working.')
                                ] %}
                                {% for value, icon, title, detail in workday_options %}
                                <div class="answer-option">
                                    <input type="radio" name="personality_q1" value="{{ value }}" id="workday_{{ loop.index }}" {% if value in selected_personality %}checked{% endif %} required>
                                    <label class="answer-card" for="workday_{{ loop.index }}"><span class="answer-icon">{{ icon }}</span><span><span class="answer-title">{{ title }}</span><span class="answer-detail">{{ detail }}</span></span></label>
                                </div>
                                {% endfor %}
                            </div>
                            <div class="quiz-actions"><button type="button" class="quiz-back" data-quiz-back>← Back</button><button type="button" class="quiz-next" data-quiz-next>Continue →</button></div>
                        </section>

                        <section class="quiz-step" data-quiz-step>
                            <div class="quiz-question-number">Your natural strength</div>
                            <h2 class="quiz-question">What do people tend to count on you for?</h2>
                            <p class="quiz-helper">Think about what classmates, teammates, or coworkers ask you to bring to the table.</p>
                            <div class="answer-grid">
                                {% set strength_options = [
                                    ('Calm under pressure', '🧊', 'Keeping a clear head', 'I stay composed when the stakes or pace increase.'),
                                    ('Ethical', '⚖️', 'Doing the right thing', 'I notice risks, protect trust, and speak up when something feels wrong.'),
                                    ('Meticulous', '🔎', 'Catching what others miss', 'I care about accuracy, quality, and getting the details right.'),
                                    ('Collaborative', '🧠', 'Bringing people together', 'I help different personalities and perspectives work as a team.')
                                ] %}
                                {% for value, icon, title, detail in strength_options %}
                                <div class="answer-option">
                                    <input type="radio" name="personality_q2" value="{{ value }}" id="strength_{{ loop.index }}" {% if value in selected_personality %}checked{% endif %} required>
                                    <label class="answer-card" for="strength_{{ loop.index }}"><span class="answer-icon">{{ icon }}</span><span><span class="answer-title">{{ title }}</span><span class="answer-detail">{{ detail }}</span></span></label>
                                </div>
                                {% endfor %}
                            </div>
                            <div class="quiz-actions"><button type="button" class="quiz-back" data-quiz-back>← Back</button><button type="button" class="quiz-next" data-quiz-next>Continue →</button></div>
                        </section>

                        <section class="quiz-step" data-quiz-step>
                            <div class="quiz-question-number">Your ideal environment</div>
                            <h2 class="quiz-question">Where do you feel most energized?</h2>
                            <p class="quiz-helper">Go with your first instinct.</p>
                            <div class="answer-grid">
                                {% set environment_options = [
                                    ('Ambitious', '🏁', 'A fast-moving challenge', 'Clear goals, healthy competition, and visible results motivate me.'),
                                    ('Independent', '🎯', 'Space to own my work', 'I like focused responsibility and the freedom to find my approach.'),
                                    ('Team-player', '🌐', 'A connected team', 'I gain energy from shared goals and working closely with others.'),
                                    ('Curious', '🔭', 'A place where I keep learning', 'New subjects, changing problems, and discovery keep me engaged.')
                                ] %}
                                {% for value, icon, title, detail in environment_options %}
                                <div class="answer-option">
                                    <input type="radio" name="personality_q3" value="{{ value }}" id="environment_{{ loop.index }}" {% if value in selected_personality %}checked{% endif %} required>
                                    <label class="answer-card" for="environment_{{ loop.index }}"><span class="answer-icon">{{ icon }}</span><span><span class="answer-title">{{ title }}</span><span class="answer-detail">{{ detail }}</span></span></label>
                                </div>
                                {% endfor %}
                            </div>
                            <div class="quiz-actions"><button type="button" class="quiz-back" data-quiz-back>← Back</button><button type="button" class="quiz-next" data-quiz-next>Continue →</button></div>
                        </section>

                        <section class="quiz-step" data-quiz-step>
                            <div class="quiz-question-number">Problems that interest you</div>
                            <h2 class="quiz-question">Which challenge would you most want to take on?</h2>
                            <p class="quiz-helper">This helps us distinguish among business, technology, analytical, and control-oriented roles.</p>
                            <div class="answer-grid">
                                {% set challenge_options = [
                                    ('Risk-aware', '🛡️', 'Spot and prevent problems', 'I would protect customers and the bank by identifying risk early.'),
                                    ('User-centric', '📱', 'Build a better digital experience', 'I would make banking tools simpler and more useful for people.'),
                                    ('Quantitative', '📊', 'Find the story inside the numbers', 'I would use data and models to explain what is happening.'),
                                    ('Strategic', '♟️', 'Decide where the business should go', 'I would connect market trends, customer needs, and long-term goals.')
                                ] %}
                                {% for value, icon, title, detail in challenge_options %}
                                <div class="answer-option">
                                    <input type="radio" name="personality_q4" value="{{ value }}" id="challenge_{{ loop.index }}" {% if value in selected_personality %}checked{% endif %} required>
                                    <label class="answer-card" for="challenge_{{ loop.index }}"><span class="answer-icon">{{ icon }}</span><span><span class="answer-title">{{ title }}</span><span class="answer-detail">{{ detail }}</span></span></label>
                                </div>
                                {% endfor %}
                            </div>
                            <div class="quiz-actions"><button type="button" class="quiz-back" data-quiz-back>← Back</button><button type="button" class="quiz-next" data-quiz-next>Continue →</button></div>
                        </section>

                        <section class="quiz-step" data-quiz-step>
                            <div class="quiz-question-number">Your working rhythm</div>
                            <h2 class="quiz-question">How do you prefer to approach a new assignment?</h2>
                            <p class="quiz-helper">Choose the approach that you would naturally take first.</p>
                            <div class="answer-grid">
                                {% set approach_options = [
                                    ('Process-oriented', '🗂️', 'Create a clear plan', 'I define the steps, timeline, and checks before moving ahead.'),
                                    ('Resilient', '🌊', 'Jump in and adapt', 'I am comfortable learning as conditions and priorities change.'),
                                    ('Judicious', '🧭', 'Study the tradeoffs', 'I gather context and use careful judgment before deciding.'),
                                    ('Outgoing', '💬', 'Talk with the people involved', 'I build momentum by asking questions and connecting with others.')
                                ] %}
                                {% for value, icon, title, detail in approach_options %}
                                <div class="answer-option">
                                    <input type="radio" name="personality_q5" value="{{ value }}" id="approach_{{ loop.index }}" {% if value in selected_personality %}checked{% endif %} required>
                                    <label class="answer-card" for="approach_{{ loop.index }}"><span class="answer-icon">{{ icon }}</span><span><span class="answer-title">{{ title }}</span><span class="answer-detail">{{ detail }}</span></span></label>
                                </div>
                                {% endfor %}
                            </div>
                            <div class="quiz-actions"><button type="button" class="quiz-back" data-quiz-back>← Back</button><button type="button" class="quiz-next" data-quiz-next>Continue →</button></div>
                        </section>

                        <section class="quiz-step" data-quiz-step>
                            <div class="quiz-question-number">What motivates you</div>
                            <h2 class="quiz-question">At the end of a great project, what would make you proudest?</h2>
                            <p class="quiz-helper">One last choice, then we’ll reveal your matches.</p>
                            <div class="answer-grid">
                                {% set impact_options = [
                                    ('Helpful', '🙌', 'I made someone’s life easier', 'My work had a practical, positive effect on a customer or teammate.'),
                                    ('Leadership-oriented', '🚩', 'I helped people succeed together', 'I created direction and brought out the best in a group.'),
                                    ('Precise', '✅', 'The result was exceptionally accurate', 'The work was dependable, complete, and built to a high standard.'),
                                    ('Forward-thinking', '🌟', 'I helped create what comes next', 'The project introduced an idea or capability that moves banking forward.')
                                ] %}
                                {% for value, icon, title, detail in impact_options %}
                                <div class="answer-option">
                                    <input type="radio" name="personality_q6" value="{{ value }}" id="impact_{{ loop.index }}" {% if value in selected_personality %}checked{% endif %} required>
                                    <label class="answer-card" for="impact_{{ loop.index }}"><span class="answer-icon">{{ icon }}</span><span><span class="answer-title">{{ title }}</span><span class="answer-detail">{{ detail }}</span></span></label>
                                </div>
                                {% endfor %}
                            </div>
                            <div class="quiz-actions"><button type="button" class="quiz-back" data-quiz-back>← Back</button><button type="submit" class="quiz-next quiz-submit">Reveal My Matches ✨</button></div>
                        </section>
                    </form>
                </div>
                {% endif %}
                
                {% if results %}
                <div class="mt-4">
                    <h3 class="text-center">Your Top Matches</h3>
                    <p class="text-center text-muted">Based on your background and how you naturally like to work.</p>
                    <div class="text-center mb-4"><a href="/match" class="btn btn-outline-dark rounded-pill">Retake the quiz</a></div>
                    {% for job in results %}
                    <div class="card match-card p-3 mb-3">
                        <div class="row align-items-center">
                            <div class="col-md-8">
                                <h5>
                                    <a href="/job/{{ job.id }}" class="text-decoration-none text-dark">{{ job.name }}</a>
                                </h5>
                                <p class="text-muted small mb-0">{{ job.department }}</p>
                            </div>
                            <div class="col-md-4 text-end">
                                <div class="mb-1">
                                    <span class="match-salary">{{ job.salary }}</span>
                                </div>
                                <div class="mb-2">
                                    <span class="badge bg-warning text-dark">
                                        {{ "%.0f"|format(job.match_score) }}% Match
                                    </span>
                                </div>
                                <a href="/job/{{ job.id }}" class="btn btn-outline-dark btn-sm">View Details</a>
                                <button type="button" class="btn favorite-button btn-sm" data-favorite-button data-job-id="{{ job.id }}" aria-pressed="false">Save Job</button>
                            </div>
                        </div>
                    </div>
                    {% endfor %}
                </div>
                {% endif %}

                {% if results %}
                <div class="mt-5">
                    <div class="card p-4" style="background: #f0f7ff; border-left: 5px solid #f8c842;">
                        <h3 class="mb-3">💡 Get Personalized Advice</h3>
                        <p class="text-muted mb-4">Ask follow-up questions about your profile, skills, career path, or these roles.</p>
                        <form id="advisorForm" method="POST" action="/match" class="mb-4">
                            <input type="hidden" name="major" value="{{ selected_major }}">
                            <input type="hidden" name="grade" value="{{ selected_grade }}">
                            {% for trait in selected_personality %}
                            <input type="hidden" name="personality" value="{{ trait }}">
                            {% endfor %}
                            <textarea name="question" class="form-control mb-3" rows="3" placeholder="E.g., What skills should I focus on? How can I prepare for these roles? What's the career path like?" required></textarea>
                            <button type="submit" class="btn btn-match" name="get_advice" value="true">Ask Advisor</button>
                        </form>
                        {% if advice %}
                        <div class="mt-4">
                            <h5>Advisor Response:</h5>
                            <div style="background: white; padding: 20px; border-radius: 8px; border-left: 4px solid #f8c842;">
                                <pre style="white-space: pre-wrap; font-family: inherit; background: transparent; border: none; margin: 0; color: #0a1628; line-height: 1.6;">{{ advice }}</pre>
                            </div>
                        </div>
                        {% endif %}
                    </div>
                </div>
                {% endif %}
            </div>
        </div>
    </div>
    
    <div class="footer">
        <div class="container text-center">
            <p class="mb-0">🏦 Banking on the Future © 2026</p>
        </div>
    </div>
    <script>
        (() => {
            const quiz = document.getElementById('careerQuiz');
            if (!quiz) return;

            quiz.classList.add('quiz-enhanced');
            const form = document.getElementById('careerQuizForm');
            const steps = Array.from(quiz.querySelectorAll('[data-quiz-step]'));
            const progressBar = document.getElementById('quizProgressBar');
            const stepLabel = document.getElementById('quizStepLabel');
            let currentStep = 0;

            const showStep = (index, moveFocus = true) => {
                currentStep = Math.max(0, Math.min(index, steps.length - 1));
                steps.forEach((step, stepIndex) => step.classList.toggle('is-active', stepIndex === currentStep));
                progressBar.style.width = `${((currentStep + 1) / steps.length) * 100}%`;
                stepLabel.textContent = `Question ${currentStep + 1} of ${steps.length}`;
                if (moveFocus) {
                    const question = steps[currentStep].querySelector('.quiz-question');
                    question.setAttribute('tabindex', '-1');
                    question.focus({ preventScroll: true });
                    quiz.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            };

            const currentStepIsValid = () => {
                const requiredFields = Array.from(steps[currentStep].querySelectorAll('[required]'));
                const checkedGroups = new Set();
                for (const field of requiredFields) {
                    if (field.type === 'radio') {
                        if (checkedGroups.has(field.name)) continue;
                        checkedGroups.add(field.name);
                        const choice = steps[currentStep].querySelector(`input[name="${field.name}"]:checked`);
                        if (!choice) {
                            field.reportValidity();
                            return false;
                        }
                    } else if (!field.checkValidity()) {
                        field.reportValidity();
                        return false;
                    }
                }
                return true;
            };

            quiz.querySelectorAll('[data-quiz-next]').forEach(button => {
                button.addEventListener('click', () => {
                    if (currentStepIsValid()) showStep(currentStep + 1);
                });
            });
            quiz.querySelectorAll('[data-quiz-back]').forEach(button => {
                button.addEventListener('click', () => showStep(currentStep - 1));
            });
            form.addEventListener('keydown', event => {
                if (event.key === 'Enter' && currentStep < steps.length - 1 && event.target.tagName !== 'BUTTON') {
                    event.preventDefault();
                    if (currentStepIsValid()) showStep(currentStep + 1);
                }
            });

            showStep(0, false);
        })();
    </script>
    {{ favorite_script | safe }}
</body>
</html>
'''

# %%
resume_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Resume Review - Banking on the Future</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&display=swap" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(rgba(245, 247, 250, 0.82), rgba(245, 247, 250, 0.82)), url('/background1.jpg') center / cover fixed no-repeat;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .navbar { background: #0a1628 !important; }
        .navbar-brand { color: #ffffff !important; font-family: 'Cormorant Garamond', Georgia, serif; font-size: 1.65rem; font-weight: 700; letter-spacing: 0.015em; line-height: 1; display: inline-flex; align-items: center; gap: 11px; }
        .brand-icon { display: inline-grid; place-items: center; width: 38px; height: 38px; border: 1px solid rgba(248, 200, 66, 0.72); border-radius: 10px; background: linear-gradient(145deg, rgba(248, 200, 66, 0.2), rgba(248, 200, 66, 0.05)); box-shadow: inset 0 0 0 1px rgba(255,255,255,0.05); font-size: 1.05rem; }
        .brand-highlight { color: #f8c842; font-weight: 600; }
        .brand-logo { display: block; width: 42px; height: 42px; flex: 0 0 auto; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.14); }
        .brand-copy { display: flex; flex-direction: column; gap: 4px; }
        .brand-title { line-height: 0.9; }
        .brand-attribution { color: rgba(255,255,255,0.72); font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; font-size: 0.56rem; font-weight: 700; letter-spacing: 0.12em; line-height: 1; text-transform: uppercase; }
        .nav-actions { display: flex; flex-wrap: wrap; justify-content: flex-end; gap: 10px; }
        .nav-button { padding: 8px 18px; border: 1px solid transparent; border-radius: 999px; font-weight: 600; text-decoration: none; transition: background-color 0.2s, color 0.2s, transform 0.2s; }
        .nav-button:hover { transform: translateY(-1px); }
        .nav-button:focus-visible { outline: none; box-shadow: 0 0 0 3px rgba(248, 200, 66, 0.4); }
        .nav-home, .nav-favorites { color: white; border-color: rgba(255,255,255,0.7); }
        .nav-home:hover, .nav-favorites:hover { color: #0a1628; background: white; }
        .nav-match { color: #0a1628; background: #f8c842; border-color: #f8c842; }
        .nav-match:hover { color: #0a1628; background: #e6b83a; border-color: #e6b83a; }
        .btn-match { background: #f8c842; color: #0a1628; font-weight: 600; border: none; padding: 12px 30px; border-radius: 30px; }
        .btn-match:hover { background: #e6b83a; }
        .card { border: none; border-radius: 16px; box-shadow: 0 6px 20px rgba(0,0,0,0.08); }
        .aba-talent-section { position: relative; overflow: hidden; margin-top: 2.5rem; padding: clamp(1.5rem, 4vw, 2.5rem); border-radius: 24px; background: linear-gradient(145deg, #0a1628 0%, #152b4c 62%, #24446e 100%); color: white; box-shadow: 0 18px 48px rgba(10,22,40,0.2); }
        .aba-talent-section::after { content: ''; position: absolute; top: -90px; right: -80px; width: 260px; height: 260px; border-radius: 50%; background: rgba(248,200,66,0.11); }
        .aba-talent-content { position: relative; z-index: 1; }
        .aba-eyebrow { display: inline-flex; align-items: center; gap: 0.45rem; margin-bottom: 0.9rem; padding: 0.38rem 0.75rem; border: 1px solid rgba(248,200,66,0.5); border-radius: 999px; background: rgba(248,200,66,0.1); color: #f8c842; font-size: 0.75rem; font-weight: 800; letter-spacing: 0.1em; text-transform: uppercase; }
        .aba-talent-title { max-width: 650px; margin-bottom: 0.8rem; font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; font-size: clamp(1.7rem, 4vw, 2.5rem); font-weight: 700; line-height: 1.12; }
        .aba-talent-lead { max-width: 690px; color: rgba(255,255,255,0.8); font-size: 1.03rem; line-height: 1.65; }
        .aba-benefits { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 0.85rem; margin: 1.5rem 0; }
        .aba-benefit { padding: 1rem; border: 1px solid rgba(255,255,255,0.13); border-radius: 14px; background: rgba(255,255,255,0.07); }
        .aba-benefit-icon { display: block; margin-bottom: 0.45rem; font-size: 1.35rem; }
        .aba-benefit strong { display: block; color: #f8c842; }
        .aba-benefit span { display: block; margin-top: 0.3rem; color: rgba(255,255,255,0.72); font-size: 0.84rem; line-height: 1.4; }
        .aba-mentorship { margin-bottom: 1.5rem; padding: 1.15rem; border-left: 4px solid #f8c842; border-radius: 0 14px 14px 0; background: rgba(248,200,66,0.1); }
        .aba-mentorship h3 { color: #f8c842; font-size: 1.05rem; }
        .aba-mentorship p { margin: 0; color: rgba(255,255,255,0.83); line-height: 1.55; }
        .aba-submit-form { padding: clamp(1.25rem, 4vw, 2rem); border-radius: 18px; background: white; color: #0a1628; }
        .aba-submit-form .form-control { min-height: 48px; border-color: #d8dee8; border-radius: 11px; }
        .aba-submit-form .form-control:focus { border-color: #d4a900; box-shadow: 0 0 0 4px rgba(248,200,66,0.2); }
        .aba-submit-button { border: 0; border-radius: 999px; padding: 0.85rem 1.65rem; background: #f8c842; color: #0a1628; font-weight: 800; }
        .aba-submit-button:hover { background: #e6b83a; transform: translateY(-1px); }
        .privacy-note { color: #6b7280; font-size: 0.78rem; }
        .footer { background: #0a1628; color: white; padding: 20px 0; margin-top: 40px; border-radius: 20px 20px 0 0; }
        .alert-pre { white-space: pre-wrap; font-family: inherit; }
        :root { --aba-blue: #005a8c; --aba-gray: #58595b; --aba-gold: #dc9f1d; --aba-slate: #4e7c9c; --aba-sans: "Helvetica Neue", Helvetica, Arial, sans-serif; --aba-serif: "Minion Pro", "Times New Roman", Times, serif; }
        body { color: var(--aba-gray); font-family: var(--aba-sans); }
        .navbar, .footer { background: var(--aba-blue) !important; }
        .brand-icon { border-color: rgba(220,159,29,0.76); background: linear-gradient(145deg, rgba(220,159,29,0.24), rgba(220,159,29,0.07)); }
        .brand-highlight { color: var(--aba-gold); }
        .nav-button:focus-visible { box-shadow: 0 0 0 3px rgba(220,159,29,0.42); }
        .nav-home:hover, .nav-favorites:hover { color: var(--aba-blue); }
        .nav-match, .btn-match, .aba-submit-button { color: white; background: var(--aba-gold); border-color: var(--aba-gold); }
        .nav-match:hover, .btn-match:hover, .aba-submit-button:hover { color: white; background: #bd8413; border-color: #bd8413; }
        .aba-talent-section { background: linear-gradient(145deg, var(--aba-blue) 0%, var(--aba-slate) 100%); box-shadow: 0 18px 48px rgba(0,90,140,0.2); }
        .aba-talent-section::after { background: rgba(220,159,29,0.13); }
        .aba-eyebrow { border-color: rgba(220,159,29,0.62); background: rgba(220,159,29,0.12); color: #f2c75d; }
        .aba-benefit strong, .aba-mentorship h3 { color: #f2c75d; }
        .aba-mentorship { border-left-color: var(--aba-gold); background: rgba(220,159,29,0.12); }
        .aba-submit-form { color: var(--aba-gray); }
        .aba-submit-form .form-control:focus { border-color: var(--aba-gold); box-shadow: 0 0 0 4px rgba(220,159,29,0.2); }
        .privacy-note { color: var(--aba-gray); }
        .card > p, .aba-talent-lead, .aba-benefit span, .aba-mentorship p, .aba-submit-form > p, .alert-pre { font-family: var(--aba-serif); }
        @media (max-width: 767.98px) { .aba-benefits { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="/"><img class="brand-logo" src="/banking-future-logo.svg" alt="" width="42" height="42"><span class="brand-copy"><span class="brand-title">Banking on the <span class="brand-highlight">Future</span></span><span class="brand-attribution">American Bankers Association</span></span></a>
            <div class="nav-actions">
                <a class="nav-button nav-home" href="/">Home</a>
                <a class="nav-button nav-match" href="/match">Match</a>
                <a class="nav-button nav-match" href="/resume">Resume Review</a>
                <a class="nav-button nav-favorites" href="/favorites">Favorites (<span data-favorite-count>0</span>)</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4 mb-5 flex-grow-1">
        <div class="row justify-content-center">
            <div class="col-lg-8">
                <div class="card p-4">
                    <h2 class="text-center">Resume Review</h2>
                    <p class="text-center text-muted">Upload your resume and tell us your target position. We will provide editing advice and interview questions.</p>

                    {% if error %}
                    <div class="alert alert-danger">{{ error }}</div>
                    {% endif %}

                    <form method="POST" action="/resume" enctype="multipart/form-data">
                        <input type="hidden" name="form_type" value="resume_review">
                        <div class="mb-3">
                            <label class="form-label fw-bold">Target Position</label>
                            <input type="text" name="target_position" class="form-control" placeholder="e.g., Risk Analyst" value="{{ target_position }}" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label fw-bold">Upload Resume</label>
                            <input type="file" name="resume_file" class="form-control" accept=".pdf,.txt" required>
                            <div class="form-text">Supported formats: PDF, TXT.</div>
                        </div>
                        <div class="text-center">
                            <button type="submit" class="btn btn-match btn-lg">Submit Resume Review</button>
                        </div>
                    </form>

                    {% if feedback %}
                    <div class="mt-4">
                        <h4>Resume Feedback</h4>
                        <div class="card p-3">
                            <pre class="alert-pre mb-0">{{ feedback }}</pre>
                        </div>
                    </div>
                    {% endif %}
                </div>

                <section class="aba-talent-section" aria-labelledby="aba-talent-title">
                    <div class="aba-talent-content">
                        <div class="aba-eyebrow">✨ Your next opportunity starts here</div>
                        <h2 class="aba-talent-title" id="aba-talent-title">Submit Your Resume to the ABA Talent Pool</h2>
                        <p class="aba-talent-lead">Don’t let your resume sit in just one application portal. Tell us where you want to go, and ABA can share your resume with participating member banks looking for emerging talent—giving you another powerful path to be discovered.</p>

                        <div class="aba-benefits">
                            <div class="aba-benefit"><span class="aba-benefit-icon">🏦</span><strong>Reach member banks</strong><span>Your resume can be considered by banks across ABA’s membership network.</span></div>
                            <div class="aba-benefit"><span class="aba-benefit-icon">👀</span><strong>Increase your visibility</strong><span>Join ABA’s dedicated talent pool so more banking employers can discover your potential.</span></div>
                            <div class="aba-benefit"><span class="aba-benefit-icon">🚀</span><strong>Open more doors</strong><span>One submission can connect you with opportunities beyond the role you originally had in mind.</span></div>
                        </div>

                        <div class="aba-mentorship">
                            <h3>🌟 Standout students may be invited to ABA’s student membership and mentorship program!</h3>
                            <p>Selected students can be paired with a real ABA professional who will personally help refine their resume, offer practical career guidance, and practice interviews through one-on-one mock interview sessions.</p>
                        </div>

                        <div class="aba-submit-form">
                            <h3 class="h4 fw-bold mb-2">Put your name in the room</h3>
                            <p class="text-muted mb-4">Share your goals and resume with ABA. We’re excited to see where your banking journey could take you.</p>

                            {% if submission_success %}
                            <div class="alert alert-success" role="status"><strong>🎉 You’re in the ABA Talent Pool!</strong><br>{{ submission_success }}</div>
                            {% endif %}
                            {% if submission_error %}
                            <div class="alert alert-danger" role="alert">{{ submission_error }}</div>
                            {% endif %}

                            <form method="POST" action="/resume#aba-talent-title" enctype="multipart/form-data">
                                <input type="hidden" name="form_type" value="aba_submission">
                                <div class="row g-3">
                                    <div class="col-md-6">
                                        <label class="form-label fw-bold" for="applicantName">Full Name</label>
                                        <input id="applicantName" type="text" name="applicant_name" class="form-control" value="{{ applicant_name }}" autocomplete="name" required>
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label fw-bold" for="applicantEmail">Email Address</label>
                                        <input id="applicantEmail" type="email" name="applicant_email" class="form-control" value="{{ applicant_email }}" autocomplete="email" required>
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label fw-bold" for="targetBank">Bank You Want to Apply To</label>
                                        <input id="targetBank" type="text" name="target_bank" class="form-control" value="{{ target_bank }}" placeholder="e.g., First Community Bank" required>
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label fw-bold" for="abaTargetPosition">Position You Want</label>
                                        <input id="abaTargetPosition" type="text" name="aba_target_position" class="form-control" value="{{ aba_target_position }}" placeholder="e.g., Data Analyst Intern" required>
                                    </div>
                                    <div class="col-12">
                                        <label class="form-label fw-bold" for="abaResumeFile">Upload Your Resume</label>
                                        <input id="abaResumeFile" type="file" name="aba_resume_file" class="form-control" accept=".pdf,.doc,.docx,.txt" required>
                                        <div class="form-text">PDF, DOC, DOCX, or TXT · Maximum 5 MB</div>
                                    </div>
                                    <div class="col-12">
                                        <div class="form-check">
                                            <input class="form-check-input" type="checkbox" name="sharing_consent" value="yes" id="sharingConsent" required>
                                            <label class="form-check-label" for="sharingConsent">I authorize ABA to store my resume and share it with participating ABA member banks for recruiting consideration. I understand that submission does not guarantee employment or selection for the mentorship program.</label>
                                        </div>
                                    </div>
                                    <div class="col-12 d-flex flex-column flex-md-row align-items-md-center gap-3">
                                        <button type="submit" class="aba-submit-button">Join the ABA Talent Pool →</button>
                                        <span class="privacy-note">Your information is collected for recruiting and talent-pool consideration.</span>
                                    </div>
                                </div>
                            </form>
                        </div>
                    </div>
                </section>
            </div>
        </div>
    </div>

    <div class="footer">
        <div class="container text-center">
            <p class="mb-0">🏦 Banking on the Future © 2026</p>
        </div>
    </div>
    {{ favorite_script | safe }}
</body>
</html>
'''

# %%
favorites_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Favorite Jobs - Banking on the Future</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&display=swap" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(rgba(245, 247, 250, 0.82), rgba(245, 247, 250, 0.82)), url('/background1.jpg') center / cover fixed no-repeat;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .navbar { background: #0a1628 !important; }
        .navbar-brand { color: #ffffff !important; font-family: 'Cormorant Garamond', Georgia, serif; font-size: 1.65rem; font-weight: 700; letter-spacing: 0.015em; line-height: 1; display: inline-flex; align-items: center; gap: 11px; }
        .brand-icon { display: inline-grid; place-items: center; width: 38px; height: 38px; border: 1px solid rgba(248, 200, 66, 0.72); border-radius: 10px; background: linear-gradient(145deg, rgba(248, 200, 66, 0.2), rgba(248, 200, 66, 0.05)); box-shadow: inset 0 0 0 1px rgba(255,255,255,0.05); font-size: 1.05rem; }
        .brand-highlight { color: #f8c842; font-weight: 600; }
        .brand-logo { display: block; width: 42px; height: 42px; flex: 0 0 auto; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.14); }
        .brand-copy { display: flex; flex-direction: column; gap: 4px; }
        .brand-title { line-height: 0.9; }
        .brand-attribution { color: rgba(255,255,255,0.72); font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; font-size: 0.56rem; font-weight: 700; letter-spacing: 0.12em; line-height: 1; text-transform: uppercase; }
        .nav-actions { display: flex; flex-wrap: wrap; justify-content: flex-end; gap: 10px; }
        .nav-button { padding: 8px 18px; border: 1px solid transparent; border-radius: 999px; font-weight: 600; text-decoration: none; transition: background-color 0.2s, color 0.2s, transform 0.2s; }
        .nav-button:hover { transform: translateY(-1px); }
        .nav-button:focus-visible { outline: none; box-shadow: 0 0 0 3px rgba(248, 200, 66, 0.4); }
        .nav-home, .nav-favorites { color: white; border-color: rgba(255,255,255,0.7); }
        .nav-home:hover, .nav-favorites:hover { color: #0a1628; background: white; }
        .nav-match { color: #0a1628; background: #f8c842; border-color: #f8c842; }
        .nav-match:hover { color: #0a1628; background: #e6b83a; border-color: #e6b83a; }
        .page-header { background: linear-gradient(135deg, #0a1628, #1a2a4a); color: white; padding: 42px 30px; border-radius: 20px; }
        .job-card { height: 100%; border: none; border-radius: 16px; box-shadow: 0 6px 20px rgba(0,0,0,0.08); }
        .job-card .job-description { flex-grow: 1; }
        .job-card h5, .job-card h6 { overflow-wrap: anywhere; }
        .favorite-meta { display: flex; flex-wrap: wrap; gap: 0.45rem; }
        .favorite-pill { display: inline-block; max-width: 100%; padding: 0.36rem 0.58rem; border-radius: 8px; font-size: 0.75rem; font-weight: 700; line-height: 1.3; white-space: normal; overflow-wrap: anywhere; }
        .favorite-salary { background: #e2f3e8; color: #17633a; }
        .favorite-office { background: #e3f1f6; color: #174f63; }
        .job-title { color: #0a1628; font-weight: 700; text-decoration: none; }
        .job-title:hover { color: #d4a900; }
        .favorite-button { border-color: #d4a900; color: #725b00; font-weight: 600; }
        .favorite-button:hover, .favorite-button.is-favorite { background: #f8c842; border-color: #f8c842; color: #0a1628; }
        .empty-state { background: white; border-radius: 16px; padding: 50px 24px; text-align: center; box-shadow: 0 6px 20px rgba(0,0,0,0.06); }
        .footer { background: #0a1628; color: white; padding: 20px 0; margin-top: 40px; border-radius: 20px 20px 0 0; }
        :root { --aba-blue: #005a8c; --aba-gray: #58595b; --aba-gold: #dc9f1d; --aba-slate: #4e7c9c; --aba-sans: "Helvetica Neue", Helvetica, Arial, sans-serif; --aba-serif: "Minion Pro", "Times New Roman", Times, serif; }
        body { color: var(--aba-gray); font-family: var(--aba-sans); }
        .navbar, .footer { background: var(--aba-blue) !important; }
        .brand-icon { border-color: rgba(220,159,29,0.76); background: linear-gradient(145deg, rgba(220,159,29,0.24), rgba(220,159,29,0.07)); }
        .brand-highlight { color: var(--aba-gold); }
        .nav-button:focus-visible { box-shadow: 0 0 0 3px rgba(220,159,29,0.42); }
        .nav-home:hover, .nav-favorites:hover { color: var(--aba-blue); }
        .nav-match { color: white; background: var(--aba-gold); border-color: var(--aba-gold); }
        .nav-match:hover { color: white; background: #bd8413; border-color: #bd8413; }
        .page-header { background: linear-gradient(135deg, var(--aba-blue), var(--aba-slate)); }
        .job-title { color: var(--aba-blue); }
        .job-title:hover { color: #9a6b0d; }
        .favorite-office { background: #e5f0f6; color: var(--aba-blue); }
        .favorite-button { border-color: var(--aba-gold); color: #76550d; }
        .favorite-button:hover, .favorite-button.is-favorite { background: var(--aba-gold); border-color: var(--aba-gold); color: white; }
        .job-description, .empty-state p { font-family: var(--aba-serif); }
    </style>
</head>
<body data-page="favorites">
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="/"><img class="brand-logo" src="/banking-future-logo.svg" alt="" width="42" height="42"><span class="brand-copy"><span class="brand-title">Banking on the <span class="brand-highlight">Future</span></span><span class="brand-attribution">American Bankers Association</span></span></a>
            <div class="nav-actions">
                <a class="nav-button nav-home" href="/">Home</a>
                <a class="nav-button nav-match" href="/match">Match</a>
                <a class="nav-button nav-match" href="/resume">Resume Review</a>
                <a class="nav-button nav-favorites" href="/favorites">Favorites (<span data-favorite-count>0</span>)</a>
            </div>
        </div>
    </nav>

    <main class="container mt-4 flex-grow-1">
        <div class="page-header mb-4">
            <h1 class="display-6 fw-bold">Favorite Jobs</h1>
            <p class="lead mb-0">Keep the banking roles you want to explore further.</p>
        </div>

        <div class="row">
            {% for job in jobs %}
            <div class="col-md-6 col-lg-4 mb-4 d-flex d-none" data-favorite-card data-job-id="{{ job.id }}">
                <div class="card job-card p-3 d-flex flex-column w-100">
                    <h5><a href="/job/{{ job.id }}" class="job-title">{{ job.name }}</a></h5>
                    <h6 class="text-muted">{{ job.department }}</h6>
                    <p class="job-description text-muted small">{{ job.description[:120] }}...</p>
                    <div class="favorite-meta">
                        <span class="favorite-pill favorite-salary">{{ job.salary }}</span>
                        <span class="favorite-pill favorite-office">{{ job.office }}</span>
                    </div>
                    <div class="d-flex gap-2 mt-2">
                        <a href="/job/{{ job.id }}" class="btn btn-outline-dark btn-sm flex-grow-1">View Details</a>
                        <button type="button" class="btn favorite-button btn-sm" data-favorite-button data-job-id="{{ job.id }}" aria-pressed="true">Saved</button>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>

        <div class="empty-state" data-favorites-empty>
            <h3>No favorite jobs yet</h3>
            <p class="text-muted">Save roles from the home, matching, or job detail pages.</p>
            <a href="/" class="btn btn-dark">Browse All Jobs</a>
        </div>
    </main>

    <div class="footer">
        <div class="container text-center">
            <p class="mb-0">🏦 Banking on the Future © 2026</p>
        </div>
    </div>
    {{ favorite_script | safe }}
</body>
</html>
'''

# %%
@app.route('/')
def index():
    """Home page showing all banking jobs"""
    category_details = [
        {
            "id": "banking-client-services",
            "name": "Banking & Client Services",
            "description": "Roles centered on serving individuals, businesses, and institutional banking clients.",
            "button_description": "Includes retail, commercial, corporate, lending, and relationship roles. A great fit if you enjoy helping customers and working with clients.",
            "icon": "🏦",
            "button_class": "role-path-banking",
            "families": [
                ("Business, Commercial & Corporate Banking", "Business lending, corporate banking, credit, treasury-services, and relationship roles"),
                ("Consumer & Retail Banking", "Branch, personal banking, mortgages, cards, consumer lending, and customer-service roles"),
            ],
        },
        {
            "id": "markets-investments-wealth",
            "name": "Markets, Investments & Wealth",
            "description": "Roles involving capital markets, investments, trading, research, and wealth management.",
            "button_description": "Includes investment banking, markets, trading, research, securities services, and wealth management. A strong fit if you enjoy investments, strategy, and numbers.",
            "icon": "📈",
            "button_class": "role-path-markets",
            "families": [
                ("Investment Banking & Capital Markets", "Advisory, mergers and acquisitions, underwriting, and capital-raising roles"),
                ("Markets, Sales & Trading", "Sales, trading, structuring, quantitative, and markets roles"),
                ("Wealth Management, Private Bank & Trust", "Advisory, portfolio, trust, planning, and private-banking roles"),
                ("Research", "Economic, equity, credit, and investment-research roles"),
                ("Securities Services", "Custody, fund services, and institutional asset-servicing roles"),
            ],
        },
        {
            "id": "risk-finance-controls",
            "name": "Risk, Finance & Controls",
            "description": "Roles that protect the bank, manage its balance sheet, and support financial integrity.",
            "button_description": "Includes risk, compliance, legal, treasury, finance, accounting, and audit. Ideal if you are analytical, careful, ethical, and detail-focused.",
            "icon": "🛡️",
            "button_class": "role-path-controls",
            "families": [
                ("Risk Management", "Credit, market, liquidity, model, operational, and enterprise-risk roles"),
                ("Treasury, Finance & Capital Management", "Liquidity, funding, capital, reporting, accounting, tax, and financial-control roles"),
                ("Compliance, Financial Crime & Legal", "Compliance, AML, sanctions, fraud, regulatory, and legal roles"),
                ("Internal Audit", "Independent business, technology, risk, and control-assurance roles"),
            ],
        },
        {
            "id": "technology-operations-impact",
            "name": "Technology, Operations & Corporate Impact",
            "description": "Roles that build technology, run the bank, shape products, and strengthen its people and communities.",
            "button_description": "Includes technology, data, operations, product, strategy, marketing, HR, and community impact. A great fit for builders, organizers, communicators, and creative thinkers.",
            "icon": "💡",
            "button_class": "role-path-innovation",
            "families": [
                ("Technology, Cybersecurity & Data", "Software, cloud, cybersecurity, AI, engineering, data, and technology-risk roles"),
                ("Operations, Payments & Servicing", "Payments, servicing, onboarding, settlement, processing, and operational-resilience roles"),
                ("Product, Strategy & Corporate Functions", "Product, strategy, project, marketing, communications, HR, and corporate-support roles"),
                ("Community Impact & Responsible Banking", "CRA, accessibility, financial education, sustainability, and community-impact roles"),
            ],
        },
    ]
    role_categories = []
    for category in category_details:
        groups = [
            {
                "name": name,
                "description": description,
                "jobs": [job for job in jobs_list if job.get("job_family") == name],
            }
            for name, description in category["families"]
        ]
        role_categories.append(
            {
                **category,
                "groups": groups,
                "job_count": sum(len(group["jobs"]) for group in groups),
            }
        )
    return render_template_string(
        index_html,
        jobs=jobs_list,
        role_categories=role_categories,
        favorite_script=favorite_script,
    )

# %%
@app.route('/job/<int:job_id>')
def job_detail(job_id):
    """Show detailed information for a specific job"""
    # Find the job with matching ID
    job = None
    for j in jobs_list:
        if j["id"] == job_id:
            job = j
            break
    
    if job is None:
        return "Job not found", 404
    
    return render_template_string(
        detail_html,
        job=job,
        favorite_script=favorite_script,
    )

# %%
@app.route('/favorites')
def favorites():
    """Show jobs saved in this browser."""
    return render_template_string(
        favorites_html,
        jobs=jobs_list,
        favorite_script=favorite_script,
    )

# %%
@app.route('/match', methods=['GET', 'POST'])
def match():
    """Career matching page - shows form and results, with integrated advisor"""
    results = None
    advice = ''
    selected_major = ''
    selected_grade = ''
    selected_personality = []
    
    if request.method == 'POST':
        # Get user input from form
        selected_major = request.form.get('major', '')
        selected_grade = request.form.get('grade', '')
        selected_personality = request.form.getlist('personality')
        for field_name in ('personality_q1', 'personality_q2', 'personality_q3',
                           'personality_q4', 'personality_q5', 'personality_q6'):
            trait = request.form.get(field_name, '')
            if trait and trait not in selected_personality:
                selected_personality.append(trait)
        
        # Check if user is asking for advisor advice
        is_asking_advice = request.form.get('get_advice') == 'true'
        question = request.form.get('question', '').strip()
        
        if is_asking_advice and question:
            # Generate advisor advice based on user profile and question
            user_profile = {
                'major': selected_major,
                'grade': selected_grade,
                'personality': selected_personality,
            }
            # Get relevant jobs for context (no more than 5)
            relevant_jobs = ai_advisor.get_relevant_jobs(user_profile, jobs_list, count=5)
            advice = ai_advisor.generate_advice(user_profile, question, relevant_jobs)
            # Keep results from previous match
            if selected_major:
                scored_jobs = []
                for job in jobs_list:
                    job_copy = job.copy()
                    job_copy['match_score'] = calculate_match_score(job, selected_major, selected_grade, selected_personality)
                    scored_jobs.append(job_copy)
                scored_jobs.sort(key=lambda x: x['match_score'], reverse=True)
                results = scored_jobs[:5]
        else:
            # Calculate match score for each job
            scored_jobs = []
            for job in jobs_list:
                job_copy = job.copy()
                job_copy['match_score'] = calculate_match_score(job, selected_major, selected_grade, selected_personality)
                scored_jobs.append(job_copy)
            
            # Sort by match score (highest first)
            scored_jobs.sort(key=lambda x: x['match_score'], reverse=True)
            
            # Get top 5 matches
            results = scored_jobs[:5]
    
    # Get all unique majors and personality traits for the form
    all_majors = get_all_majors()
    all_personality = get_all_personality()
    
    return render_template_string(match_html, 
                                all_majors=all_majors, 
                                all_personality=all_personality, 
                                results=results,
                                selected_major=selected_major,
                                selected_grade=selected_grade,
                                selected_personality=selected_personality,
                                advice=advice,
                                favorite_script=favorite_script)

# %%
@app.route('/resume', methods=['GET', 'POST'])
def resume_review():
    """Resume review plus opt-in submission to the ABA talent pool."""
    feedback = ''
    error = ''
    target_position = ''
    submission_success = ''
    submission_error = ''
    applicant_name = ''
    applicant_email = ''
    target_bank = ''
    aba_target_position = ''

    if request.method == 'POST':
        form_type = request.form.get('form_type', 'resume_review')

        if form_type == 'aba_submission':
            applicant_name = request.form.get('applicant_name', '').strip()
            applicant_email = request.form.get('applicant_email', '').strip()
            target_bank = request.form.get('target_bank', '').strip()
            aba_target_position = request.form.get('aba_target_position', '').strip()
            sharing_consent = request.form.get('sharing_consent') == 'yes'
            aba_resume_file = request.files.get('aba_resume_file')

            if not applicant_name:
                submission_error = 'Please enter your full name.'
            elif not applicant_email or '@' not in applicant_email:
                submission_error = 'Please enter a valid email address.'
            elif not target_bank:
                submission_error = 'Please enter the bank you want to apply to.'
            elif not aba_target_position:
                submission_error = 'Please enter the position you want to apply for.'
            elif not aba_resume_file or aba_resume_file.filename == '':
                submission_error = 'Please upload your resume.'
            elif not sharing_consent:
                submission_error = 'Please provide permission for ABA to store and share your resume with participating member banks.'
            else:
                original_filename = secure_filename(aba_resume_file.filename)
                extension = os.path.splitext(original_filename)[1].lower()
                if extension not in ABA_ALLOWED_RESUME_EXTENSIONS:
                    submission_error = 'Unsupported file type. Upload a PDF, DOC, DOCX, or TXT resume.'
                else:
                    resume_data = aba_resume_file.read(ABA_MAX_RESUME_SIZE + 1)
                    if not resume_data:
                        submission_error = 'The uploaded resume is empty. Please choose another file.'
                    elif len(resume_data) > ABA_MAX_RESUME_SIZE:
                        submission_error = 'Your resume is larger than 5 MB. Please upload a smaller file.'
                    else:
                        stored_filename = f'{uuid.uuid4().hex}{extension}'
                        stored_path = os.path.join(ABA_SUBMISSION_DIR, stored_filename)
                        try:
                            os.makedirs(ABA_SUBMISSION_DIR, exist_ok=True)
                            with open(stored_path, 'wb') as stored_resume:
                                stored_resume.write(resume_data)

                            submission_record = {
                                'submission_id': uuid.uuid4().hex,
                                'submitted_at_utc': datetime.now(timezone.utc).isoformat(),
                                'applicant_name': applicant_name,
                                'applicant_email': applicant_email,
                                'target_bank': target_bank,
                                'target_position': aba_target_position,
                                'original_filename': original_filename,
                                'stored_filename': stored_filename,
                                'sharing_consent': True,
                            }
                            with open(ABA_SUBMISSION_METADATA, 'a', encoding='utf-8') as metadata_file:
                                metadata_file.write(json.dumps(submission_record, ensure_ascii=False) + '\n')

                            submission_success = (
                                'ABA has received your resume and career interests. '
                                'Your profile can now be reviewed for member-bank opportunities and selective mentorship consideration.'
                            )
                            applicant_name = ''
                            applicant_email = ''
                            target_bank = ''
                            aba_target_position = ''
                        except OSError:
                            try:
                                if os.path.exists(stored_path):
                                    os.remove(stored_path)
                            except OSError:
                                pass
                            submission_error = 'We could not save your submission right now. Please try again.'
        else:
            target_position = request.form.get('target_position', '').strip()
            resume_file = request.files.get('resume_file')

            if not target_position:
                error = 'Please enter your target position.'
            elif not resume_file or resume_file.filename == '':
                error = 'Please upload a resume file.'
            else:
                filename = resume_file.filename
                extension = os.path.splitext(filename)[1].lower()
                try:
                    if extension == '.txt':
                        raw_text = resume_file.read().decode('utf-8', errors='ignore')
                    elif extension == '.pdf':
                        with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as tmp:
                            tmp.write(resume_file.read())
                            tmp_path = tmp.name
                        raw_text = resume_polisher.extract_text_from_resume(tmp_path)
                        try:
                            os.remove(tmp_path)
                        except OSError:
                            pass
                    else:
                        error = 'Unsupported file type. Upload a PDF or TXT resume.'
                        raw_text = ''

                    if not error:
                        if not raw_text.strip():
                            error = 'Could not extract text from the resume file. Please upload a different file.'
                        else:
                            feedback = resume_polisher.generate_resume_feedback(raw_text, target_position)
                except Exception as e:
                    error = f'Error processing resume: {e}'

    return render_template_string(
        resume_html,
        feedback=feedback,
        error=error,
        target_position=target_position,
        submission_success=submission_success,
        submission_error=submission_error,
        applicant_name=applicant_name,
        applicant_email=applicant_email,
        target_bank=target_bank,
        aba_target_position=aba_target_position,
        favorite_script=favorite_script,
    )

# %%
@app.route('/advisor', methods=['GET', 'POST'])
def advisor_redirect():
    """Redirect advisor requests to the unified match page"""
    return redirect(url_for('match'))

# %%
if __name__ == '__main__':
    print("=" * 60)
    print("🏦 Banking on the Future - Flask Application")
    print("=" * 60)
    print(f"📊 Loaded {len(jobs_list)} banking roles")
    print("=" * 60)
    print("\n🚀 Starting Flask app...")
    print("📱 Open your browser and go to: http://localhost:5001")
    print("📱 or http://127.0.0.1:5001")
    print("=" * 60)
    app.run(debug=True, port=5001, host='0.0.0.0') 
