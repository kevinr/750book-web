from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to

from django.contrib import admin
admin.autodiscover()


handler500 = "pinax.views.server_error"


urlpatterns = patterns("",
    url(r"^$", redirect_to, {
        "url": "/bookmaker/create/",
    }, name="home"),
    url(r"^admin/", include(admin.site.urls)),
    url(r"^bookmaker/", include('bookmaker.urls')),
)


if settings.SERVE_MEDIA:
    urlpatterns += patterns("",
        url(r"", include("staticfiles.urls")),
    )
