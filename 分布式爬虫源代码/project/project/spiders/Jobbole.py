# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from scrapy.http import Request

import pymongo
import datetime
import newspaper
import jieba
import urllib
import re

from newspaper import Article
from snownlp import SnowNLP



class JobboleSpider(RedisSpider):
    name = 'jobbole'

    client = pymongo.MongoClient('localhost',27017)
    news = client['news']
    news_info = news['news_info']

    def parse(self, response):
        global web_name
        is_professional, web_name = self.url_deff(response.url )
        # 给定一个初始首页，提取其中的相关具体页面：
        print('******************************提取文章页面的url：**********************************************************\n')
        # 将memoize_articles设为 False 阻止自动记录已爬取过的网页
        cnn_paper2 = newspaper.build(response.url, language='zh', memoize_articles=False)
        articles = cnn_paper2.articles
        # 环球新闻部分article页面url会返回类似于 http://www.huanqiu.com/weaponlist/aircraft/list_0_0_0_0_0_0_4 的错误url
        # 或 http://epaper.jinghua.cn/html/2016-07/18/node_100.htm 这样的外网链接
        # 可通过查找有无 .html 和 url中是否包含网站名（如people）字段来判断是否为正确的文章页面 url 和 外网链接
        # 但鉴于某些外网链接也是新闻的文章详情页面，对后面的提取操作来说，是没有影响的，所以这里忽略，即将其当作当前网站的一部分
        # 但对于qq新闻这类域名不同的网站来说，因为我的策略是通过域名来判断是否是新闻页面，所以可能会被自动屏蔽，不必担心
        for article in articles:
            # 判断是否是专业的新闻网站
            if is_professional:
                if web_name not in article.url:
                    articles.remove(article)
                    continue
            else:
                if "news" not in article.url:
                    articles.remove(article)
                    continue
            # 判断 url 是否有效：
            try:
                if not urllib.request.urlopen(article.url).getcode():
                    articles.remove(article)
                    continue
                else:
                    print(article.url)
                    # # 一边提取url，一边提取文章信息：
                    #self.store_to_mysql(article.url)
                    yield Request(url=article.url, callback=self.store_to_mysql)
            except urllib.error.HTTPError as e:
                articles.remove(article)
                continue
            except Exception as ee:
                articles.remove(article)
                continue

        print('***********************************categeary***********************************************\n')
        categorys = cnn_paper2.categories
        for category in categorys:
            print(category.url)


    #过滤不合法url
    def url_deff(self, url):
        is_professional = None
        # 判断专业与非专业的新闻网站域名：
        if "www." not in url:
            # 非专业的新闻门户:只要判断每个url中是否有 news 关键字即可
            is_professional = False
            if "news" in url:
                pass
        else:
            # 专业的新闻门户
            is_professional = True
            web_name = re.match(r'.*www.(.*).com.*', url).group()[0]  # 提取出网站名，防止非文章页被提取而数据出错
        return is_professional, web_name


    def store_to_mysql(self, response):
        # newspaper提取文章相关内容（文章详情页）：（目前newspaper可以对中文页面做简单的提取，部分功能运用到中文页面会失效）
        a = Article(response.url, language='zh')  # chinese
        a.download(response.body)
        a.parse()
        print('---------------title---------------------------------------')
        title = a.title
        text = a.text
        #  判断 title 是否为空，若为空，将其填充：
        if title == "":
            # title = re.match(r'(.*)。.*', text).groups()[0]
            title = text.summary(1)
        print(title)
        print('---------------text---------------------------------------')
        print(text[:100])

        print('---------------------meta_description--(文章摘要)----------------------------------')
        meta_description = a.meta_description
        print(meta_description)

        print('====================================+++++snowNPL+++++=========================================')
        # 用snowNLP进行关键字提取（优化newspaper的关键字泛滥问题）：（缺点：提取速度较慢）
        s = SnowNLP(text)
        keyword5 = s.keywords(5)    # 可自行决定关键字数量
        print('关键词：')
        print(keyword5)

        data = {
            'title': title,
            'meta_description': meta_description,
            'keyword5': keyword5,
            'text': text
        }
        print(data)
        self.news_info.insert_one(data)
        print("插入数据成功")

