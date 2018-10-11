from django.conf.urls import include, url
from django.contrib import admin
from user import views

urlpatterns = [
    url(r'^register$', views.RegisterView.as_view(),name="register"),
    # url(r'^register$', views.register,name="register"),

    # url(r'^register_handle$', views.register_handle,name="register_handle"),
]
