from django.shortcuts import render, redirect, HttpResponseRedirect
from django.http import HttpResponse
import re
from user.models import *
from django.core.urlresolvers import reverse
from django.views.generic import View
from dailyfresh import settings
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired, BadSignature
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login
from celery_tasks.tasks import task_send_email
from utils.util import LoginRequiredMixin
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import random
from django.conf import settings
from django.contrib.auth import logout


class RegisterView(View):
    '''注册类'''

    def get(self, request):
        '''注册'''
        return render(request, "register.html")

    def post(self, request):
        '''进行注册处理'''
        # 验证码
        validate = request.POST.get("validate_code", '').strip().lower()
        # print(validate,22222)
        # print(request.session.get('validate_code').lower(),3333)
        if validate == '' or validate != request.session.get('validate_code').lower():
            return render(request, 'register.html', {'validate_code_error': '验证码错误'})

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
        if not 8 <= len(pwd) <= 20:
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

            # 加密用户的身份信息，生成激活token
            serialize = Serializer(settings.SECRET_KEY, 3600)
            info = {'confirm': user.id}
            token = serialize.dumps(info).decode()
            encryption_url = "http://192.168.12.209:8888/user/active/%s" % token

            # 发邮件
            subject = '天天生鲜欢迎信息'  # 主题
            message = ''  # 收件人
            sender = settings.EMAIL_FROM  # 发件人
            receive = [email]  # 收件人
            html_message = '<h1>%s,欢迎您成为天天生鲜注册会员</h1>请点击下面链接激活您的账户<br/><a href="%s">%s</a>' % (
            username, encryption_url, encryption_url)

            task_send_email.delay(subject, message, sender, receive, html_message)

            # 注册成功，跳转登录界面
            # return render(request, "")
            return HttpResponse('请去邮箱激活')


class ActiveView(View):
    '''用户激活'''

    def get(self, request, token):
        '''进行解密'''
        serialize = Serializer(settings.SECRET_KEY, 3600)
        try:
            info = serialize.loads(token)
            # 获取待激活的id
            user_id = info['confirm']

            # 根据id获取用户信息
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


class ForgetPasswordView(View):
    '''忘记密码'''

    def get(self, request):
        return render(request, "forget_password.html")

    def post(self, request):
        # 跳转到登录界面
        username = request.POST.get("username")
        email = request.POST.get("email")
        # print(username,email)

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None
        if user:
            if user.email == email:
                # 发送邮件

                # 加密用户的身份信息，生成激活token
                serialize = Serializer(settings.SECRET_KEY, 3600)
                info = {'confirm': user.id}
                token = serialize.dumps(info).decode()
                encryption_url = "http://192.168.12.209:8888/user/update_password/%s" % token

                # 发邮件
                subject = '天天生鲜欢迎信息'  # 主题
                message = ''  # 收件人
                sender = settings.EMAIL_FROM  # 发件人
                receive = [email]  # 收件人
                html_message = '<h1>%s,欢迎您成为天天生鲜注册会员</h1>请点击下面链接修改您的账户密码<br/><a href="%s">%s</a>' % (
                    username, encryption_url, encryption_url)

                task_send_email.delay(subject, message, sender, receive, html_message)

                # 发送成功激活时让is_superuser=1,修改密码之后立即改为0，作为判断是否可以修改密码的依据
                user.is_superuser = 1
                user.save()
                return HttpResponse("请去邮箱进行修改密码")
            else:
                errors = '此邮箱和用户名注册邮箱不匹配'
                return render(request, "forget_password.html", {"errors": errors})
        else:
            errors = '用户名不存在'
            return render(request, "forget_password.html", {"errors": errors})

class UpdatePasswordView(View):
    def get(self, request, token):
        print("get", 111)
        return render(request, "update_password.html")

    def post(self, request, token):
        print("post", 222)
        username = request.POST.get("username")
        pwd = request.POST.get("pwd")
        user = User.objects.get(username=username)
        if user.is_superuser:
            '''进行解密'''
            serialize = Serializer(settings.SECRET_KEY, 3600)
            try:
                info = serialize.loads(token)
                # 获取待激活的id
                user_id = info['confirm']

                # 根据id获取用户信息
                user = User.objects.get(id=user_id)
                user.is_active = 1
                user.is_superuser = 0
                user.set_password(pwd)
                user.save()

                # 跳转到登录界面
                return redirect(reverse('user:login'))
            except SignatureExpired as e:
                # 激活链接已过期
                return HttpResponse('激活链接已过期')
            except BadSignature as e:
                # 激活链接被修改
                return HttpResponse('激活链接非法')
        else:
            errors = "你没有修改密码权限"
            return render(request, "update_password.html", {"errors": errors})




class LoginView(View):
    '''登录'''

    def get(self, request):
        # 使用模板
        remember_username = request.COOKIES.get("remember_username", "")

        return render(request, "login.html", {"remember_username": remember_username})

    def post(self, request):
        '''进行注册处理'''
        # 接收数据
        username = request.POST.get("username")
        pwd = request.POST.get("pwd")
        remember = request.POST.get("remember")

        # 检验用户名是否存在
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
                # 记住用户登录状态
                login(request, user)

                next_url = request.GET.get("next")

                if next_url:
                    resp = redirect(next_url)
                else:
                    # 返回到首页
                    resp = render(request, "index.html")

                # 判断是否记住用户名
                if remember:
                    resp.set_cookie("remember_username", username, 3600 * 24 * 7)
                else:
                    resp.set_cookie("remember_username", username, 0)
                return resp
            else:
                return render(request, "login.html", {'errors': '未激活，请去邮箱激活'})
        else:
            return render(request, "login.html", {'errors': '密码错误'})


class UserInfoView(LoginRequiredMixin, View):
    '''用户中心--个人信息'''

    def get(self, request):
        # context = {'page':'1'}
        user = User.objects.get(username=request.user)
        username = user.username
        address = user.address
        receiver = user.receiver
        postcode = user.postcode
        phone = user.phone
        user1 = {
            "address": address,
            "receiver": receiver,
            "postcode": postcode,
            "phone": phone,
        }

        return render(request, "user_center_info.html", {"user1": user1, 'page': '1'})


class UserOrderView(LoginRequiredMixin, View):
    '''用户中心--订单'''

    def get(self, request):
        context = {'page': '2'}
        return render(request, "user_center_order.html", context)


class UserAddressView(LoginRequiredMixin, View):
    '''用户中心--收货地址'''

    def get(self, request):
        # context = {'page': '3'}
        user = User.objects.get(username=request.user)
        address = user.address
        return render(request, "user_center_site.html", {'page': '3', "address": address})

    def post(self, request):
        receiver = request.POST.get("receiver", '')
        address = request.POST.get("address", '')
        postcode = request.POST.get("postcode", '')
        phone = request.POST.get("phone", '')

        username = request.user
        # print(username,receiver,postcode,address,phone)

        user = User.objects.get(username=username)
        user.address = address
        user.receiver = receiver
        user.postcode = postcode
        user.phone = phone
        user.save()

        return redirect(reverse('user:user'))


class UserCarView(LoginRequiredMixin, View):
    '''用户中心--收货地址'''

    def get(self, request):
        return render(request, "cart.html")


def validate_cod(request):
    # 定义变量，用于画面的背景色、宽、高
    bgcolor = (random.randrange(20, 100), random.randrange(
        20, 100), 255)
    width = 100
    height = 25
    # 创建画面对象
    im = Image.new('RGB', (width, height), bgcolor)
    # 创建画笔对象
    draw = ImageDraw.Draw(im)
    # 调用画笔的point()函数绘制噪点
    for i in range(0, 100):
        xy = (random.randrange(0, width), random.randrange(0, height))
        fill = (random.randrange(0, 255), 255, random.randrange(0, 255))
        draw.point(xy, fill=fill)
    # 定义验证码的备选值
    str1 = 'ABCD123EFGHIJK456LMNOPQRS789TUVWXYZ0'
    # 随机选取4个值作为验证码
    rand_str = ''
    for i in range(0, 4):
        rand_str += str1[random.randrange(0, len(str1))]

    # 把验证码保存到session
    request.session["validate_code"] = rand_str
    print(rand_str, 1111)

    # 构造字体对象
    font = ImageFont.truetype(settings.FOND_STYLE, 20)
    # 构造字体颜色
    fontcolor = (255, random.randrange(0, 255), random.randrange(0, 255))
    # 绘制4个字
    for i in range(4):
        draw.text((5 + 25 * i, 2), rand_str[i], font=font, fill=fontcolor)

    # 释放画笔
    del draw

    # 内存文件操作
    buf = BytesIO()
    # 将图片保存在内存中，文件类型为png
    im.save(buf, 'png')
    # 将内存中的图片数据返回给客户端，MIME类型为图片png
    return HttpResponse(buf.getvalue(), 'image/png')


def index(request):
    return render(request, "index.html")


def logout_view(request):
    logout(request)
    return render(request, 'index.html')
