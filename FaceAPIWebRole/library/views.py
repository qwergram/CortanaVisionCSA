from django.shortcuts import render
from django.views.generic import View, TemplateView

# Create your views here.


class UnsortedImageView(TemplateView):
    template_name = "folder/name.html"

    def get_context_data(self, *args, **kwargs):
        context = super(UnsortedImageView, self).get_context_data(*args, **kwargs)
        return context


class FaceImageView(TemplateView):
    template_name = "samefolder"

    def get_context_data(self, *args, **kwargs):
        context = super(FaceImageView, self).get_context_data(*args, **kwargs)
        return context


class NoFaceImageView(TemplateView):
    template_name = "samefolder"

    def get_context_data(self, *args, **kwargs):
        context = super(NoFaceImageView, self).get_context_data(*args, **kwargs)
        return context