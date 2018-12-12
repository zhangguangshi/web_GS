# -*- coding: utf-8 -*-
import scrapy
import json
from ..items import UserItem,UserRelationItem,WeiBoItem
class WeiboSpider(scrapy.Spider):
    name = 'weibo'
    allowed_domains = ['m.weibo.cn']
    # start_urls = ['http://m.weibo.cn/']
    # 用户详情api
    user_url = 'https://m.weibo.cn/api/container/getIndex?uid={uid}&type=uid&value={uid}&containerid=100505{uid}'
    # 用户关注列表api
    follow_url = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_followers_-_{uid}&page={page}'
    # 用户粉丝列表api
    fan_url = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_fans_-_{uid}&page={page}'
    # 用户微博列表api
    weibo_url = 'https://m.weibo.cn/api/container/getIndex?uid={uid}&type=uid&page={page}&containerid=107603{uid}'
    #设置起始用户列表
    #王思聪，uzi，马云,安久拉北鼻
    start_users = ["1826792401","5444117278","2145291155","1642351362"]

    def start_requests(self):
        """
        重新start_requests方法，首先访问起始用户的首页
        :return:
        """
        for uid in self.start_users:
            yield scrapy.Request(url=self.user_url.format(uid=uid),callback=self.parse_user)

    def parse_user(self, response):
        """
        解析用户信息的函数
        :param response:
        :return:
        """
        result = json.loads(response.text)
        #如果获取的ok这个键对应的值是1，则代表用户信息接口访问成功
        if result.get("ok")==1:
            user_info = result.get("data").get("userInfo")
            user_item = UserItem()
            field_map = {
                #用户id
                "id":"id",
                #用户昵称
                "nick_name":"screen_name",
                #头像的url
                "head_img":"profile_image_url",
                #用户性别
                "sex":"gender",
                #用户简介
                "user_des":"description",
                #用户的粉丝数量
                "fans_count":"followers_count",
                #用户的关注数量
                "follows_count":"follow_count",
                #用户的微博数量
                "weibos_count":"statuses_count",
                #用户是否是认证用户
                "is_verified":"verified",
                #用户的认证内容
                "verified_count":"verified_reason"
            }
            for field,attr in field_map.items():
                #user_item["id"]=user_info.get("id")=1642351362
                #user_item["nick_name"]=user_info.get("screen_name")=angelababy
                #.....
                user_item[field]=user_info.get(attr)
            yield user_item
            #根据用户的id，拼接用户关注的api地址
            uid =user_info.get("id")
            yield scrapy.Request(url=self.follow_url.format(uid=uid,page=1),callback=self.parse_follows,meta={"uid":uid,"page":1})
            # 根据用户的id，拼接用户粉丝的api地址
            yield scrapy.Request(url=self.fan_url.format(uid=uid,page=1),callback=self.parse_fans,meta={"uid":uid,"page":1})
            # 根据用户的id，拼接用户微博的api地址
            yield scrapy.Request(url=self.weibo_url.format(uid=uid, page=1), callback=self.parse_weibos,
                                 meta={"uid": uid, "page": 1})


    def parse_follows(self, response):
        """
        解析用户关注的函数
        :param response:
        :return:
        """
        result = json.loads(response.text)
        if result.get("ok")==1:
            #获取用户关注的列表，列表里面嵌套这一个一个的字典，字典里面存放着被关注的人的信息
            follows = result.get("data").get("cards")[-1].get("card_group")
            #获取每一个字典，字典里面存放着被关注的人的信息
            for follow in follows:
                #解析出用户所关注的用户的id，然后再传给parse_user函数进行解析
                uid = follow.get("user").get("id")
                yield scrapy.Request(url=self.user_url.format(uid=uid),callback=self.parse_user)
            uid = response.meta["uid"]
            follows_1 = [{"id":follow.get("user").get("id"),"name":follow.get("user").get("screen_name")} for follow in follows]
            user_relation_item = UserRelationItem()
            user_relation_item["id"]=uid
            user_relation_item["follows"]=follows_1
            user_relation_item["fans"]=[]
            yield user_relation_item
            #获取下一页关注
            page = response.meta["page"]+1
            yield scrapy.Request(url=self.follow_url.format(uid=uid,page=page),callback=self.parse_follows,meta={"page":page,"uid":uid})

    def parse_fans(self,response):
        """
        解析用户粉丝的函数
        :param response:
        :return:
        """
        result = json.loads(response.text)
        if result.get("ok")==1:
            # 获取用户粉丝的列表，列表里面嵌套这一个一个的字典，字典里面存放着粉丝的信息
            fans = result.get("data").get("cards")[-1].get("card_group")
            # 获取每一个字典，字典里面存放粉丝的信息
            for fan in fans:
                uid  =fan.get("user").get("id")
                yield scrapy.Request(url=self.user_url.format(uid=uid),callback=self.parse_user)
            uid = response.meta.get("uid")
            fans_1 = [{"id":fan.get("user").get("id"),"name":fan.get("user").get("screen_name")} for fan in fans]
            user_relation_item = UserRelationItem()
            user_relation_item["id"]=uid
            user_relation_item["fans"]=fans_1
            user_relation_item["follows"]=[]
            yield user_relation_item
            #获取下一页粉丝
            page = response.meta.get("page")+1
            yield scrapy.Request(url=self.fan_url.format(uid=uid,page=page),callback=self.parse_fans,meta={"page":page,"uid":uid})


    def parse_weibos(self,response):
        """
        解析用户微博的函数
        :param response:
        :return:
        """
        result=json.loads(response.text)
        if result.get("ok")==1:
            #获取微博信息所在的列表，列表里面包含着一个个的字典，字典里面包含着微博的详细信息
            weibos = result.get("data").get("cards")

            for weibo in weibos:
                weibo_item = WeiBoItem()
                mblog = weibo.get("mblog")
                if mblog:
                    field_map={
                        #微博id
                        "weibo_id":"id",
                        #微博发布时间
                        "weibo_publish_time":"created_at",
                        #转发数
                        "forward_number":"reposts_count",
                        #评论数
                        "comment_number":"comments_count",
                        #点赞数
                        "like_number":"attitudes_count",
                        #发布来源(使用什么发布的微博)
                        "publish_source":"source",
                        #微博内容
                        "weibo_content":"text"
                    }
                    for field,attr in field_map.items():
                        weibo_item[field]=mblog.get(attr)
                    weibo_item["uid"] = response.meta.get("uid")
                    yield weibo_item
            #获取下一页微博
            uid = response.meta.get("uid")
            page = response.meta.get("page")+1
            yield scrapy.Request(self.weibo_url.format(uid=uid,page=page),callback=self.parse_weibos,meta={"page":page,"uid":uid})

