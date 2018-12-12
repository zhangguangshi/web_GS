# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class WeibospiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class UserItem(scrapy.Item):
    collection = "users"
    id=scrapy.Field()
    nick_name = scrapy.Field()
    head_img = scrapy.Field()
    sex = scrapy.Field()
    user_des = scrapy.Field()
    fans_count = scrapy.Field()
    follows_count = scrapy.Field()
    weibos_count = scrapy.Field()
    is_verified = scrapy.Field()
    verified_count = scrapy.Field()
    follows = scrapy.Field()
    fans =scrapy.Field()
    crawled_time=scrapy.Field()

class UserRelationItem(scrapy.Item):
    collection =  "users"
    #用户id
    id=scrapy.Field()
    #关注列表
    follows = scrapy.Field()
    #粉丝列表
    fans = scrapy.Field()


class WeiBoItem(scrapy.Item):
    collection = "weibos"
    uid = scrapy.Field()
    weibo_id=scrapy.Field()
    weibo_publish_time = scrapy.Field()
    forward_number = scrapy.Field()
    comment_number = scrapy.Field()
    like_number = scrapy.Field()
    publish_source = scrapy.Field()
    weibo_content = scrapy.Field()
    crawled_time = scrapy.Field()





