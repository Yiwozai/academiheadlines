# -*- coding: utf-8 -*-

import json
from django.db import models


class Papers(models.Model):
    """论文模型
    """
    id = models.IntegerField(primary_key=True)
    dissertation = models.CharField(max_length=100)
    doi = models.CharField(max_length=50)
    author = models.CharField(max_length=50)
    journal = models.CharField(max_length=20)
    journal_date = models.CharField(max_length=10)
    keywords = models.CharField(max_length=90)
    dissertation_en = models.CharField(max_length=150)
    abstract = models.CharField(max_length=1000)
    author_unit = models.CharField(max_length=255)
    author_contact = models.CharField(max_length=100)
    classification = models.CharField(max_length=20)
    keywords_en = models.CharField(max_length=800)
    fund_project = models.CharField(max_length=255)
    abstract_en = models.CharField(max_length=2000)
    author_en = models.CharField(max_length=100)
    journal_en = models.CharField(max_length=100)
    url_id = models.CharField(max_length=50)

    def __str__(self):
        return self.dissertation

    class Meta:
        managed = False
        db_table = 'papers'


# 这两个参数定义了：推荐文章每天的数量、推荐文章最多纪录数量
RECOMMENDED_DAY_LENTH = 10
RECOMMENDED_MAX_LENTH = 140


class Recommended(models.Model):
    """用户推荐类
    """
    # 用户ID作为主键
    # 推荐过的文章ID序列化后作为一个字段
    user_id = models.IntegerField(primary_key=True)
    recommended_papers = models.CharField(max_length=2000, default='')

    class Meta:
        db_table = 'recommended'

    def is_full(self):
        """返回推荐文章是否满队列
        """
        if len(json.loads(self.recommended_papers)) == RECOMMENDED_MAX_LENTH:
            return True
        else:
            return False

    def clear(self):
        """在满队列情况下调用，压出最前每天的数量
        """
        # 这里不采用 堆 的弹出操作，
        # 因为数据需要序列化与反序列化
        # 同时注意：要自行显式调用save()方法
        papers_list = json.loads(self.recommended_papers)[RECOMMENDED_DAY_LENTH:]
        self.recommended_papers = json.dumps(papers_list)
        return None

    def add(self, article_id):
        """为推荐队列添加文章，不判断是否超出长度
           必须在外部清出空间
        """
        papers_list = json.loads(self.recommended_papers)
        papers_list.append(article_id)
        # 注意也要在外部显式调用save()方法
        self.recommended_papers = json.dumps(papers_list)
        return None
