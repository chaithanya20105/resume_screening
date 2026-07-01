import os
import docx2txt
import PyPDF2

from django.shortcuts import render, redirect
from .forms import ResumeUploadForm
from .models import Resume, JobDescription

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import nltk
from nltk.corpus import stopwords

# Ensure NLTK resources are available
nltk.download('punkt')
nltk.download('stopwords')

def extract_text_from_file(uploaded_file):
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    
    if ext == '.pdf':
        reader = PyPDF2.PdfReader(uploaded_file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
        return text
    
    elif ext == '.docx':
        return docx2txt.process(uploaded_file)
    
    else:
        return ''  # Unsupported file

def preprocess_text(text):
    tokens = nltk.word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    filtered = [word for word in tokens if word.isalnum() and word not in stop_words]
    return ' '.join(filtered)

def upload_resume(request):
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            resume_text = extract_text_from_file(uploaded_file)
            processed_resume = preprocess_text(resume_text)

            job_description = JobDescription.objects.first()
            if not job_description:
                return render(request, 'upload_resume.html', {
                    'form': form,
                    'error': 'No job description available.'
                })

            processed_job = preprocess_text(job_description.description)

            vectorizer = TfidfVectorizer()
            vectors = vectorizer.fit_transform([processed_resume, processed_job])
            score = cosine_similarity(vectors[0:1], vectors[1:2])[0][0] * 100

            Resume.objects.create(
                file=uploaded_file,
                text=resume_text,
                score=round(score, 2)
            )

            return redirect('upload_success')
    else:
        form = ResumeUploadForm()

    return render(request, 'upload_resume.html', {'form': form})

def upload_success(request):
    return render(request, 'upload_success.html')
