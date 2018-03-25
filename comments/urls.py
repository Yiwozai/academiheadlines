from django.conf.urls import url

from . import views

app_name = 'comments'
urlpatterns = [
    url(r'^papers$', views.CommentView.as_view(), name='comment'),
]
