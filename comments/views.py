# -*- coding: utf-8 -*-

from .models import Comment
from .forms import CommentForm
from papers.models import Papers

from django.urls import reverse
from django.views import View
from django.shortcuts import redirect


class CommentView(View):
    """评论逻辑，实现功能且重定向至论文页面
    """
    form_class = CommentForm

    @classmethod
    def get(cls):
        """GET方法重定向到主页
        """
        return redirect('/')

    def post(self, request):
        """POST方法储存评论
        """
        # 从POST数据中获取评论所有信息
        article_id = request.POST.get('article_id', None)
        user_id = request.POST.get('user_id', None)
        text = request.POST.get('text', None)

        # 若数据都存在且合法，则保存到数据库
        if (article_id and user_id and text) and self.form_class(request.POST).is_valid():
            Comment(article_id=article_id, user_id=user_id, text=text).save()
            return redirect(reverse('papers:paper', kwargs={'article_id': article_id}))
        # 检查到数据不合法，重新渲染详情页，并且渲染表单的错误。
        # 因此我们传了2个模板变量给论文页，
        # 一个是论文，一个是表单 form
        else:
            return redirect(reverse('papers:paper', kwargs={
                'article_id': article_id,
                'comment_form': self.form_class(request.POST)
                    }
                )
            )
