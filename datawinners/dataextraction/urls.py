from django.conf.urls.defaults import patterns
from dataextraction.views import get_for_subject, get_for_form

urlpatterns = patterns('',
    (r'^api/get_for_subject/(?P<subject_type>\w+?)/(?P<subject_id>\w+?)/$', get_for_subject),
    (r'^api/get_for_subject/(?P<subject_type>\w+?)/(?P<subject_id>\w+?)/(?P<start_date>[-0-9]+?)/$', get_for_subject),
    (r'^api/get_for_subject/(?P<subject_type>\w+?)/(?P<subject_id>\w+?)/(?P<start_date>[-0-9]+?)/(?P<end_date>[-0-9]+?)/$', get_for_subject),
    (r'^api/get_for_form/(?P<form_code>\w+?)/$', get_for_form),
    (r'^api/get_for_form/(?P<form_code>\w+?)/(?P<start_date>[-0-9]+?)/(?P<end_date>[-0-9]+?)/$', get_for_form),

)