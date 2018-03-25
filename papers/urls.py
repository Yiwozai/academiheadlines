# -*- coding: utf-8 -*-

from django.conf.urls import url

from . import views

app_name = 'papers'
urlpatterns = [
    url(r'^$', views.home_page, name='home_page'),
    url(r'^archives/$', views.archives, name='archives'),
    url(r'^papers/(?P<article_id>[0-9]+)/$', views.paper, name='paper'),
]
