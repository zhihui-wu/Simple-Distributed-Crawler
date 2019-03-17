# -*- coding: utf-8 -*-
import requests
import scrapy
from scrapy_redis.spiders import RedisSpider
from scrapy import Selector, Request
import re
import pymongo
from bs4 import BeautifulSoup
from selenium import webdriver



class JdSpider(RedisSpider):
    name = 'jd'
    allowed_domains = ['www.jd.com']
    #start_urls = ['https://www.jd.com/allSort.aspx']

    client = pymongo.MongoClient('localhost', 27017)
    jd = client['jd']
    seller_info = jd['seller_info']
    goods_url = jd['goods_url']
    goods_info = jd['goods_info']

    #添加浏览器设置（无图设置）
    chrome_opt = webdriver.ChromeOptions()
    prefs = {"profile.managed_default_content_settings.images" : 2}
    chrome_opt.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(executable_path="E:\wzh\distribute\sourse\chromedriver.exe", chrome_options=chrome_opt)


    def parse(self, response):
        """获取分类页"""
        selector = Selector(response)
        try:
            texts = selector.xpath('//div[@class="category-item m"]/div[@class="mc"]/div[@class="items"]/dl/dd/a').extract()
            for text in texts:
                items = re.findall(r'<a href="(.*?)" target="_blank">(.*?)</a>', text)
                for item in items:
                    print(item)
                    print(item[0].split('.')[0][2:])
                    #if item[0].split('.')[0][2:] in key_word:
                    if item[0].split('.')[0][2:] != 'list':
                        yield Request(url='https:' + item[0], callback=self.parse)
                    else:
                        # categoriesItem = CategoriesItem()
                        # categoriesItem['name'] = item[1]
                        # categoriesItem['url'] = 'https:' + item[0]
                        # categoriesItem['_id'] = item[0].split('=')[1].split('&')[0]
                        #yield categoriesItem
                        name = item[1]
                        url = 'https:' + item[0]
                        id = item[0].split('=')[1].split('&')[0]
                        print(name)
                        print(url)
                        print(id)
                        self.parse_list(url='https:' + item[0])
                        #yield Request(url='https:' + item[0], callback=self.parse_list)
        except Exception as e:
            print('error:', e)

    def parse_list(self, url):
        """分别获得商品的地址和下一页地址"""
        response = requests.get(url)
        #print('lalalalalalalalalallalalalalalal')
        meta = dict()
        meta['category'] = response.url.split('=')[1].split('&')[0]

        selector = Selector(response)
        texts = selector.xpath('//*[@id="plist"]/ul/li/div/div[@class="p-img"]/a').extract()
        for text in texts:
            items = re.findall(r'<a target="_blank" href="(.*?)">', text)
            print(items)
            self.parse_seller(url='https:' + items[0], meta=meta)
            #yield Request(url='https:' + items[0], callback=self.parse_product, meta=meta)

    def parse_seller(self, url, meta):
        self.driver.get(url)
        self.driver.implicitly_wait(3)
        page = self.driver.page_source


        """分别获得店铺"""
        #response = requests.get(url)
        #print(response.text)
        ids = re.findall(r"venderId:(.*?),\s.*?shopId:'(.*?)',", page)
        if not ids:
            ids = re.findall(r"venderId:(.*?),\s.*?shopId:(.*?),", page)
        vender_id = ids[0][0]
        shop_id = ids[0][1]

        soup = BeautifulSoup(page, 'lxml')
        try:
            temp_name = soup.find("div", {"class" : {"seller-infor"}}).a
            name = temp_name.get_text()
        except Exception:
            name = u'京东自营'
        print(vender_id)
        print(shop_id)
        print(name)
        data = {
            'vender_id':vender_id,
            'shop_id':shop_id,
            'name':name
        }
        print(data)
        self.seller_info.insert_one(data)
        print("插入数据成功")


        """分别获得商品"""
        try:
            #tb = driver.find_element_by_xpath("//*[@id='J_PromoPriceNum']")
            tb = self.driver.find_element_by_xpath("// *[ @ id = 'jd-price']")
            tb_res =  tb.is_displayed()
        except Exception as e:
            print(e)
            tb_res = False
        if tb_res:
            print("商品")
            good_name = ''
            good_address = ''
            good_price = ''
            temp_data = soup.find("div", {"id" : {"itemInfo"}}).div.h1.strings
            for string in temp_data:
                good_name = good_name+string
            print(good_name)
            temp_data = soup.find("div", {"id" : {"summary-service"}}).div.strings
            for string in temp_data:
                good_address = good_address+string
            print(good_address)
            temp_data = soup.find("strong", {"id": {"jd-price"}}).string
            good_price = temp_data
            print(good_price)

        if tb_res == False:
            print("该商品出错")

        print(good_name)
        print(good_price)
        print(good_address)
        data = {
            'url': url
        }
        print(data)
        self.goods_url.insert_one(data)
        print("插入数据成功")
        data = {
            'url': url,
            'good_name': good_name,
            'good_price': good_price,
            'good_address': good_address
        }
        print(data)
        self.goods_info.insert_one(data)
        print("插入数据成功")
