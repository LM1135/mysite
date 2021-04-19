from django.shortcuts import render, redirect, reverse
from .models import User,ConfirmString
from . import forms
import hashlib
import datetime
from django.conf import settings


def hash_code(s, salt='mysite'):
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())
    return h.hexdigest()


def make_confirm_string(user):
    now = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
    code = hash_code(user.username, now)
    ConfirmString.objects.create(code=code, user=user)
    return code


def send_email(email, code):

    from django.core.mail import EmailMultiAlternatives

    subject = '来自www.liujiangblog.com的注册确认邮件'

    text_content = '''感谢注册www.liujiangblog.com，这里是刘江的博客和教程站点，专注于Python、Django和机器学习技术的分享！\
                    如果你看到这条消息，说明你的邮箱服务器不提供HTML链接功能，请联系管理员！'''

    html_content = '''
                    <p>感谢注册<a href="http://{}/confirm/?code={}" target=blank>www.liujiangblog.com</a>，\
                    这里是刘江的博客和教程站点，专注于Python、Django和机器学习技术的分享！</p>
                    <p>请点击站点链接完成注册确认！</p>
                    <p>此链接有效期为{}天！</p>
                    '''.format('127.0.0.1:8000', code, settings.CONFIRM_DAYS)

    msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


# Create your views here.
def index_handler(request):
    # 判断是否登录，未登录
    if not request.session.get('is_login',None):
        # 重定向到登录页面
        return redirect(reverse('user_login'))
        # return redirect(reverse('user_login'))
    # 已登录，进入index页面
    return render(request,'login/index.html')
    # return render(request, 'login/index.html' )


def login_handler(request):
    ''' 从login_2.html 中取数据

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        context = {}
        user_s = User.objects.filter(username=username, password=password)
        if user_s:
            print(username, password)
            return redirect(reverse("user_inder"))
        else:
            context['message'] = '登录信息错误，请输入正确用户名和密码'

    return render(request, 'login/login.html', context)
    '''
    # 不允许重复登录
    if request.session.get('is_login',None):
        return redirect('user_inder')
    if request.method =='POST':
        login_forms = forms.UserForms(request.POST)
        print(login_forms)
        message = '请检查填写的内容'
        # 使用表单类自带的is_valid()方法一步完成数据验证工作
        if login_forms.is_valid():
            username = login_forms.cleaned_data['username']
            password = login_forms.cleaned_data['password']
            try:
                user_s = User.objects.get(username=username)
            except:
                message = '用户不存在'
                return render(request,'login/login.html',locals())
            if not user_s.has_confirmed:
                message = '用户还未邮件确认'
                return render(request,'login/login.html',locals())
            if user_s.password == hash_code(password):
                request.session['is_login']=True
                request.session['user_id'] = user_s.id
                request.session['username'] = user_s.username
                return redirect(reverse('user_inder'))
            else:
                message = '输入的信息不正确，请检查'
                return render(request,'login/login.html',locals())
    login_forms = forms.UserForms()
    return render(request, 'login/login.html', locals())


def register_handler(request):
    # 判断是否已登录，已登录
    if request.session.get('is_login'):
        # 重定向到 index页面
        return redirect(reverse('user_inder'))

    if request.method == 'POST':
        register_form = forms.RegisterForm(request.POST)
        message = '请检查填写的内容'
        if register_form.is_valid():
            username = register_form.cleaned_data['username']
            password1 = register_form.cleaned_data.get('password1')
            password2 = register_form.cleaned_data.get('password2')
            email = register_form.cleaned_data.get('email')
            sex = register_form.cleaned_data.get('sex')
            # 判断密码1与密码2是否相等
            if password1 != password2:
                message = '两次输入的密码不一致'
                return render(request,'login/register.html',locals())
            else:
                # 查看是否已存在用户名
                same_username = User.objects.filter(username=username)
                if same_username:
                    message = '用户名已存在'
                    return render(request,'login/register.html',locals())
                same_email = User.objects.filter(email=email)
                if same_email:
                    message = '邮箱已存在'
                    return render(request,'login/register.html',locals())
                new_user = User()
                new_user.username = username
                new_user.password = hash_code(password1)
                new_user.email = email
                new_user.sex = sex
                new_user.save()
                code = make_confirm_string(new_user)
                send_email(email, code)
                message = '请前往邮箱确认'
                return render(request,'login/confirm.html',locals())
        else:
            return render(request,'login/register.html',locals())
    # 如果是GET请求，返回一个空的表单
    register_form = forms.RegisterForm()
    return render(request,'login/register.html',locals())


def logout_hanger(request):
    # 未登录
    if not request.session.get('is_login',None):
        return redirect(reverse('user_login'))
    request.session.flush()
    return redirect(reverse('user_login'))
    # return redirect('user_login' )


def confirm_hander(request):
    # get 传递code
    code = request.GET.get("code",None)
    message = ''
    try:
        confirm = ConfirmString.objects.get(code=code)
    except:
        message = '无效的确认请求!'
        return render(request, 'login/confirm.html', locals())

    c_time = confirm.create_time
    now = datetime.datetime.now()
    if now > c_time + datetime.timedelta(settings.CONFIRM_DAYS):
        confirm.user.delete()
        message = '您的邮件已经过期！请重新注册!'
        return render(request, 'login/confirm.html', locals())
    else:
        confirm.user.has_confirmed = True
        confirm.user.save()
        confirm.delete()
        message = '感谢确认，请使用账户登录！'
        return render(request, 'login/confirm.html', locals())