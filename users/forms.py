# -*- coding: utf-8 -*-

from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.template import loader

from django import forms
from .models import User


# 对于表单，每个属性渲染一栏
# UserCreationForm继承自forms.ModelForm， 而ActivationForm继承自forms.From
class RegisterForm(UserCreationForm):

    # 继承类属性，包括密码、密码确认

    class Meta(UserCreationForm.Meta):
        model = User  # 重新指定model属性
        fields = ("username", "email",)  # 覆盖fields属性, 使用自定义字段

    @classmethod
    def send_email(cls, context, to_email, from_email=None,
                   subject_template_name='users/register_activate_subject.txt',
                   email_template_name='users/register_activate_email.html',
                   html_email_template_name=None):
        """发送可附带HTML的邮件
        """
        subject = loader.render_to_string(subject_template_name, context)
        # subject 一定不能包含新行
        subject = ''.join(subject.splitlines())
        boby = loader.render_to_string(email_template_name, context)

        email_message = EmailMultiAlternatives(subject, boby, from_email, [to_email])
        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_email, 'text/html')

        email_message.send()


# 在HTML模板中：
# <label for="id_username">用户名:</label><!-- 对应 {{ field.label_tag }} -->
# <input type="text" name="username" id="id_username" autofocus required maxlength="150" /><!-- 对应 {{ field }} -->
# <p class="help text-small text-muted">必填。150个字符或者更少。</p><!-- 对应 {{ field.help_text }} -->


def validate_email(email):
    try:
        User.objects.get(email=email)
    except Exception:
        raise ValidationError('邮箱账户不存在')


class ActivationForm(forms.Form):
    email = forms.EmailField(label="邮箱",
                             max_length=254,
                             validators=[validate_email],
                             )

    class Meta(object):
        model = User
        fields = ('email',)
