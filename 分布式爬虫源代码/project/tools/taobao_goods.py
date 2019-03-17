import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from multiprocessing import Pool
from multiprocessing.dummy import Pool as TheaderPool
import re
import pymongo
import json
import urllib.parse

client = pymongo.MongoClient('localhost',27017)
taobao_seller = client['taobao_seller']
goods_url = taobao_seller['goods_url']
driver = webdriver.Chrome(executable_path="E:\wzh\distribute\sourse\chromedriver.exe")

def get_taobao_cate():
    url = 'https://shopsearch.taobao.com/search?app=shopsearch'
    driver.get(url)
    driver.implicitly_wait(3)
    page = driver.page_source
    soup = BeautifulSoup(page,'lxml')
    cate_name = re.findall(r"q=(.*?)&amp;tracelog=shopsearchnoqcat",str(soup))
    cate_list = []
    for c in cate_name:
        cname = urllib.parse.unquote(c,encoding='gb2312')
        cate_list.append(c)
        print(cname)
    #print(cate_list)
    return cate_list

# 获取淘宝卖家信息
def get_taobao_seller(keywords):
    # 爬取指定数量的店铺信息
    def get_seller_from_num(nums):
        #url = "https://shopsearch.taobao.com/search?data-key=s&data-value={0}&ajax=true&_ksTS=1481770098290_1972&callback=jsonp602&app=shopsearch&q={1}&js=1&isb=0".format(nums,keywords)
        url = "https://s.taobao.com/search?data-key=s&data-value={0}&q={1}&ajax=true".format(nums,keywords)
        wbdata = requests.get(url).text
        data = json.loads(wbdata)
        # print(data)
        # exit()
        g_list = data['mods']['itemlist']['data']['auctions']
        for g in g_list:
            g_url = g['detail_url']
            driver.get(g_url)
            driver.implicitly_wait(3)
            page = driver.page_source
            soup = BeautifulSoup(page,'lxml')
            temp_data = soup.find("div", {"class" : {"tb-detail-hd"}}).h1
            good_name = temp_data.get_text()
            temp_data = soup.find("div", {"class" : {"tm-promo-price"}}).span
            good_price = temp_data.get_text()
            temp_data = soup.find("span", {"class" : {"tb-deliveryAdd"}})
            good_address = temp_data.get_text()
            print(good_name)
            print(good_price)
            print(good_address)
            exit()
            data = {
                'g_url':g_url
            }
            print(data)
            goods_url.insert_one(data)
            print("插入数据成功")

    nums = range(0,10020,20)
    for num in nums:
        get_seller_from_num(num)

print("lalalalala")
cate_list = get_taobao_cate()
#print(cate_list)
for keywords in cate_list:
    get_taobao_seller(keywords)