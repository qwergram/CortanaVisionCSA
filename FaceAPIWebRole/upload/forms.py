from django import forms

class UploadImageForm(forms.Form):
    imageupload = forms.ImageField()
