# -*- coding: utf-8 -*-

from django.conf.urls import url

from . import views

app_name = 'papers'
urlpatterns = [
    url(r'^$', views.home_page, name='home_page'),
    url(r'^archives/$', views.ArchivesView.as_view(), name='archives'),
    url(r'^papers/$', views.PaperView.as_view(), name='paper'),
    url(r'^explore/$', views.explore, name='explore'),
    url(r'^explore_hot/$', views.explore_hot, name='explore_hot'),
    url(r'^attention/$', views.attention, name='attention'),
]
