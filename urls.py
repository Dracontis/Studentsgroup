# ~*~ coding: utf-8 ~*~
from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.views.generic.simple import direct_to_template
from django.views.generic import list_detail
import settings
import views
from studentsgroup.engine_models.models import Group

admin.autodiscover()

group_set = {
    'queryset': Group.objects.all(),
    'template_name': 'base_index.html',
    'template_object_name': 'group',
}

# Pattern for standart urls and addons
urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^ajax_select/', include('ajax_select.urls')),
    url(r'^tinymce/', include('tinymce.urls')),
#    url(r'^grappelli/', include('grappelli.urls')),
)
# Site pattern
urlpatterns += patterns('',
    url(r'(?P<group_id>\d+)/books/$', views.books),
    url(r'(?P<group_id>\d+)/archive/$', views.archive),
    url(r'^(?P<group_id>\d+)/$', views.NewsAndTasks),
    url(r'^(?P<group_id>\d+)/groupauth/$',views.GroupAuth),
    url(r'^(?P<group_id>\d+)/(?P<pagename>\w+[^0-9_])/$', views.NewsAndTasks),
    url(r'^(?P<group_id>\d+)/(?P<pagename>\w+[^0-9_])/page/(?P<page>\w+[^0-9_])/$',views.NewsAndTasks),
    url(r'^(?P<group_id>\d+)/$', views.NewsAndTasks),
    url(r'^(?P<group_id>\d+)/$', views.NewsAndTasks),
    url(r'^(?P<group_id>\d+)/(?P<pagename>\w+[^0-9_])/(?P<message_id>\d+)/$',views.EntryPage),
    url(r'^login/$',views.Login),
    url(r'^logout/$',views.Logout),
    url(r'^about/$',views.About),
    url(r'^$',list_detail.object_list,group_set),
    url(r'^err/$',direct_to_template,{'template':'about.html'})
)
# DEBUG: Pattern for static files in debug mode
"""
urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',{'document_root': settings.MEDIA_ROOT}),
        (r'^static/(?P<path>.*)$', 'django.views.static.serve',{'document_root': settings.STATIC_ROOT}),
)
"""
