import scrapy
import json
import xml.etree.ElementTree as ET
import logging as logger



class CnnSpider(scrapy.Spider):
    name = "cnn"
    allowed_domains = ["edition.cnn.com"]
    start_urls = ["https://edition.cnn.com/sitemap/news.xml"]
    namespaces = {
        '': 'http://www.sitemaps.org/schemas/sitemap/0.9',
        'news': 'http://www.google.com/schemas/sitemap-news/0.9',
        'video': 'http://www.google.com/schemas/sitemap-video/1.1'
    }

    def __init__(self, *args, **kwargs):
        super(CnnSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        logger.info("Parsing XML response")
        root = ET.fromstring(response.text)

        for url in root.findall('url', self.namespaces):
            loc = url.find('loc', self.namespaces).text
            lastmod = url.find('lastmod', self.namespaces).text
            news_title = url.find('news:news/news:title', self.namespaces).text

            logger.info(f"Following URL: {loc}")
            yield scrapy.Request(loc, callback=self.parse_article, meta={'title': news_title, 'lastmod': lastmod})

    def parse_article(self, response):
        title = response.meta['title']
        lastmod = response.meta['lastmod']

        json_ld_script = response.css('script[type="application/ld+json"]::text').get()
        if json_ld_script:
            json_data = json.loads(json_ld_script)

            standardized_data = {
                "url": response.url,
                "title": title,
                "description": json_data[0].get("description"),
                "language": json_data[0].get("inLanguage"),
                "datePublished": json_data[0].get("datePublished"),
                "dateModified": lastmod,
                "publisher": {
                    "name": "CNN",
                    "logo": json_data[0].get("publisher", {}).get("logo")
                },
                "author": [author.get("name") for author in json_data[0].get("author", [])],
                "images": [image.get("url") for image in json_data[0].get("image", []) if "url" in image],
                "videos": [video.get("contentUrl") for video in json_data[0].get("video", []) if "contentUrl" in video]
            }

            yield standardized_data