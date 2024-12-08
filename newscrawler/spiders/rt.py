import scrapy


class RtSpider(scrapy.Spider):
    name = "rt"
    allowed_domains = ["rt.com"]
    start_urls = ["https://rt.com"]

    def parse(self, response):
        pass
