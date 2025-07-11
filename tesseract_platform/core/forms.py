from django import forms

class DocumentUploadForm(forms.Form):
    file = forms.FileField(label='Выберите файл')
