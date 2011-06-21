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

urlpatterns += patterns('common.views',
    url(r'^$', 'index', name='index'),
    url(r'^dashboard/$', 'dashboard', name='dashboard'),
    url(r'^settings/$', 'setting', name='setting'),

    #(r'^membership/', include('membership.urls')),
    #(r'^subscription/', include('subscription.urls')),
    #(r'^publication/', include('publication.urls')),
    #(r'^discovery/', include('discovery.urls')),
    #(r'^statistic/', include('statistic.urls')),
)

urlpatterns += patterns('membership.views',
    url(r'^settings/account/$', 'setting', name='membership-setting'),
)

#urlpatterns += patterns('subscription.views',
#    url(r'^/$', '', name=''),
#)

urlpatterns += patterns('publication.views',
    url(r'^publication/upload/$', 'upload_publication', name='publication-upload'),

    url(r'^publisher/new/$', 'create_publisher', name='publication-create-publisher'),
    url(r'^publisher/(?P<id>\d+)/$', 'show_publisher', name='publication-show-publisher'),
    url(r'^publisher/(?P<id>\d+)/edit/$', 'update_publisher', name='publication-update-publisher'),
)

#urlpatterns += patterns('discovery.views',
#    url(r'^/$', '', name=''),
#)

#urlpatterns += patterns('statistic.views',
#    url(r'^/$', '', name=''),
#)

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
