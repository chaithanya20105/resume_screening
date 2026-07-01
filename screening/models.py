from django.db import models

class JobDescription(models.Model):
    title = models.CharField(max_length=200)
    keywords = models.TextField(help_text="Comma-separated list of keywords")

    def __str__(self):
        return self.title

class Resume(models.Model):
    candidate_name = models.CharField(max_length=200)
    file = models.FileField(upload_to='resumes/')
    extracted_text = models.TextField(blank=True, null=True)
    score = models.FloatField(default=0.0)

    def __str__(self):
        return self.candidate_name
