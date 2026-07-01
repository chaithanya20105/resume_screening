from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import docx2txt
import pdfplumber 
import re
import os

# ✅ Extract text from PDF
def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()

# ✅ Extract text from DOCX
def extract_text_from_docx(file):
    return docx2txt.process(file).strip()

# ✅ Preprocessing
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', ' ', text)  # remove punctuation/numbers/symbols
    text = re.sub(r'\s+', ' ', text).strip()  # normalize whitespace
    return text

# ✅ Extract name
def extract_name(text):
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if line.lower().startswith("name:"):
            return line.split(":", 1)[1].strip()
        if line:
            return line
    return "Candidate"

# ✅ Required skills
REQUIRED_SKILLS = {
    "python", "java", "c++", "c", "javascript", "typescript", "ruby", "go", "php", "sql",
    "django", "flask", "spring", "express", "react", "angular", "vue", "nextjs", "nodejs",
    "mysql", "postgresql", "mongodb", "sqlite", "oracle", "nosql", "redis",
    "git", "github", "gitlab", "bitbucket", "docker", "kubernetes", "jenkins", "ci", "cd", "aws", "azure", "gcp",
    "rest", "api", "graphql", "json", "http", "soap", "ajax",
    "html", "css", "bootstrap", "sass", "jquery", "tailwind",
    "unit testing", "selenium", "junit", "pytest", "cypress",
    "agile", "scrum", "oop", "data structures", "algorithms", "debugging", "version control"
}

# ✅ Extract skills from text
def extract_skills(text):
    known_skills = set(skill.lower() for skill in REQUIRED_SKILLS)
    text = text.lower()
    return {skill for skill in known_skills if skill in text}

# ✅ Compute skill match
def compute_skill_match(resume_skills_set, required_skills_set):
    resume_skills = set(map(lambda s: s.lower().strip(), resume_skills_set))
    required_skills = set(map(lambda s: s.lower().strip(), required_skills_set))
    matched_skills = resume_skills & required_skills
    score = len(matched_skills) / len(required_skills) * 100 if required_skills else 0
    return round(score, 2), matched_skills

# ✅ Main view for ranking multiple resumes
def screen_resumes(request):
    if request.method == 'POST':
        job_description = request.POST.get('job_description', '').strip()
        resume_files = request.FILES.getlist('resumes')

        if not resume_files or not job_description:
            return render(request, 'upload.html', {'error': 'Please upload at least one resume and enter a job description.'})

        candidates = []
        job_skills = extract_skills(job_description)

        for resume_file in resume_files:
            ext = os.path.splitext(resume_file.name)[1].lower()
            if ext == '.pdf':
                resume_text = extract_text_from_pdf(resume_file)
            elif ext == '.docx':
                resume_text = extract_text_from_docx(resume_file)
            else:
                continue

            if not resume_text.strip():
                continue

            clean_resume = preprocess_text(resume_text)
            clean_jd = preprocess_text(job_description)

            vectorizer = TfidfVectorizer(stop_words='english')
            vectors = vectorizer.fit_transform([clean_jd, clean_resume])
            tfidf_score = cosine_similarity(vectors[0:1], vectors[1:2])[0][0] * 100

            resume_skills = extract_skills(resume_text)
            skill_score, matched_skills = compute_skill_match(resume_skills, job_skills)

            final_score = round((0.6 * tfidf_score + 0.4 * skill_score), 2)

            if final_score >= 70:
                status = "Highly Recommended"
            elif final_score >= 40:
                status = "Consider for Interview"
            else:
                status = "Not a Strong Match"

            name = extract_name(resume_text)
            candidates.append({
                'name': name,
                'filename': resume_file.name,
                'score': final_score,
                'tfidf_score': round(tfidf_score, 2),
                'skill_score': round(skill_score, 2),
                'matched_skills': ', '.join(sorted(matched_skills)),
                'status': status
            })

        ranked_candidates = sorted(candidates, key=lambda x: x['score'], reverse=True)
        request.session['ranked_candidates'] = candidates

        return HttpResponseRedirect(reverse('show_results'))

    return render(request, 'upload.html')

# ✅ PRG GET View to avoid resubmission
def show_results(request):
    candidates = request.session.get('ranked_candidates', [])
    return render(request, 'ranking_result.html', {'candidates': candidates})
