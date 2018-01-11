# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html
import time
from scrapy import signals
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from scrapy.http import HtmlResponse
import requests
from bs4 import BeautifulSoup
import re

class DataSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class SeleniumMiddleware(object):
    """一个selenium中间件，用浏览器代替下载器进行请求，并返回html"""

    def __init__(self):
        self.browser = webdriver.Chrome()
        self.wait = WebDriverWait(self.browser, 20)
        self.browser.get('http://www.czce.com.cn/portal/jysj/qhjysj/mrhq/A09112001index_1.htm')
        self.input_window = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'table tbody input#pubDate')))
        self.button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'table tbody img#button')))

    def process_request(self,request,spider):
        datetime = request.meta['time']
        self.input_window.clear()
        self.input_window.send_keys(datetime)
        self.button.click()
        self.browser.switch_to_window(self.browser.window_handles[-1])
        html = self.browser.page_source
        self.browser.close()
        self.browser.switch_to_window(self.browser.window_handles[0])
        return HtmlResponse(self.browser.current_url,body=html,encoding='utf-8')


class LonglongLoginMiddleware(object):
    """
    用于灵通金属报价网站的登陆，获取cookie，并保存，知道cookie失效再次重新获取。
    """

    def __init__(self):
        self.path = 'C:\\Users\Amos\PycharmProjects\Data\Data\lingtong_cookie'
        with open(self.path) as f:
            content = f.read()
            self.cookie = eval(content)

    def process_request(self,request,spider):
        request.cookies = self.cookie

    # def process_response(self,request,response,spider):
    #     if response.status == 500:
    #         if self.cookie == request.cookies:
    #             self.cookie = {'das':'dsa'}
    #             self.get_cookie()
            # print('cookie失效，重新开始')
            # print('cookie:',request.cookies)
            # print(request.url)
            # new_request = request.copy()
            # new_request.dont_filter = True
            # return new_request
        # else:
        #     return response


