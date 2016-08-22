from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from django.views.generic import View, TemplateView

from upload.forms import UploadImageForm
from upload.upload_image import ImageQueue

# Create your views here.

class IndexUploadView(TemplateView):
    template_name = "upload/index.html"

    def get_context_data(self, *args, **kwargs):
        context = super(IndexUploadView, self).get_context_data(*args, **kwargs)
        # context['something'] = model.objects.all()[:int]
        return context


class IndexUploadPost(View):

    def post(self, request):
        "Handle Images being uploaded and push them to Queue and Storage Blob"
        form = UploadImageForm(request.POST, request.FILES)
        if form.is_valid():
            IQ = ImageQueue()
            IQ.new_image(request.FILES)
            return HttpResponseRedirect('/upload/?success=true')
        else:
            return HttpResponseRedirect('/upload/?success=false')