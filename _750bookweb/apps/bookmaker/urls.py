from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template


urlpatterns = patterns("bookmaker.views",
    url(r"^create/$", 'create_update_submission', name="create"),
    url(r"^(?P<nonce>[\da-fA-F-]+)/$", 'review', name="review"),
    url(r"^(?P<nonce>[\da-fA-F-]+)/update/$", 'create_update_submission', name="update"),
    url(r"^(?P<nonce>[\da-fA-F-]+)/add_files/$", 'add_files', name="add_files"),
    url(r"^(?P<nonce>[\da-fA-F-]+)/process/$", 'process', name="process"),
)
