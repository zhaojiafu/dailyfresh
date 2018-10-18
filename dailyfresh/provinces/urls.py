from django.conf.urls import include, url
from provinces import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    url(r'^province$', views.show, name="province"),  # 用户个人信息页

    url(r'^get_all_province$', views.get_all_province, name="get_all_province"),  # 获取所有省份
    url(r'^get_city_by_id$', views.get_city_by_id, name="get_city_by_id"),  # 通过改变的省份获取对应的城市
    url(r'^get_area_by_id$', views.get_area_by_id, name="get_area_by_id"),  # 通过改变的城市获取对应的区/县
]
