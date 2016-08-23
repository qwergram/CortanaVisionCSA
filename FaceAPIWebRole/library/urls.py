from django.conf.urls import include, url
from library.views import FaceImageView, UnsortedImageView, NoFaceImageView

urlpatterns = [
    url(r'^$', FaceImageView.as_view()),
    url(r'unsorted/$', UnsortedImageView.as_view()),
    url(r'noface/$', NoFaceImageView.as_view()),
]