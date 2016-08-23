from django.shortcuts import render
from django.views.generic import TemplateView
from secrets import ACCOUNT_KEY, ACCOUNT_NAME
from azure.storage.blob import BlockBlobService

# Create your views here.


def get_urls_from_container(containername):
    blob = BlockBlobService(account_name=ACCOUNT_NAME, account_key=ACCOUNT_KEY)
    return ["https://{}.blob.core.windows.net/{}/{}".format(ACCOUNT_NAME, containername, x.name) for x in blob.list_blobs(containername)]


class UnsortedImageView(TemplateView):
    template_name = "folder/name.html"

    def get_context_data(self, *args, **kwargs):
        context = super(UnsortedImageView, self).get_context_data(*args, **kwargs)
        context['image_list'] = get_urls_from_container('unsorted-images')
        return context


class FaceImageView(TemplateView):
    template_name = "samefolder"

    def get_context_data(self, *args, **kwargs):
        context = super(FaceImageView, self).get_context_data(*args, **kwargs)
        context['image_list'] = get_urls_from_container('has-face-images')
        return context


class NoFaceImageView(TemplateView):
    template_name = "samefolder"

    def get_context_data(self, *args, **kwargs):
        context = super(NoFaceImageView, self).get_context_data(*args, **kwargs)
        context['image_list'] = get_urls_from_container('no-face-images')
        return context