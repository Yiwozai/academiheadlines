# -*- coding: utf-8 -*-

from django.db import models


class Comment(models.Model):
    """评论模型
    """
    # 评论用户的ID
    user_id = models.IntegerField()
    # 评论内容
    text = models.TextField()
    # 评论时间
    created_time = models.DateTimeField(auto_now_add=True)
    # # 评论文章的ID
    # article_id = models.IntegerField()
    # 评论文章的wanfang id
    # 摈弃数据库返回文章后，以往依照论文ID建立评论模式失效
    # 我们现在从论文的ID入手来建立评论
    article_wanfangid = models.CharField(max_length=50, default='')

    def __str__(self):
        return self.text[:20]

    class Meta:
        db_table = 'comments'
