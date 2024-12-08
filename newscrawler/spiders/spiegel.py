import scrapy


class SpiegelSpider(scrapy.Spider):
    name = "spiegel"
    allowed_domains = ["spiegel.de"]
    start_urls = ["https://spiegel.de"]

    def parse(self, response):
        pass
