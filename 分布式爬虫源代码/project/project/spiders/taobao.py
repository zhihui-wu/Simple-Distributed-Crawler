# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from scrapy_redis.spiders import RedisSpider
from bs4 import BeautifulSoup
import re
import urllib.parse
import requests
import json
import pymongo
from selenium import webdriver


class TaobaoSpider(RedisSpider):
    name = 'taobao'
    #allowed_domains = ['www.shopsearch.taobao.com']
    #start_urls = ['https://shopsearch.taobao.com/search?app=shopsearch&ajax=true']

    client = pymongo.MongoClient('localhost',27017)
    taobao = client['taobao']
    seller_info = taobao['seller_info']
    goods_url = taobao['goods_url']
    goods_info = taobao['goods_info']

    #添加浏览器设置（无图设置）
    chrome_opt = webdriver.ChromeOptions()
    prefs = {"profile.managed_default_content_settings.images" : 2}
    chrome_opt.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(executable_path="E:\wzh\distribute\sourse\chromedriver.exe", chrome_options=chrome_opt)


    def parse(self, response):
        cate = response.text
        data = json.loads(cate)
        c1_list = data['mods']['hotcat']['data']['hotCats']
        cate_list = []
        for c1 in c1_list:
            c2_list = c1['subCats']
            for c2 in c2_list:
                cate = c2['name']
                cate_list.append(cate)
                print(cate)

        for keywords in cate_list:
            nums = range(0, 10020, 20)
            for num in nums:
                self.get_taobao_seller(keywords, num)

    def get_taobao_seller(self,keywords,nums):
        #获取信息
        # 爬取指定数量的店铺信息
        url = "https://shopsearch.taobao.com/search?data-key=s&data-value={0}&ajax=true&_ksTS=1481770098290_1972&callback=jsonp602&app=shopsearch&q={1}&js=1&isb=0".format(nums,keywords)
        # url = "https://shopsearch.taobao.com/search?data-key=s&data-value={0}&ajax=true&callback=jsonp602&app=shopsearch&q={1}".format(nums,keywords)
        wbdata = requests.get(url).text[11:-2]
        data = json.loads(wbdata)
        # print(data)
        # exit()
        shop_list = data['mods']['shoplist']['data']['shopItems']
        for s in shop_list:
            name = s['title'] # 店铺名
            nick = s['nick'] # 卖家昵称
            nid = s['nid'] # 店铺ID
            provcity = s['provcity'] # 店铺区域
            shopUrl = s['shopUrl'] # 店铺链接
            totalsold = s['totalsold'] # 店铺宝贝数量
            procnt = s['procnt'] # 店铺销量
            startFee = s['startFee'] # 未知
            #mainAuction = s['mainAuction'] # 店铺关键词
            userRateUrl = s['userRateUrl'] # 用户评分链接
            dsr = json.loads(s['dsrInfo']['dsrStr'])
            goodratePercent = dsr['sgr']  # 店铺好评率
            srn = dsr['srn'] # 店铺等级
            category = dsr['ind'] # 店铺分类
            mas = dsr['mas'] # 描述相符
            sas = dsr['sas']  # 服务态度
            cas = dsr['cas']  # 物流速度
            data = {
                'name':name,
                'nick':nick,
                'nid':nid,
                'provcity':provcity,
                'shopUrl':shopUrl,
                'totalsold':totalsold,
                'procnt':procnt,
                'startFee':startFee,
                'goodratePercent':goodratePercent,
                # 'mainAuction':mainAuction,
                'userRateUrl':userRateUrl,
                'srn':srn,
                'category':category,
                'mas':mas,
                'sas':sas,
                'cas':cas
            }
            print(data)
            self.seller_info.insert_one(data)
            print("插入数据成功")

        #爬取指定数量的商品详情页url
        url = "https://s.taobao.com/search?data-key=s&data-value={0}&q={1}&ajax=true".format(nums, keywords)
        wbdata = requests.get(url).text
        data = json.loads(wbdata)
        # print(data)
        # exit()
        g_list = data['mods']['itemlist']['data']['auctions']
        for g in g_list:
            g_url = g['detail_url']
            base_url = "https://"
            g_url = urllib.parse.urljoin(base_url, g_url)
            self.driver.get(g_url)
            self.driver.implicitly_wait(3)
            page = self.driver.page_source
            soup = BeautifulSoup(page,'lxml')
            #天猫商品页面
            try:
                tm = self.driver.find_element_by_xpath("//*[@id='J_PromoPrice']/dd/div/span")
                tm_res =  tm.is_displayed()
            except Exception as e:
                tm_res = False
            if tm_res:
                print("天猫商品")
                temp_data = soup.find("div", {"class" : {"tb-detail-hd"}}).h1
                good_name = temp_data.get_text()
                temp_data = soup.find("div", {"class" : {"tm-promo-price"}}).span
                good_price = temp_data.get_text()
                temp_data = soup.find("span", {"class" : {"tb-deliveryAdd"}})
                good_address = temp_data.get_text()

            #淘宝商品页面
            try:
                #tb = driver.find_element_by_xpath("//*[@id='J_PromoPriceNum']")
                tb = self.driver.find_element_by_xpath("// *[ @ id = 'J_StrPriceModBox'] / span")
                tb_res =  tb.is_displayed()
            except Exception as e:
                tb_res = False
            if tb_res:
                print("淘宝商品")
                temp_data = soup.find("h3", {"class" : {"tb-main-title"}})
                good_name = temp_data.get_text()
                try:
                    temp_data = soup.find("em", {"class" : {"tb-rmb-num"}})
                except Exception:
                    temp_data = soup.find("em", {"id": {"J_PromoPriceNum"}})
                good_price = temp_data.get_text()
                try:
                    temp_data = soup.find("span", {"id" : {"J-From"}})
                    good_address = temp_data.get_text()
                except Exception:
                    good_address = False

            if tm_res == False and tb_res == False:
                print("该商品出错")
                continue

            print(good_name)
            print(good_price)
            print(good_address)
            data = {
                'g_url': g_url
            }
            print(data)
            self.goods_url.insert_one(data)
            print("插入数据成功")
            data = {
                'g_url': g_url,
                'good_name': good_name,
                'good_price': good_price,
                'good_address': good_address
            }
            print(data)
            self.goods_info.insert_one(data)
            print("插入数据成功")
