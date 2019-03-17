import re
import redis

def depart(url_list):
    list = ('taobao.com', '1688.com', 'jd.com', 'nuomi.com', 'tmall.com',
            'meituan.com', 'vip.com', 'dangdang.com','etao.com',
            'xmeise.com', 'suning.com', 'hc360.com', 'yhd.com', 'vmall.com',
            'maigoo.com', 'alibaba.com', 'wbiao.cn', 'amazon.com', '51sole.com',
            'gome.com.cn', 'kongfz.com', 'lemall.com', 'jumei.com', 'damai.cn',
            'jiaoyimao.com')
    len(list)
    print("total:")
    print(len(url_list))

    goods = []
    news = []
    i = 0

    for url in url_list:
        m = re.match(r".*[com|cn]/", url)
        temp_url = m.group(0)
        #print(temp_url)
        #print(i)
        i = i + 1
        statue = 0
        for web in list:
            if web in temp_url:
                goods.append(temp_url)
                statue = 1
                module(web)
                break
        if statue == 0:
            news.append(temp_url)

    print("*************************************************")
    
    print("电商网站")
    print(len(goods))
    for val in goods:
        print(val)

    print("*************************************************")

    print("新闻博客类")
    print(len(news))
    for val in news:
        print(val)
        r.lpush("news:start_urls", val)


def module(web):
    if web == 'taobao.com':
        r.lpush("taobao:start_urls", 'https://shopsearch.taobao.com/search?app=shopsearch&ajax=true')
    if web == 'jd.com':
        r.lpush("jd:start_urls", 'https://www.jd.com/allSort.aspx')













r = redis.StrictRedis(host = 'localhost', port = 6379, db=0)

url_list = ['https://taobao.com/',
            'http://news.xinhuanet.com/politics/2017-06/05/c_129624876.htm',
            'http://news.xinhuanet.com/comments/2017-06/04/c_1121075078_4.htm',
            'http://people.com.cn/',
            'http://edu.people.com.cn/',
            'http://jd.com/',
            'http://www.techweb.com.cn/internet/2017-06-05/2531140.shtml',
            'http://tech.ifeng.com/listpage/26334/1/list.shtml',
            'http://www.huanqiu.com/']

depart(url_list)













