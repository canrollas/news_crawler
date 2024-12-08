import scrapy


class ElpaisSpider(scrapy.Spider):
    name = "elpais"
    allowed_domains = ["elpais.com"]
    start_urls = ["https://elpais.com"]

    def parse(self, response):
        pass
