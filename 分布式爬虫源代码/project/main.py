from scrapy.cmdline import execute
import sys
import os


# 文件路径
# print(__file__)
# 文件绝对路径
# print(os.path.abspath(__file__))
# 该文件所在目录
# print(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


#execute(["scrapy", "crawl", "taobao"])
execute(["scrapy", "crawl", "news"])
#execute(["scrapy", "crawl", "jd"])
#execute(["scrapy", "crawl", "jobbole"])
