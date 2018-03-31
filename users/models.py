# -*- coding: utf-8 -*-

from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import AbstractBaseUser, UserManager

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.validators import UnicodeUsernameValidator


class User(AbstractBaseUser):
    """
    用户模型，继承基类用户后有：

    password, last_login, username, email, is_active, unit, area, labels共计8个字段
    """
    username_validator = UnicodeUsernameValidator()
    objects = UserManager()

    # 用户名
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    # 邮箱
    email = models.EmailField(_('email address'),
                              unique=True,
                              error_messages={
                                  'unique': "该邮箱地址已被占用。",
        },
    )
    # 是否激活
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    # 机构、学校
    unit = models.CharField('机构/学校', max_length=150, default='')
    # 领域、方向
    area = models.CharField('领域/方向', max_length=150, default='')
    # 关键词、标签（相关性推荐用）
    labels = models.CharField('标签', max_length=150, default='')

    EMAIL_FIELD = 'email'  # 描述模型中邮件字段的名称，该值可由get_email_field_name()返回
    USERNAME_FIELD = 'username'  # 这是唯一标识符字段的名称，字段必须是唯一的（即在其定义中设置unique=True）
    REQUIRED_FIELDS = ['email']  # 当通过createsuperuser管理命令创建用户时，提示用户给列表里面的每个字段提供一个值

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = '用户'

    def clean(self):
        """先继承父类
        """
        super(User, self).clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def email_user(self, subject, message, from_email=None, **kwargs):
        """给该用户发送邮件
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)


# 新增，收藏文章
class Favorite(models.Model):
    user_id = models.IntegerField()
    article_id = models.IntegerField()

    @classmethod
    def create(cls, user_id, article_id):
        favorite = cls(user_id=user_id, article_id=article_id)
        return favorite

    class Meta:
        db_table = 'favorite'
        
        
# 新增，好友。注意，好友只是单向的关注
class Friend(models.Model):
    user_id = models.IntegerField()  # 发出关注动作的用户
    friend_id = models.IntegerField()  # 被关注的用户

    @classmethod
    def create(cls, user_id, friend_id):
        friend = cls(user_id=user_id, friend_id=friend_id)
        return friend

    class Meta:
        db_table = 'friend'
