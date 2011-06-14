from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

admin.autodiscover()

urlpatterns = patterns('',
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    (r'^accounts/', include('registration.urls')),
)

urlpatterns += patterns('core.views',
    url(r'^$', 'home', name='home'),
)

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
