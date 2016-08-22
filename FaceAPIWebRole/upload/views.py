from django.shortcuts import render
from django.views.generic import View, TemplateView

# Create your views here.

class IndexUploadView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, *args, **kwargs):
        context = super(IndexUploadView, self).get_context_data(*args, **kwargs)
        # context['something'] = model.objects.all()[:int]
        return context