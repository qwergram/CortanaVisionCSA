"""
Definition of urls for FaceAPIWebRole.
"""

from django.conf.urls import include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

import upload.urls
import library.urls

urlpatterns = [
    # Examples:
    # url(r'^$', FaceAPIWebRole.views.home, name='home'),
    # url(r'^FaceAPIWebRole/', include('FaceAPIWebRole.FaceAPIWebRole.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^upload/', include(upload.urls)),
    url(r'^', include(library.urls)),
]
