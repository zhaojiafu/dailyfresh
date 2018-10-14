from django.conf.urls import include, url
from user import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    # 注册、登录
    url(r'^register$', views.RegisterView.as_view(), name="register"),  # 注册
    url(r'^active/(?P<token>.*)$', views.ActiveView.as_view(), name="active"),  # 帐号激活
    url(r'^login$', views.LoginView.as_view(), name="login"),  # 登录

    # 用户中心三个页面跳转
    # url(r'^$', login_required(views.UserInfoView.as_view()), name="user"),#用户个人信息页
    # url(r'^order$', login_required(views.UserOrderView.as_view()), name="order"),#用户个人订单页
    # url(r'^address$', login_required(views.UserAddressView.as_view()), name="address"),#用户收货地址页

    url(r'^$', views.UserInfoView.as_view(), name="user"),  # 用户个人信息页
    url(r'^order$', views.UserOrderView.as_view(), name="order"),  # 用户个人订单页
    url(r'^address$', views.UserAddressView.as_view(), name="address"),  # 用户收货地址页

]
