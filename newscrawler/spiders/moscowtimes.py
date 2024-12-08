import scrapy
import json
import logging as logger
import xml.etree.ElementTree as ET


class MoscowTimesSpider(scrapy.Spider):
    name = "moscowtimes"
    allowed_domains = ["themoscowtimes.com"]
    start_urls = ["https://www.themoscowtimes.com/rss/news"]

    def parse(self, response):
        logger.info("Parsing The Moscow Times RSS feed")
        root = ET.fromstring(response.text)

        for item in root.findall('.//item'):
            link = item.find('link').text
            title = item.find('title').text
            pub_date = item.find('pubDate').text
            description = item.find('description').text if item.find('description') is not None else ""

            logger.info(f"Found article: {title}")
            yield scrapy.Request(
                link,
                callback=self.parse_article,
                meta={
                    'title': title,
                    'pubDate': pub_date,
                    'description': description
                }
            )

    def parse_article(self, response):
        title = response.meta.get('title', '')
        pub_date = response.meta.get('pubDate', '')
        description = response.meta.get('description', '')

        # JSON-LD verilerini çek
        json_ld_scripts = response.css('script[type="application/ld+json"]::text').extract()
        news_data = {}
        for script in json_ld_scripts:
            try:
                data = json.loads(script)
                if data.get('@type') == "NewsArticle":
                    news_data = data
                    break
            except json.JSONDecodeError as e:
                logger.warning(f"JSON parsing error: {e}")

        # İçerik çekimi
        content = " ".join(response.css("p::text").extract()).replace("\n", " ").replace("\t", " ").replace("\r", " ").strip()

        # Standartlaştırılmış veri yapısı
        standardized_data = {
            "url": response.url,
            "crawled_from": "The Moscow Times",
            "title": news_data.get("headline", title),
            "description": news_data.get("description", description),
            "language": news_data.get("inLanguage", {}).get("name", "en"),
            "datePublished": news_data.get("datePublished", pub_date),
            "dateModified": news_data.get("dateModified", ""),
            "content": content,
            "publisher": {
                "name": news_data.get("publisher", {}).get("name", "The Moscow Times"),
                "logo": news_data.get("publisher", {}).get("logo", {}).get("url", "")
            },
            "author": news_data.get("author", {}).get("name", "The Moscow Times"),
            "images": [news_data.get("image", {}).get("url", "")],
            "keywords": news_data.get("keywords", "").split(", ")
        }

        # Veri doğrulama
        if not standardized_data["title"] or not standardized_data["datePublished"]:
            logger.info("Incomplete data, skipping article.")
            return

        logger.info(f"Article parsed: {standardized_data['title']}")
        yield standardized_data
