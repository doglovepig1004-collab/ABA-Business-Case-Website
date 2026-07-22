# %%
# Notebook setup: pip install flask flask-ngrok

# %%
from flask import Flask, render_template_string, request, redirect, url_for, send_from_directory
from flask_ngrok import run_with_ngrok
import json
import sys
import os
import tempfile
import ai_advisor
import resume_polisher

# %%
app = Flask(__name__)
# run_with_ngrok(app)  # Comment this out if running locally

@app.route('/background1.jpg')
def background_image():
    """Serve the site background image from the project folder."""
    return send_from_directory(notebook_path, 'background1.jpg')

# %%
# Get the current notebook directory
notebook_path = os.getcwd()

# Try to import jobs_list from website_data.py
try:
    from website_data import jobs_list
    print(f"✅ Successfully imported {len(jobs_list)} jobs from website_data.py")
except ImportError:
    print("❌ website_data.py not found")
    print("Please make sure website_data.py is in the same folder as this notebook")
    jobs_list = []  # Empty list as fallback
except Exception as e:
    print(f"❌ Error loading website_data.py: {e}")
    jobs_list = []

# %%
def get_all_majors():
    """Extract all unique majors from the job database"""
    majors = set()
    for job in jobs_list:
        for major in job["suitable_major"]:
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
    elif major == "Any Major":
        score += 20
    
    # Grade/Level match (max 30 points)
    if grade.lower() in job["suitable_grade"].lower():
        score += 30
    elif "preferred" in job["suitable_grade"].lower() and "graduate" in grade.lower():
        score += 20
    elif "graduate" in grade.lower() and "graduate" in job["suitable_grade"].lower():
        score += 25
    elif "senior" in grade.lower() and "senior" in job["suitable_grade"].lower():
        score += 25
    
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
    <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=Montserrat:wght@700;800&display=swap" rel="stylesheet">
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
        .office-section { margin-top: 2.5rem; }
        .office-heading { border-left: 5px solid #f8c842; padding-left: 12px; color: #0a1628; }
        .job-title { color: #0a1628; font-weight: 700; text-decoration: none; }
        .job-title:hover { color: #f8c842; }
        .favorite-button { border-color: #d4a900; color: #725b00; font-weight: 600; }
        .favorite-button:hover, .favorite-button.is-favorite { background: #f8c842; border-color: #f8c842; color: #0a1628; }
        .hero { background: linear-gradient(135deg, #0a1628, #1a2a4a); color: white; padding: 60px 0; border-radius: 20px; margin-bottom: 40px; }
        .hero-title { display: inline-block; position: relative; margin-bottom: 1.25rem; font-family: 'Montserrat', Arial, sans-serif; font-size: clamp(2.4rem, 6vw, 4.6rem); font-weight: 800; line-height: 1.08; letter-spacing: -0.055em; background: linear-gradient(100deg, #ffffff 18%, #f8c842 82%); -webkit-background-clip: text; background-clip: text; color: transparent; text-shadow: 0 8px 30px rgba(0,0,0,0.18); }
        .hero-title::after { content: ''; position: absolute; left: 50%; bottom: -14px; width: 76px; height: 3px; border-radius: 999px; background: #f8c842; transform: translateX(-50%); box-shadow: 0 0 16px rgba(248, 200, 66, 0.45); }
        .btn-match { background: #f8c842; color: #0a1628; font-weight: 600; border: none; padding: 12px 30px; border-radius: 30px; }
        .btn-match:hover { background: #e6b83a; color: #0a1628; }
        .footer { background: #0a1628; color: white; padding: 20px 0; margin-top: 40px; border-radius: 20px 20px 0 0; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="/"><span class="brand-icon">🏦</span><span>Banking on the <span class="brand-highlight">Future</span></span></a>
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
        
        <h3>All Banking Roles</h3>
        <p class="text-muted">{{ jobs|length }} positions available</p>

        {% for group in office_groups %}
        <section class="office-section">
            <h4 class="office-heading">{{ group.name }}</h4>
            <p class="text-muted">{{ group.description }} · {{ group.jobs|length }} roles</p>
            <div class="row">
                {% for job in group.jobs %}
                <div class="col-md-6 col-lg-4 mb-4 d-flex">
                    <div class="card job-card p-3 d-flex flex-column w-100">
                        <h5><a href="/job/{{ job.id }}" class="job-title">{{ job.name }}</a></h5>
                        <h6 class="text-muted">{{ job.department }}</h6>
                        <p class="job-description text-muted small">{{ job.description[:120] }}...</p>
                        <div class="mt-2">
                            <span class="badge bg-success">{{ job.salary }}</span>
                            <span class="badge bg-info text-dark">{{ job.suitable_grade }}</span>
                        </div>
                        <div class="d-flex gap-2 mt-2">
                            <a href="/job/{{ job.id }}" class="btn btn-outline-dark btn-sm flex-grow-1">View Details</a>
                            <button type="button" class="btn favorite-button btn-sm" data-favorite-button data-job-id="{{ job.id }}" aria-pressed="false">Save Job</button>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
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
    <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=Montserrat:wght@700;800&display=swap" rel="stylesheet">
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
        .footer { background: #0a1628; color: white; padding: 20px 0; margin-top: 40px; border-radius: 20px 20px 0 0; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="/"><span class="brand-icon">🏦</span><span>Banking on the <span class="brand-highlight">Future</span></span></a>
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
        
        <div class="card p-4">
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
                            <span class="badge bg-success fs-6">{{ job.salary }}</span>
                        </div>
                        <div class="col-md-6">
                            <h6>Suitable Grade</h6>
                            <span class="badge bg-info text-dark fs-6">{{ job.suitable_grade }}</span>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-4">
                    <div class="bg-light p-3 rounded">
                        <h6>Recommended Majors</h6>
                        {% for major in job.suitable_major %}
                        <span class="badge bg-primary m-1">{{ major }}</span>
                        {% endfor %}
                        
                        <h6 class="mt-3">Ideal Personality Traits</h6>
                        {% for trait in job.personality %}
                        <span class="badge bg-secondary m-1">{{ trait }}</span>
                        {% endfor %}
                        
                        <h6 class="mt-3">Key Skills</h6>
                        {% for skill in job.skills %}
                        <span class="badge bg-dark m-1">{{ skill }}</span>
                        {% endfor %}
                    </div>
                </div>
            </div>
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
    <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=Montserrat:wght@700;800&display=swap" rel="stylesheet">
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
        .match-card { border-left: 5px solid #f8c842; background: white; }
        .favorite-button { border-color: #d4a900; color: #725b00; font-weight: 600; }
        .favorite-button:hover, .favorite-button.is-favorite { background: #f8c842; border-color: #f8c842; color: #0a1628; }
        .footer { background: #0a1628; color: white; padding: 20px 0; margin-top: 40px; border-radius: 20px 20px 0 0; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="/"><span class="brand-icon">🏦</span><span>Banking on the <span class="brand-highlight">Future</span></span></a>
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
                <div class="card p-4">
                    <h2 class="text-center">Find Your Banking Career Match</h2>
                    <p class="text-center text-muted">Answer a few questions and we'll recommend the best roles for you</p>
                    
                    <form method="POST" action="/match">
                        <div class="mb-3">
                            <label class="form-label fw-bold">Your Major</label>
                            <select name="major" class="form-select" required>
                                <option value="">Select your major...</option>
                                {% for major in all_majors %}
                                <option value="{{ major }}">{{ major }}</option>
                                {% endfor %}
                            </select>
                        </div>
                        
                        <div class="mb-3">
                            <label class="form-label fw-bold">Your Grade/Level</label>
                            <select name="grade" class="form-select" required>
                                <option value="">Select your level...</option>
                                <option value="Fresh Graduate">Fresh Graduate</option>
                                <option value="Junior">Junior (1-2 years experience)</option>
                                <option value="Senior">Senior (3+ years experience)</option>
                                <option value="Graduate Student">Graduate Student</option>
                                <option value="Senior/Recent Graduate">Senior/Recent Graduate</option>
                                <option value="Senior/Graduate Student">Senior/Graduate Student</option>
                            </select>
                        </div>
                        
                        <div class="mb-3">
                            <label class="form-label fw-bold">Your Personality Traits</label>
                            <p class="text-muted small">Select all that apply</p>
                            <div class="row">
                                {% for trait in all_personality %}
                                <div class="col-md-6">
                                    <div class="form-check">
                                        <input class="form-check-input" type="checkbox" name="personality" value="{{ trait }}" id="trait_{{ loop.index }}">
                                        <label class="form-check-label" for="trait_{{ loop.index }}">{{ trait }}</label>
                                    </div>
                                </div>
                                {% endfor %}
                            </div>
                        </div>
                        
                        <div class="text-center">
                            <button type="submit" class="btn btn-match btn-lg">
                                Find My Match
                            </button>
                        </div>
                    </form>
                </div>
                
                {% if results %}
                <div class="mt-4">
                    <h3 class="text-center">Your Top Matches</h3>
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
                                    <span class="badge bg-success">{{ job.salary }}</span>
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
resume_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Resume Review - Banking on the Future</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=Montserrat:wght@700;800&display=swap" rel="stylesheet">
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
        .footer { background: #0a1628; color: white; padding: 20px 0; margin-top: 40px; border-radius: 20px 20px 0 0; }
        .alert-pre { white-space: pre-wrap; font-family: inherit; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="/"><span class="brand-icon">🏦</span><span>Banking on the <span class="brand-highlight">Future</span></span></a>
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
    <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=Montserrat:wght@700;800&display=swap" rel="stylesheet">
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
        .job-title { color: #0a1628; font-weight: 700; text-decoration: none; }
        .job-title:hover { color: #d4a900; }
        .favorite-button { border-color: #d4a900; color: #725b00; font-weight: 600; }
        .favorite-button:hover, .favorite-button.is-favorite { background: #f8c842; border-color: #f8c842; color: #0a1628; }
        .empty-state { background: white; border-radius: 16px; padding: 50px 24px; text-align: center; box-shadow: 0 6px 20px rgba(0,0,0,0.06); }
        .footer { background: #0a1628; color: white; padding: 20px 0; margin-top: 40px; border-radius: 20px 20px 0 0; }
    </style>
</head>
<body data-page="favorites">
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="/"><span class="brand-icon">🏦</span><span>Banking on the <span class="brand-highlight">Future</span></span></a>
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
                    <div>
                        <span class="badge bg-success">{{ job.salary }}</span>
                        <span class="badge bg-info text-dark">{{ job.office }}</span>
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
    office_details = [
        ("Front Office", "Client-facing and revenue-generating roles"),
        ("Middle Office", "Risk, compliance, product, and strategic support roles"),
        ("Back Office", "Operations, technology, finance, and internal support roles"),
        ("Specialized", "Specialized and emerging banking roles"),
    ]
    office_groups = [
        {
            "name": name,
            "description": description,
            "jobs": [job for job in jobs_list if job.get("office") == name],
        }
        for name, description in office_details
    ]
    return render_template_string(
        index_html,
        jobs=jobs_list,
        office_groups=office_groups,
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
    """Resume polishing and interview question advice using Gemini."""
    feedback = ''
    error = ''
    target_position = ''

    if request.method == 'POST':
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
