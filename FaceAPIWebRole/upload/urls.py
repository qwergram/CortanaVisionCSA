"""
Definition of urls for FaceAPIWebRole.
"""

from django.conf.urls import include, url
from upload.views import IndexUploadView, IndexUploadPost

urlpatterns = [
    url(r'^$', IndexUploadView.as_view()),
    url(r'^image/$', IndexUploadPost.as_view()),
]