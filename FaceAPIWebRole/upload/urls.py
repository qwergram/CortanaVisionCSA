"""
Definition of urls for FaceAPIWebRole.
"""

from django.conf.urls import include, url
from upload.views import IndexUploadView

urlpatterns = [
    url(r'^$', IndexUploadView.as_view()),
]