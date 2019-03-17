import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from multiprocessing import Pool
from multiprocessing.dummy import Pool as TheaderPool
import re
import pymongo
import json
import urllib.parse
import logging

client = pymongo.MongoClient('localhost',27017)
jd_seller = client['jd_seller']
seller_info = jd_seller['seller_info']
goods_url = taobao_seller['goods_url']
goods_info = taobao_seller['goods_info']

#添加浏览器设置（无图设置）
chrome_opt = webdriver.ChromeOptions()
prefs = {"profile.managed_default_content_settings.images" : 2}
chrome_opt.add_experimental_option("prefs", prefs)
driver = webdriver.Chrome(executable_path="E:\wzh\distribute\sourse\chromedriver.exe", chrome_options=chrome_opt)

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
    #获取信息
    def get_seller_from_num(nums):
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
            seller_info.insert_one(data)
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
            driver.get(g_url)
            driver.implicitly_wait(3)
            page = driver.page_source
            soup = BeautifulSoup(page,'lxml')
            WebElement linkUsername = driver.findElement(By.xpath("//a[contains(text()," + username + ")]"));
            return linkUsername.isDisplayed();
            try:
                temp_data = soup.find("div", {"class" : {"tb-detail-hd"}}).h1
                good_name = temp_data.get_text()
                temp_data = soup.find("div", {"class" : {"tm-promo-price"}}).span
                good_price = temp_data.get_text()
                temp_data = soup.find("span", {"class" : {"tb-deliveryAdd"}})
                good_address = temp_data.get_text()
            except AttributeError as e:
                temp_data = soup.find("h3", {"class" : {"tb-main-title"}}).h1
                good_name = temp_data.get_text()
                temp_data = soup.find("em", {"class" : {"tb-rmb-num"}})
                good_price = temp_data.get_text()
                temp_data = soup.find("span", {"id" : {"J-From"}})
                good_address = temp_data.get_text()
            except Exception as e:
                logging.exception(e)
                continue
            print(good_name)
            print(good_price)
            print(good_address)
            data = {
                'g_url': g_url
            }
            print(data)
            goods_url.insert_one(data)
            print("插入数据成功")
            data = {
                'g_url': g_url,
                'good_name': good_name,
                'good_price': good_price,
                'good_address': good_address
            }
            print(data)
            goods_info.insert_one(data)
            print("插入数据成功")


    # 多线程执行
    nums = range(0,10020,20)
    for num in nums:
        get_seller_from_num(num)

print("lalalalala")
cate_list = get_taobao_cate()
#print(cate_list)
for keywords in cate_list:
    get_taobao_seller(keywords)