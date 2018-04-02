# -*- coding: utf-8 -*-

import re
import requests
from bs4 import BeautifulSoup

from django.shortcuts import render
from django.http import Http404
from django.views import View

from comments.models import Comment
from comments.forms import CommentForm
from .models import Papers


def home_page(request):
    """主页
    """
    return render(request, 'papers/home_page.html')


# def archives(request):
#     """搜索结果页面, 从数据库返回的简易版本
#     """
#     context = {}
#     search_target = request.POST['search_target']
#     search_article_list = Papers.objects.filter(dissertation__icontains=search_target)[:20]
#     context['search_article_list'] = search_article_list
#     return render(request, 'papers/archives.html', context=context)


class ArchivesView(View):
    """
    搜索结果后返回页面的逻辑。

    在这个项目中，结果返回应当分为两部分：
    一部分直接从自己的数据库返回，另一部分通过实时搜索另一个论文库并清洗返回文章数据。

    这里实现的只是搜索“万方”然后返回数据。(从数据库返回部分已被完全砍掉)
    搜索万方的方式是直接访问URL，不需要POST数据
    """
    template_name = 'papers/archives.html'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/57.0.2987.133 Safari/537.36'}
    wanfang_search_prefix_url = 'http://g.wanfangdata.com.cn/search/searchList.do?searchType=all&searchWord='

    # 清洗页面用到的正则匹配
    regex_dessertation = re.compile(r'\d\.<strong>\[(?:.+?)\]</strong>\s+<a href=(?:.+?)>(.+?)</a>')
    regex_authors = re.compile(r'onclick=\"toAuthor(?:.+?)>(.+?)</a>')
    regex_journal = re.compile(r'<div class="Source">\s+<a href=(?:.+?)\s+target=(?:.+?)>(.+?)</a>')
    regex_journal_date = re.compile(r'- <a href=(?:.+?)>(.+?)</a>')
    regex_abstract = re.compile(r'<div class="summary">摘要：(.+?)</div>')
    regex_keywords = re.compile(r'onclick=\"keywordsKeyUp(?:.+?)\">(.+?)</a>')
    regex_url = re.compile(r'href=\"/link\.do\?url=(.+?)\" target=')

    def _parse_dissertation(self, text):
        """解析出论文名
        """
        dissertation = self.regex_dessertation.search(text)
        assert dissertation is not None, '未找到论文'
        dissertation = re.sub(r'<em>|</em>', '', dissertation.group(1))
        return dissertation

    def _parse_author(self, text):
        """解析出作者
        """
        authors = self.regex_authors.findall(text)
        return authors

    def _parse_journal(self, text):
        """解析出期刊名
        """
        journal = self.regex_journal.search(text)
        try:
            return re.sub(r'<em>|</em>', '', journal.group(1))
        except AttributeError:
            return ''

    def _parse_journal_date(self, text):
        """解析出期刊日期
        """
        journal_date = self.regex_journal_date.search(text)
        try:
            return journal_date.group(1)
        except AttributeError:
            return ''

    def _parse_abstract(self, text):
        """解析出摘要
        """
        abstract = self.regex_abstract.search(text)
        try:
            return re.sub(r'<em>|</em>', '', abstract.group(1))
        except AttributeError:
            return ''

    def _parse_keywords(self, text):
        """解析出关键词
        """
        keywords = self.regex_keywords.findall(text)
        return keywords

    def _parse_url(self, text):
        """解析出url
        """
        url = self.regex_url.search(text)
        assert url is not None, 'URL未找到'
        return url.group(1)

    def _clean(self, html):
        """
        清洗万方返回网页源码，返回需要的数据

        :return: list
        这个list：
        1. 通常情况下长度为20，默认为万方返回长度。（可能会更少，但不会多于20）
        2. 每个元素是一个字典，与一篇论文对应，这个字典有6个键值对：
            {'dissertation': <class 'str'>, 'author': <class 'list'>, 'journal': <class 'str'>,
            'journal_date': <class 'str'>, 'abstract': <class 'str'>, 'keywords': <class 'list'>}
            (请关注每个字段值的类型，以正确调用)
        """
        parsed_doom_tree = BeautifulSoup(html, 'lxml')
        tags = parsed_doom_tree.find_all('div', 'ResultCont')

        # 盛装返回数据
        page_papers_data = []

        for tag in tags:
            tag_string = tag.decode()
            single_paper_data = {}

            # 这是每篇文章的数据，放在一个{}
            single_paper_data['dissertation'] = self._parse_dissertation(tag_string)
            single_paper_data['author'] = self._parse_author(tag_string)
            single_paper_data['journal'] = self._parse_journal(tag_string)
            single_paper_data['journal_date'] = self._parse_journal_date(tag_string)
            single_paper_data['abstract'] = self._parse_abstract(tag_string)
            single_paper_data['keywords'] = self._parse_keywords(tag_string)
            single_paper_data['url'] = self._parse_url(tag_string)
            # 将每篇文章数据添加入要返回的[]
            page_papers_data.append(single_paper_data)

        return page_papers_data

    def get(self, request):
        """定义get方法，当请求为GET时触发
        """
        return render(request, self.template_name, context={'search_article_list': []})

    def post(self, request):
        """定义post方法，当请求为POST时触发
        """
        search_target = request.POST['search_target']

        # XXX: 为了更好适配项目，可将reqeusts.get函数覆盖为自定义方法，加入更多异常控制
        response = requests.get(self.wanfang_search_prefix_url + search_target, headers=self.headers)
        papers = self._clean(response.text)

        return render(request, self.template_name, context={'search_article_list': papers})


# def paper(request, article_id):
#     """论文页面, 从数据库返回的简易版本
#     """
#     try:
#         # 获取文章、评论
#         article = Papers.objects.get(pk=article_id)
#         comment_list = Comment.objects.filter(article_id=article_id)
#         # 创建评论表单
#         comment_form = CommentForm()
#         context = {
#             'article': article,
#             'comment_form': comment_form,
#             'comment_list': comment_list
#         }
#     except Papers.DoesNotExist:
#         raise Http404('论文页面未找到')
#     return render(request, 'papers/paper.html', context=context)


class PaperView(View):
    """点击搜索结果页面中文章后返回的“论文页面”
    """

    template_name = 'papers/paper.html'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/57.0.2987.133 Safari/537.36'}
    wanfang_paper_prefix_url = 'http://g.wanfangdata.com.cn/link.do?url='

    regex_dissetation = re.compile(r'<font style="font-weight:bold;">(.+?)</font>')
    regex_dissetation_en = re.compile(r'<div class="English">(.+?)</div>')
    regex_doi = re.compile(r'onclick=\"toDoi\(\'(?:.+?)\',\'(.+?)\'\)')
    regex_abstract = re.compile(
        r'<div class="abstract">.+?<textarea rows="" cols="" style="display: none;">(.+?)</textarea>', re.S)
    regex_abstract_en = re.compile(
        r'<div class="abstract_title"(?:.+?)</div>(?:\s+)<div  id="abstract_content"(?:.+?)>(.+?)</div>', re.S)
    regex_author = re.compile(
        r'class=\"info_right_name\" onclick="authorHome\(\'(?:\w+)\',\'(?:\d*)\',\'(?:\d*)\',\'(\w+)\'')
    regex_author_unit = re.compile(r'onclick=\"searchResult\(\'perio\',\'作者单位:(.+?)\'\)')
    regex_journal = re.compile(r'class=\"college\" onclick=\"(?:.+?)\">(\w+)</a>')
    regex_journal_en = re.compile(r'onclick=\"toJournal(?:.+?)\">(.+?)</a>')
    regex_journal_date = re.compile(r'onclick=\"seeInfo(?:.+?)>(.+?)</a>')
    regex_classification = re.compile(r'分类号：</div><div(?:.+?)>(.+?)</div>', re.S)
    regex_keywords = re.compile(r'onclick=\"searchResult\(\'perio\',\'关键词:(.+?)\'\)')
    regex_fund_project = re.compile(r'onclick=\"fundProgram\(\'(.+?)\'\)')

    def _parse_dissertation(self, text):
        """解析论文题目
        """
        dissertation = self.regex_dissetation.search(text)
        assert dissertation is not None, '未找到论文名'
        return dissertation.group(1).strip()

    def _parse_dissertation_en(self, text):
        """解析论文英文题目
        """
        try:
            return self.regex_dissetation_en.search(text).group(1).strip()
        except AttributeError:
            return ''

    def _parse_doi(self, text):
        """解析doi
        """
        try:
            return self.regex_doi.search(text).group(1)
        except AttributeError:
            return ''

    def _parse_abstract(self, text):
        """解析摘要
        """
        try:
            return self.regex_abstract.search(text).group(1).strip()
        except AttributeError:
            return ''

    def _parse_abstract_en(self, text):
        """解析英文摘要
        """
        try:
            return self.regex_abstract_en.search(text).group(1).strip()
        except AttributeError:
            return ''

    def _parse_author(self, text):
        """解析作者名
        """
        author = self.regex_author.findall(text)
        return author

    def _parse_author_unit(self, text):
        """解析作者单位
        """
        author_unit = self.regex_author_unit.findall(text)
        return author_unit

    def _parse_journal(self, text):
        """解析期刊名
        """
        try:
            return self.regex_journal.search(text).group(1)
        except AttributeError:
            return ''

    def _parse_journal_en(self, text):
        """解析期刊英文名
        """
        try:
            return self.regex_journal_en.search(text).group(1)
        except AttributeError:
            return ''

    def _parse_journal_date(self, text):
        """解析期刊年卷期
        """
        try:
            date = self.regex_journal_date.search(text).group(1)
            return date.strip()
        except AttributeError:
            return ''

    def _parse_classification(self, text):
        """解析分类号
        """
        try:
            return self.regex_classification.search(text).group(1).strip()
        except AttributeError:
            return ''

    def _parse_keywords(self, text):
        """解析关键词
        """
        try:
            keywords = self.regex_keywords.findall(text)
            lenth = int(len(keywords) / 2)
            return keywords[:lenth]
        except AttributeError:
            return []

    def _parse_keywords_en(self, text):
        """解析英文关键词
        """
        try:
            keywords_en = self.regex_keywords.findall(text)
            lenth = int(len(keywords_en) / 2)
            return keywords_en[lenth:]
        except AttributeError:
            return []

    def _parse_fund_project(self, text):
        """解析基金项目
        """
        try:
            return self.regex_fund_project.findall(text)
        except AttributeError:
            return []

    def _clean(self, html):
        """
        清洗万方返回网页源码，返回需要的数据

        :return: dict
        共计14组键值对：除 fund_project, keywords_en, keywords, author, author_unit 5组值为list，其他均为str
        """
        paper_info = {}

        paper_info['dissertation'] = self._parse_dissertation(html)
        paper_info['dissertation_en'] = self._parse_dissertation_en(html)
        paper_info['doi'] = self._parse_doi(html)
        paper_info['abstract'] = self._parse_abstract(html)
        paper_info['abstract_en'] = self._parse_abstract_en(html)
        paper_info['author'] = self._parse_author(html)
        paper_info['author_unit'] = self._parse_author_unit(html)
        paper_info['journal'] = self._parse_journal(html)
        paper_info['journal_en'] = self._parse_journal_en(html)
        paper_info['journal_date'] = self._parse_journal_date(html)
        paper_info['classification'] = self._parse_classification(html)
        paper_info['keywords'] = self._parse_keywords(html)
        paper_info['keywords_en'] = self._parse_keywords_en(html)
        paper_info['fund_project'] = self._parse_fund_project(html)

        return paper_info

    def get(self, request):
        wanfang_url = request.GET.get('url', None)
        if wanfang_url is None:
            return Http404('论文页面未找到')

        # XXX: 为了更好适配项目，可将reqeusts.get函数覆盖为自定义方法，加入更多异常控制
        response = requests.get(self.wanfang_paper_prefix_url + wanfang_url, headers=self.headers)
        url_id = response.url.split('=')[-1]
        print('url_id:', url_id)

        # 这个页面的三大块在这返回：
        # 论文的信息、评论列表和评论表单
        paper_info = self._clean(response.text)
        comment_list = Comment.objects.filter(article_wanfangid=url_id)
        comment_form = CommentForm()
        context = {
            'article': paper_info,
            'comment_form': comment_form,
            'comment_list': comment_list
        }

        return render(request, self.template_name, context=context)
