# -*- coding: utf-8 -*-

from django.conf.urls import url
from . import views


app_name = 'users'
urlpatterns = [
    url(r'^register/confirm/', views.confirm, name='confirm'),
    url(r'^register/confirmfunc/', views.confirmfunc, name='confirmfunc'),
    url(r'^register/done/', views.activation),
    url(r'^register/', views.RegisterView.as_view(), name='register'),
    url(r'^activate/', views.ActivationView.as_view(), name='activation'),
    url(r'^activate/done', views.activationdone, name='activation_done'),
    # 新增，收藏文章
    url(r'^favorite/$', views.AddFavorite, name='favorite'),
    # 新增，添加关注（好友）
    url(r'^friend/$', views.AddFriend, name='friend'),
    # 新增，个人主页
    url(r'^profile/(?P<user_id>[0-9]+)/$', views.ShowProfile, name='profile'),
]
