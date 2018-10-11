from django.shortcuts import render,redirect
from django.http import HttpResponse
import re
from user.models import User
from django.core.urlresolvers import reverse
from django.views.generic import View

class RegisterView(View):
    '''注册类'''
    def get(self,request):
        '''注册'''
        return render(request, "register.html")

    def post(self,request):
        '''进行注册处理'''
        # 接收数据
        username = request.POST.get("user_name").lower().strip()
        pwd = request.POST.get("pwd").strip()
        cpwd = request.POST.get("cpwd").strip()
        email = request.POST.get("email").strip()
        allow = request.POST.get("allow")

        if not allow:
            # 没有同意协议
            return render(request, 'register.html', {'allow_error': '请同意协议'})
        if not all([username, pwd, cpwd, email, allow]):
            # 数据不完整
            return render(request, 'register.html', {'errmsg': '数据不完整'})
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None

        if user:
            # 用户名必须6-16位
            return render(request, 'register.html', {'name_error': '用户名已经存在'})

        if not 6 <= len(username) <= 16:
            # 用户名必须6-16位
            return render(request, 'register.html', {'name_error': '用户名必须6-16位'})
        if not re.match(r'^[a-z0-9]*[a-z0-9]$', username):
            # 用户名必须是数字和英文字母组成
            return render(request, 'register.html', {'name_error': '用户名必须是数字和英文字母组成'})
        if not len(pwd) == 6:
            # 密码必须6位
            return render(request, 'register.html', {'pwd_error': '密码必须6位'})
        if not re.match(r'^[a-z0-9]*[a-z0-9]$', pwd):
            # 必须是数字和英文字母组成
            return render(request, 'register.html', {'pwd_error': '必须是数字和英文字母组成'})
        if not pwd == cpwd:
            # 俩次密码不一致
            return render(request, 'register.html', {'pwd_error': '俩次密码不一致', 'cpwd_error': '俩次密码不一致'})
        if not (re.match(r'^[a-z0-9][\w]*@[a-z0-9]+(\.[a-z]{2,5}){1,2}$', email)):
            # 邮箱格式错误
            return render(request, 'register.html', {'email_error': '邮箱格式错误'})


        else:
            # 进行业务处理，进行用户注册
            user = User.objects.create_user(username, email, pwd)
            user.is_active = 0
            user.save()
            # 注册成功，跳转登录界面
            # return render(request, "")
            print(1)
            return redirect(reverse('goods:index'))


