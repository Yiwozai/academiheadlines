# -*- coding: utf-8 -*-

from time import time
from django.views import View
from django.views.generic.edit import FormView
from django.urls import reverse_lazy, reverse
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.sites.shortcuts import get_current_site
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator

from .models import User
from .forms import RegisterForm, ActivationForm


# 新增，收藏文章
def AddFavorite(request, article_id):
    favorite = Favorite.create(user.id, article_id)
    favorite.save()
    return redirect(reverse('papers:paper', kwargs={'article_id': article_id}))


# 新增，添加关注    
def AddFriend(request, friend_id):
    friend = Friend.create(user.id, friend_id)
    friend.save()
    return redirect(reverse('users:profile', kwargs={'user_id': friend_id}))


# 新增，个人主页
def ShowProfile(request, user_id):
    other_user = User.objects.filter(id=user_id)
    favorite_id = Favorite.article_id.filter(user_id=user_id)
    favorite_list = Papers.objects.filter(id=favorite_id)
    friend_id = Friend.friend_id.filter(user_id=user_id)
    friend_list = User.objects.filter(id=friend_id)
    return render(request, 'users/profile.html',
                  context={'other_user': other_user, 'friend_list': friend_list, 'favorite_list': favorite_list})
# return redirect(reverse('users:profile', kwargs={'user': user,'friend_list': friend_list, 'favorite_list': favorite_list}))


class RegisterView(View):
    # 指定表单和模板
    form_class = RegisterForm
    template_name = 'users/register.html'
    # 注册验证使用，内部数据像这样： {username(str): time(int), ...}
    user_regist_confirm_time = {}

    def get(self, request):
        """定义get方法，当请求为GET时触发
        """
        # 当GET请求到来时，首先渲染一个空表单让用户填写
        # 其次寻找是否带来参数next及其值，作为注册成功的跳转页面
        # next及其值作为URL一部分，以'?/next=value'的形式传递
        form = self.form_class()
        redirect_to = request.GET.get('next', '')
        return render(request, self.template_name, context={'form': form, 'next': redirect_to})

    def post(self, request):
        """定义post方法，当请求为POST时触发
        """
        form = self.form_class(request.POST)
        redirect_to = request.POST.get('next', '/')

        # 如果提交数据合法，调用表单的save方法
        # 默认save()后，is_active值会被设置为True
        # 因此需要同时更新is_active值为False
        # 在邮件发送URL确认后，再将该值设置为True
        if form.is_valid():
            form.save()
            userobj = User.objects.get(username=request.POST.get('username'))
            userobj.is_active = False
            userobj.save(update_fields=['is_active'])
            username = userobj.username
            email = userobj.email

            # 用户注册，等待验证
            ciphertext = self.confirm(userobj.username)
            current_site = get_current_site(request)
            site_name = current_site.name
            domain = current_site.domain

            fullurl = '/users/register/confirmfunc/?user=%s&value=%s&next=%s' % (username, ciphertext, redirect_to)
            fullurl = 'http://' + domain + fullurl
            context = {
                'fullurl': fullurl,
                'domain': domain,
                'site_name': site_name,
                'user': userobj,
            }
            self.form_class.send_email(context, email)
            return redirect('/users/register/done/')

        return render(request, self.template_name, context={'form': form, 'next': redirect_to})

    @classmethod
    def confirm(cls, username):
        """验证, 每次有新用户注册时，更新dict
        """
        cls._update_confirm_time(username)

        # 设置类属性dict，组合确认明文、密文
        # 同时将用户名和密文通过URL传递
        plaintext = username + str(cls.user_regist_confirm_time[username])
        ciphertext = make_password(plaintext, None, 'pbkdf2_sha256')
        return ciphertext

    @classmethod
    def _update_confirm_time(cls, username):
        """设置键值对，同时更新dict
        """
        now_time = int(time())
        cls.user_regist_confirm_time[username] = now_time

        # 当时间超过1800秒，删除这个键值对
        # 如果没有人注册，一个键值对存在时间可能是一天或者更久
        # 意味着用户可以用超过一天的确认链接来激活用户
        # 这种情况存在且允许存在
        for key in list(cls.user_regist_confirm_time.keys())[:-1]:
            if now_time - cls.user_regist_confirm_time[key] > 3600:
                del cls.user_regist_confirm_time[key]


def activation(request):
    """发送邮件提醒页面
    """
    return render(request, 'users/register_activation_email_done.html')


def confirmfunc(request):
    """验证逻辑，确认状态后重定向至confirmpage，并不显示任何页面
    """
    user_name = request.GET.get('user', None)
    value = request.GET.get('value', None)
    nextpage = request.GET.get('next', '/')

    if user_name is not None and value is not None:
        try:
            # 从RegisterView类属性获取时间，组合成明文
            plaintext = user_name + str(RegisterView.user_regist_confirm_time[user_name])
        except KeyError:
            return redirect('/users/register/confirm/?state=timeout')
        else:
            # 密文、明文相对应，激活用户同时将用户重定向到登录页面
            # 完成第一次登录后再重定向到点击“注册”的页面，没有则返回主页
            if check_password(plaintext, value):
                userobj = User.objects.get(username=user_name)
                userobj.is_active = True
                userobj.save(update_fields=['is_active'])
                return redirect('/users/register/confirm/?state=done&next=%s' % nextpage)
            else:
                return HttpResponse('Plaintext not correct.')
    # 这种情况出现在未获取到：user_name, value
    else:
        return redirect('/users/register/confirm/?state=urlerror')


def confirm(request):
    """响应验证结果的页面
    """
    state = request.GET.get('state', None)
    nextpage = request.GET.get('next', '/')

    context = {'state': state, 'next': nextpage}
    return render(request, 'users/register_confirm.html', context)


class ActivationView(FormView):
    """新构单独的激活功能
    """
    # 指定表单和模板
    form_class = ActivationForm
    template_name = 'users/register_activation.html'
    success_url = reverse_lazy('users:activation_done')

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super(ActivationView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        email = form.cleaned_data['email']
        userobj = User.objects.get(email=email)
        # print('user: ', userobj)
        # print('email: ', email)
        # print('email: ', userobj.email)
        # print('is_active: ', userobj.is_active)

        userobj.is_active = True
        userobj.save(update_fields=['is_active'])
        return super(ActivationView, self).form_valid(form)


def activationdone(request):
    return render(request, 'users/register_activation_done.html')
