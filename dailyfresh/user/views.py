from django.shortcuts import render,redirect,HttpResponseRedirect
from django.http import HttpResponse
import re
from user.models import *
from django.core.urlresolvers import reverse
from django.views.generic import View
from dailyfresh import settings
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer,SignatureExpired,BadSignature
from django.core.mail import send_mail
from django.contrib.auth import authenticate,login
from celery_tasks.tasks import task_send_email
from utils.util import LoginRequiredMixin

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
            return render(request, 'register.html', {'name_error': '用户名必须6~16位'})
        if not re.match(r'^[a-z0-9]*[a-z0-9\w]$', username):
            # 用户名必须是数字和英文字母组成
            return render(request, 'register.html', {'name_error': '用户名必须是数字或英文字母开头'})
        if not 8<=len(pwd) <= 20:
            # 密码必须6位
            return render(request, 'register.html', {'pwd_error': '密码必须8~20位'})
        if not re.match(r'^[a-z0-9]*[a-z0-9]$', pwd):
            # 必须是数字和英文字母组成
            return render(request, 'register.html', {'pwd_error': '密码必须是数字和英文字母组成'})
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

            #加密用户的身份信息，生成激活token
            serialize = Serializer(settings.SECRET_KEY,3600)
            info = {'confirm':user.id}
            token = serialize.dumps(info).decode()
            encryption_url = "http://192.168.12.209:8888/user/active/%s" % token


            # 发邮件
            subject = '天天生鲜欢迎信息'#主题
            message = ''#收件人
            sender = settings.EMAIL_FROM#发件人
            receive =[email]#收件人
            html_message = '<h1>%s,欢迎您成为天天生鲜注册会员</h1>请点击下面链接激活您的账户<br/><a href="%s">%s</a>' % (username,encryption_url,encryption_url)

            task_send_email.delay(subject,message,sender,receive,html_message)


            # 注册成功，跳转登录界面
            # return render(request, "")
            return HttpResponse('请去邮箱激活')


class ActiveView(View):
    '''用户激活'''
    def get(self,request,token):
        '''进行解密'''
        serialize = Serializer(settings.SECRET_KEY, 3600)
        try:
            info = serialize.loads(token)
            #获取待激活的id
            user_id = info['confirm']

            #根据id获取用户信息
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()

            # 跳转到登录界面
            return redirect(reverse('user:login'))
        except SignatureExpired as e:
            # 激活链接已过期
            return HttpResponse('激活链接已过期')
        except BadSignature as e:
            # 激活链接被修改
            return HttpResponse('激活链接非法')


class LoginView(View):
    '''登录'''
    def get(self,request):
        #使用模板
        remember_username = request.COOKIES.get("remember_username","")

        return render(request, "login.html",{"remember_username":remember_username})
    def post(self,request):
        '''进行注册处理'''
        # 接收数据
        username = request.POST.get("username")
        pwd = request.POST.get("pwd")
        remember = request.POST.get("remember")

        #检验用户名是否存在
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None

        if not user:
            # 用户名必须6-16位
            return render(request, 'login.html', {'errors': '用户名不存在'})
        # 获得用户
        user = authenticate(username=username, password=pwd)
        if user is not None:
            if user.is_active:
                '''用户激活'''
                #记住用户登录状态
                login(request,user)

                next_url = request.GET.get("next")

                if next_url:
                    resp = redirect(next_url)
                else:
                    #返回到首页
                    resp = render(request,"index.html")


                #判断是否记住用户名
                if remember:
                    resp.set_cookie("remember_username",username,3600*24*7)
                else:
                    resp.set_cookie("remember_username", username,0)
                return resp
            else:
                return render(request,"login.html",{'errors': '未激活，请去邮箱激活'})
        else:
            return render(request, "login.html",{'errors': '密码错误'})


class UserInfoView(LoginRequiredMixin,View):
    '''用户中心--个人信息'''
    def get(self,request):
        context = {'page':'1'}
        return  render(request, "user_center_info.html",context)


class UserOrderView(LoginRequiredMixin,View):
    '''用户中心--订单'''
    def get(self, request):
        context = {'page': '2'}
        return render(request, "user_center_order.html", context)


class UserAddressView(LoginRequiredMixin,View):
    '''用户中心--收货地址'''
    def get(self, request):
        context = {'page': '3'}
        return render(request, "user_center_site.html", context)























