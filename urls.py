from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^private_files/', include('private_files.urls')),
    url(r'^accounts/', include('registration.urls')),
)

urlpatterns += patterns('common.views',
    url(r'^$', 'index', name='index'),
    url(r'^dashboard/$', 'dashboard', name='dashboard'),

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
    url(r'^categories/$', 'index_category', name='category-index'),
    url(r'^categories/new$', 'create_category', name='category-create'),
    url(r'^categories/(?P<category_id>\d+)/edit/$', 'update_category', name='category-update'),

    url(r'^publishers/$', 'index_publisher',
        name='publication-index-publisher'),
    url(r'^publishers/new/$', 'create_publisher',
        name='publication-create-publisher'),
    url(r'^publishers/(?P<id>\d+)/$', 'show_publisher',
        name='publication-show-publisher'),
    url(r'^publishers/(?P<id>\d+)/edit/$', 'update_publisher',
        name='publication-update-publisher'),
    url(r'^publishers/(?P<id>\d+)/dashboard/$', 'publisher_dashboard',
        name='publication-publisher-dashboard'),
    url(r'^publishers/(?P<id>\d+)/team/$', 'publisher_team',
        name='publication-publisher-team'),

    url(r'^publishers/(?P<publisher_id>\d+)/books/$', 'index_book',
        name='publication-index-book'),
    url(r'^publishers/(?P<publisher_id>\d+)/books/new/$', 'create_book',
        name='publication-create-book'),
    url(r'^publishers/(?P<publisher_id>\d+)/books/(?P<book_id>\d+)/$',
        'show_book', name='publication-show-book'),
    url(r'^publishers/(?P<publisher_id>\d+)/books/(?P<book_id>\d+)/edit/$',
        'update_book', name='publication-update-book'),
    url(r'^publishers/(?P<publisher_id>\d+)/books/(?P<book_id>\d+)/delete/$',
        'delete_book', name='publication-delete-book'),
    url(r'^publishers/(?P<publisher_id>\d+)/books/(?P<book_id>\d+)/status/edit/$',
        'update_book_status', name='publication-update-book-status'),
    url(r'^publishers/(?P<publisher_id>\d+)/books/(?P<book_id>\d+)/toc/$',
        'manage_book_toc', name='publication-manage-book-toc'),

    url(r'^publishers/(?P<publisher_id>\d+)/periodicals/$',
        'index_periodical', name='publication-index-periodical'),
    url(r'^publishers/(?P<publisher_id>\d+)/periodicals/new/$',
        'create_periodical', name='publication-create-periodical'),
    url(r'^publishers/(?P<publisher_id>\d+)/periodicals/(?P<periodical_id>\d+)/$',
        'show_periodical', name='publication-show-periodical'),
    url(r'^publishers/(?P<publisher_id>\d+)/periodicals/(?P<periodical_id>\d+)/edit/$',
        'update_periodical', name='publication-update-periodical'),

    url(r'^publishers/(?P<publisher_id>\d+)/periodicals/(?P<periodical_id>\d+)/issues/$',
        'index_issue', name='publication-index-issue'),
    url(r'^publishers/(?P<publisher_id>\d+)/periodicals/(?P<periodical_id>\d+)/issues/new/$',
        'create_issue', name='publication-create-issue'),
    url(r'^publishers/(?P<publisher_id>\d+)/periodicals/(?P<periodical_id>\d+)/issues/(?P<issue_id>\d+)/$',
        'show_issue', name='publication-show-issue'),
    url(r'^publishers/(?P<publisher_id>\d+)/periodicals/(?P<periodical_id>\d+)/issues/(?P<issue_id>\d+)/edit/$',
        'update_issue', name='publication-update-issue'),
    url(r'^publishers/(?P<publisher_id>\d+)/periodicals/(?P<periodical_id>\d+)/issues/(?P<issue_id>\d+)/delete/$',
        'delete_issue', name='publication-delete-issue'),
    url(r'^publishers/(?P<publisher_id>\d+)/periodicals/(?P<periodical_id>\d+)/issues/(?P<issue_id>\d+)/status/edit/$',
        'update_issue_status', name='publication-update-issue-status'),
    url(r'^publishers/(?P<publisher_id>\d+)/periodicals/(?P<periodical_id>\d+)/issues/(?P<issue_id>\d+)/toc/$',
        'manage_issue_toc', name='publication-manage-issue-toc'),
)

#urlpatterns += patterns('discovery.views',
#    url(r'^/$', '', name=''),
#)

#urlpatterns += patterns('statistic.views',
#    url(r'^/$', '', name=''),
#)

if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    from django.views.generic.simple import redirect_to

    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}),
        (r'^favicon\.ico$', redirect_to, {'url': 'static/img/favicon.ico'}),
    )
