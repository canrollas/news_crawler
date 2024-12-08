# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymongo
import logging


class MongoDBPipeline:
    def __init__(self):
        self.mongo_uri = "mongodb://root:example@mongodb:27017"
        self.database_name = "news_db"

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.database_name]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        collection = self.db[spider.name]
        item_dict = ItemAdapter(item).asdict()
        
        # Check if article with same URL already exists
        existing_item = collection.find_one({"url": item_dict["url"]})
        if existing_item:
            logging.info(f"Article already exists: {item_dict['url']}")
            return item
            
        # Insert if not exists
        collection.insert_one(item_dict)
        logging.info(f"New article added: {item_dict['url']}")
        return item
