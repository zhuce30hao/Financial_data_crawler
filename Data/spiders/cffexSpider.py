# -*- coding: utf-8 -*-
import scrapy
import time
from xml.etree import ElementTree as ET
from Data.items import DataItem
import math
from Data.utils import select_update_time


class CffexSpider(scrapy.Spider):
    name = 'cffexSpider'
    allowed_domains = ['www.cffex.com.cn']
    start_urls = ['http://www.cffex.com.cn/']
    url = 'http://www.cffex.com.cn/sj/hqsj/rtj/{yearmonth}/{day}/index.xml'
    today_time = time.time()

    def start_requests(self):
        """
        设置初始爬取时间为 2010-01-01 16:00:00 ,以天为单位循环
        这里用的时间戳
        """
        start_time = select_update_time('cffex') + 57600

        while start_time < self.today_time:
            start_time += 86400
            year = time.strftime('%Y', time.localtime(start_time))
            month = time.strftime('%m', time.localtime(start_time))
            day = time.strftime('%d', time.localtime(start_time))
            yield scrapy.Request(self.url.format(yearmonth=year+month,day=day),callback=self.parse,meta={'time':start_time})


    def parse(self, response):
        """判断请求当天是否有数据，并进行解析"""
        if 'error' not in response.url:
            item = DataItem()
            root = ET.fromstring(response.text)
            for group in root.findall('dailydata'):
                item['time'] = time.strftime('%Y-%m-%d', time.localtime(response.meta['time']))
                item['productname'] = group.find('productid').text.strip()
                item['deliverymonth'] = group.find('instrumentid').text.strip()
                openprice = group.find('openprice').text
                item['openprice'] = (openprice.strip() if openprice else None)
                highestprice = group.find('highestprice').text
                item['highestprice'] = (highestprice.strip() if highestprice else None)
                lowestprice = group.find('lowestprice').text
                item['lowestprice'] = (lowestprice.strip() if lowestprice else None)
                item['closeprice'] = group.find('closeprice').text.strip()
                item['presettlementprice'] = group.find('presettlementprice').text.strip()
                item['settlementprice'] = group.find('settlementprice').text.strip()
                item['zd1_chg'] = float(item['closeprice']) - float(item['presettlementprice'])
                item['zd2_chg'] = float(item['settlementprice']) - float(item['presettlementprice'])
                item['volume'] = group.find('volume').text.strip()
                turnover = group.find('turnover').text.strip().split('E')
                item['turnover'] = (turnover if len(turnover)==1 else float(turnover[0])*math.pow(10,int(turnover[1])-4))
                item['openinterest'] = group.find('openinterest').text.strip()
                item['web_name'] = 'cffex'
                yield item


