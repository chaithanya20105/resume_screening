from django import forms

class ResumeUploadForm(forms.Form):
    file = forms.FileField()
