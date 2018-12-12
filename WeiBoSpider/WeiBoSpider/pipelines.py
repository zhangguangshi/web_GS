# -*- coding: utf-8 -*-

# Define your item pipelines here

# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from .items import UserItem,UserRelationItem,WeiBoItem
import time
import pymongo
class WeibospiderPipeline(object):
    def process_item(self, item, spider):
        return item

#定义一个处理爬取时间的pipeline
class TimePipeline(object):
    def process_item(self,item,spider):
        if isinstance(item,UserItem) or isinstance(item,WeiBoItem):
            now = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
            item["crawled_time"]=now
        return item

#定义一个存储数据的pipeline
class MongoPipeline(object):
    def __init__(self,host,port,db):
        self.mongo_host=host
        self.mongo_port = port
        self.mongo_db = db
    @classmethod
    def from_crawler(cls,crawler):
        return cls(host=crawler.settings.get("MONGO_HOST"),port=crawler.settings.get("MONGO_PORT"),db=crawler.settings.get("MONG0_DB"))

    def open_spider(self,spider):
        self.client = pymongo.MongoClient(host=self.mongo_host,port=self.mongo_port)
        self.db=self.client[self.mongo_db]

    def process_item(self,item,spider):
        if isinstance(item,UserItem):
            #UserItem--->self.db["users"]
            #WeiBoItem-->self.db["weibos"]
            #update()方法，第一个参数是查询条件({"id":item.get("id")}),第二个参数是爬取的item，使用$set操作符，如果爬取到的是重复的数据则对数据进行更新操作，同时不会删除已经存在的字段。第三个参数设置为True，如果数据不存在则插入数据。这样就可以做到数据存在即更新数据，数据不存在即插入数据，从而达到去重的效果。
            self.db[item.collection].update_one({"id":item.get("id")},{"$set":item},True)
        elif isinstance(item,WeiBoItem):
            self.db[item.collection].update_one({"id": item.get("weibo_id")},{"$set":item},True)
        elif isinstance(item,UserRelationItem):
            #UserRelationItem---->self.db["users"]
            #$addToSet,这个操作符可以向列表类型的字段插入数据的同时进行去重，它的值就是需要操作的字段名称。$each操作符对需要插入的列表进行遍历，以逐条插入用户的关注或者粉丝到指定的字段。
            self.db[item.collection].update_one(
                {"id":item.get("id")},
                {"$addToSet":
                    {
                    #follows，fans是UserItem里面的follows和fans这两个字段
                    #item["follows"]--->UserRelationItem中follows
                    #item["fans"]----->UserRelationItem中fans
                    "follows":{"$each":item["follows"]},
                    "fans":{"$each":item["fans"]}
                    }
                },
                True
            )
        return item

    def close_spider(self,spider):
        self.client.close()

