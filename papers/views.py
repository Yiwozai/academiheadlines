# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.http import Http404

from comments.models import Comment
from comments.forms import CommentForm
from .models import Papers


def home_page(request):
    """主页
    """
    return render(request, 'papers/home_page.html')


def archives(request):
    """搜索结果页面
    """
    context = {}
    search_target = request.POST['search_target']
    search_article_list = Papers.objects.filter(dissertation__icontains=search_target)[:20]
    context['search_article_list'] = search_article_list
    return render(request, 'papers/archives.html', context=context)


def paper(request, article_id):
    """论文页面
    """
    try:
        # 获取文章、评论
        article = Papers.objects.get(pk=article_id)
        comment_list = Comment.objects.filter(article_id=article_id)
        # 创建评论表单
        comment_form = CommentForm()
        context = {
            'article': article,
            'comment_form': comment_form,
            'comment_list': comment_list
        }
    except Papers.DoesNotExist:
        raise Http404('论文不存在')
    return render(request, 'papers/paper.html', context=context)
