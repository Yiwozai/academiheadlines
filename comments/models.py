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
    # 评论文章的ID
    article_id = models.IntegerField()

    def __str__(self):
        return self.text[:20]

    class Meta:
        pass
        # db_table = 'comments'
