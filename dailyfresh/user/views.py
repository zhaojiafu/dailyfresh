from django.shortcuts import render, redirect, HttpResponseRedirect
from django.http import HttpResponse, JsonResponse
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
from django.core import serializers


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
        # print(user.id, 111)
        try:
            # print("try", 222, user.id)
            user_id = user.id
            address = Address.objects.get(user_id=user_id, is_default=True,is_delete=0)
            # print(address.user_id, 222333)
            user1 = {
                "address": address.addr,
                "receiver": address.receiver,
                "phone": address.phone,
            }
        except Address.DoesNotExist:
            # print("except", 3333)
            user1 = {
                "address": '无默认地址',
                "receiver": '无默认地址',
                "phone": '无默认地址',
            }
        # print("except", 444)

        return render(request, "user_center_info.html", {"user1": user1, 'page': '1'})


class UserOrderView(LoginRequiredMixin, View):
    '''用户中心--订单'''

    def get(self, request):
        context = {'page': '2'}
        return render(request, "user_center_order.html", context)


class UserAddressView(LoginRequiredMixin, View):
    '''用户中心--收货地址'''
    def get(self, request):
        # 获得当前用户对象
        user = User.objects.get(username=request.user)
        # 检验当前地址是否存在
        try:
            address = Address.objects.get(user_id=user.id, is_default=True)
            addr = address.addr
        except Address.DoesNotExist:
            addr = '无默认地址'

        return render(request, "user_center_site.html", {'page': '3', "addr": addr})

    def post(self, request):
        # 接收新增地址信息
        receiver = request.POST.get("receiver",1)
        addre = request.POST.get("address",1)
        postcode = request.POST.get("postcode",1)
        phone = request.POST.get("phone",1)
        province_id = request.POST.get("province_id",1)
        city_id = request.POST.get("city_id",1)
        area_id = request.POST.get("area_id",1)
        # 检验获取输入的类型
        # print(province_id, city_id, area_id, "省市区")
        # print("province_id",province_id,type(province_id))
        # print("city_id",city_id,type(city_id))
        print("receiver",receiver,type(receiver))
        # print("addre",area_id,type(addre))
        # print("postcode",area_id,type(postcode))
        # print("phone",area_id,type(phone))

        '''检验# 检验数据是否填写'''
        if province_id=='0'and city_id=='0'and area_id=='0':

            return render(request, "user_center_site.html", {"errors": "省市区数据不完整"})
            # print("if")
        if receiver=='':
            return render(request, "user_center_site.html", {"errors": "收货人未填写"})
        if addre=='':
            return render(request, "user_center_site.html", {"errors": "详细地址未填写"})
        if phone=='':
            return render(request, "user_center_site.html", {"errors": "收货人电话不能为空"})
        if postcode=='':
            return render(request, "user_center_site.html", {"errors": "邮编未填写"})

        # 获得当前用户对象
        user = User.objects.get(username=request.user)

        # 检验当前地址是否存在
        try:
            address = Address.objects.get(user_id=user.id, is_default=True)
            address.is_default = False
            address.save()
        except Address.DoesNotExist:
            pass

        # 拼接地址字符串
        addres = province_id + '---' + city_id + '---' + area_id + '/街道:  /' + addre

        # 添加地址
        Address.objects.create(
            user_id=user.id,
            receiver=receiver,
            addr=addres,
            phone=phone,
            postcode=postcode,
            is_default=True
        )

        return redirect(reverse('user:user'))


def address_show(request):
    return render(request, "user_address_all.html", {'page': '1'})


class UserAddressAllView(LoginRequiredMixin, View):
    '''用户中心--收货地址'''

    def get(self, request):
        # 获得当前用户对象
        user = User.objects.get(username=request.user)
        # 检验当前地址是否存在
        try:
            address_list = Address.objects.filter(user_id=user.id,is_delete=0)
        except Address.DoesNotExist:
            address_list = '无地址'

        content_info = {
            'address_list': serializers.serialize('json', address_list),
        }

        # print(content_info)
        return JsonResponse(content_info)

def remove_addr(request,Rmpk):
    print(type(Rmpk),Rmpk,111)

    pk = int(Rmpk)
    a = 2
    print(type(a),a,"aaa")
    print(type(pk),pk,222)
    try:
        address = Address.objects.get(id=pk)
        addr = 1
        address.is_delete = 1
        address.save()
        # address.delete()#从数据库删除,一般不用此方法
    except Address.DoesNotExist:
        addr = 0

    return redirect(reverse("user:address_show"))




class UpdateAddress(LoginRequiredMixin, View):
    def get(self,request,Uppk):
        # 测试第一次是method类型
        # print("get", 111)
        # 获得当前用户对象
        user = User.objects.get(username=request.user)
        # 检验当前地址是否存在
        try:
            address = Address.objects.get(user_id=user.id, is_default=True)
            addr = address.addr
        except Address.DoesNotExist:
            addr = '无默认地址'

        # 测试参数类型
        pk = int(Uppk)
        # print(type(pk), pk)

        address = Address.objects.get(id=pk)
        receiver = address.receiver
        phone = address.phone
        addr = address.addr
        postcode = address.postcode
        #分割地址,获取省市区后面的地址
        addr1 = addr.split('/街道:  /')
        addr2 = addr1[1]
        content1={
            "receiver":receiver,
            "phone":phone,
            'page': '3',
            "addr1": addr2,
            "postcode":postcode,
            "addr":addr

        }

        return render(request, "user_center_site.html", content1)

    def post(self,request,Uppk):
        # print("post",222)
        #获取地址对象
        pk = int(Uppk)
        address = Address.objects.get(id=pk)

        #接收修改后的数据
        receiver = request.POST.get("receiver", 1)
        addre = request.POST.get("address", 1)
        postcode = request.POST.get("postcode", 1)
        phone = request.POST.get("phone", 1)
        province_id = request.POST.get("province_id", 1)
        city_id = request.POST.get("city_id", 1)
        area_id = request.POST.get("area_id", 1)
        print("receiver:",receiver,type(receiver),address.receiver)
        if receiver!='':
            address.receiver=receiver
        if postcode!='':
            address.postcode=postcode
        if phone!='':
            address.phone=phone
        if province_id!='0' or city_id !='0' or area_id!='0' or addre!='' :
            # 获取并分割原来的地址
            addr1 = address.addr
            addr2 = addr1.split('---')
            addr_split0=addr2[0]
            addr_split1=addr2[1]
            addr3=addr2[2].split('/街道:  /')
            addr_split2 = addr3[0]
            addr_split3 = addr3[1]
            if province_id!='0':
                addr_split0 = province_id
            if city_id!='0':
                addr_split1 = city_id
            if area_id!='0':
                addr_split2 = area_id
            if addre!='':
                addr_split3 = addre
            addre_new = addr_split0+'---'+addr_split1+'---'+addr_split2+'/街道:  /'+addr_split3
            address.addr = addre_new
        #保存修改内容到数据库
        address.save()


        # 获得当前用户对象
        user = User.objects.get(username=request.user)
        # 检验当前地址是否存在
        try:
            address = Address.objects.get(user_id=user.id, is_default=True)
            addr = address.addr
        except Address.DoesNotExist:
            addr = '无默认地址'
        cont={
            'page': '3',
            "addr":addr,
        }

        return render(request, "user_center_site.html", cont)

class UpdateDefault(LoginRequiredMixin, View):
    def get(self,request,Updefault):
        #获取地址user_id
        pk = int(Updefault)
        address = Address.objects.get(id=pk)
        userid = address.user_id
        address_list = Address.objects.filter(user_id=userid)
        for i in address_list:
            i.is_default = 0
            i.save()
        address.is_default=1
        address.save()

        return redirect(reverse('user:address_show'))


    def post(self,request,Updefault):
        return HttpResponse("post")




class UserCarView(LoginRequiredMixin, View):
    '''用户--我的购物车'''

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
