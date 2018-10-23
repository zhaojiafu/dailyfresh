from django.conf.urls import include, url
from django.contrib import admin
from goods import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(),name="index"),#首页
    url(r'^test$', views.TestView.as_view(),name="test"),#首页

]
