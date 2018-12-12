# -*- coding: utf-8 -*-
from scrapy import signals
from fake_useragent import UserAgent
import requests
import json
class RandomUserAgentMiddleware(object):
    def __init__(self,random_type="random"):
        self.ua_type = random_type
        self.ua = UserAgent(verify_ssl=False)
    @classmethod
    def from_crawler(cls,crawler):
        return cls(random_type=crawler.settings.get("RANDOM_TYPE"))
    def process_request(self,request,spider):
        def get_ua():
            return getattr(self.ua, self.ua_type)
        request.headers["User-Agent"] =get_ua()
        return None
        # request.headers.setdefault('User_Agent', get_ua())


class RandomIPMiddleware(object):
    def __init__(self,proxy_url):
        self.proxy_url = proxy_url
    @classmethod
    def from_crawler(cls,crawler):
        return cls(proxy_url=crawler.settings.get("PROXY_POOL_URL"))
    def get_proxy(self):
        try:
            response = requests.get(self.proxy_url)
            if response.status_code==200:
                proxy = response.text
                return proxy
        except Exception as e:
            return None
    def process_request(self,request,spider):
        proxy = self.get_proxy()
        print("获取到的IP是:",proxy)
        if proxy:
            proxy_url = "http://{}".format(proxy)
            request.meta["proxy"]=proxy_url


class RandomCookieMiddleware(object):
    def __init__(self,cookie_url):
        self.cookie_url = cookie_url
    @classmethod
    def from_crawler(cls,crawler):
        return cls(cookie_url=crawler.settings.get("COOKIE_POOL_URL"))

    def get_cookie(self):
        try:
            response = requests.get(self.cookie_url)
            if response.status_code==200:
                cookie = response.text
                print("获取到的cookie是:",cookie)
                return cookie
        except Exception as e:
            return None



    def process_request(self,request,spider):
        cookies = self.get_cookie()
        cookies = json.loads(cookies)
        request.cookies = cookies





