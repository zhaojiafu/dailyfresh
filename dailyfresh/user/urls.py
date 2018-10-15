from django.conf.urls import include, url
from user import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    # 注册、登录
    url(r'^register$', views.RegisterView.as_view(), name="register"),  # 注册
    url(r'^active/(?P<token>.*)$', views.ActiveView.as_view(), name="active"),  # 帐号激活
    url(r'^login$', views.LoginView.as_view(), name="login"),  # 登录

    #忘记密码
    url(r'^forget_password$', views.ForgetPasswordView.as_view(), name="forget_password"),  # 忘记密码
    url(r'^update_password$', views.UpdatePasswordView.as_view(), name="update_password"),  # 修改密码

    # 验证码
    url(r'^validate_code$', views.validate_cod, name="validate_code"),  # 注册验证码
    #首页
    url(r'^index$', views.index, name="index"),  # 天天生鲜首页
    #退出
    url(r'^logout$', views.logout_view, name="logout"),  # 天天生鲜首页

    # 用户中心三个页面跳转
    # url(r'^$', login_required(views.UserInfoView.as_view()), name="user"),#用户个人信息页
    # url(r'^order$', login_required(views.UserOrderView.as_view()), name="order"),#用户个人订单页
    # url(r'^address$', login_required(views.UserAddressView.as_view()), name="address"),#用户收货地址页

    url(r'^$', views.UserInfoView.as_view(), name="user"),  # 用户个人信息页
    url(r'^order$', views.UserOrderView.as_view(), name="order"),  # 用户个人订单页
    url(r'^address$', views.UserAddressView.as_view(), name="address"),  # 用户收货地址页

    url(r'^car$', views.UserCarView.as_view(), name="car"),  # 用户收货地址页

]
