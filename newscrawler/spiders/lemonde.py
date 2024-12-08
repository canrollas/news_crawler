import scrapy
import json
import xml.etree.ElementTree as ET
import logging as logger


class LemondeSpider(scrapy.Spider):
    name = "lemonde"
    allowed_domains = ["lemonde.fr"]
    start_urls = ["https://www.lemonde.fr/sitemap_news.xml"]

    def parse(self, response):
        logger.info("Parsing sitemap")
        root = ET.fromstring(response.text)

        for url in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
            loc = url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text
            lastmod = url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod').text

            news_data = url.find('{http://www.google.com/schemas/sitemap-news/0.9}news')
            if news_data is not None:
                publication_date = news_data.find('{http://www.google.com/schemas/sitemap-news/0.9}publication_date').text
                title = news_data.find('{http://www.google.com/schemas/sitemap-news/0.9}title').text
                language = news_data.find('{http://www.google.com/schemas/sitemap-news/0.9}publication').find('{http://www.google.com/schemas/sitemap-news/0.9}language').text

                logger.info(f"Found article: {title}")
                yield scrapy.Request(
                    loc,
                    callback=self.parse_article,
                    meta={
                        'title': title,
                        'datePublished': publication_date,
                        'lastmod': lastmod,
                        'language': language
                    }
                )

    def parse_article(self, response):
        title = response.meta.get('title', '')
        date_published = response.meta.get('datePublished', '')
        lastmod = response.meta.get('lastmod', '')
        language = response.meta.get('language', '')

        # Haber sayfasındaki JSON-LD verisini çek
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

        # Haber içeriği
        content = " ".join(response.css("p::text").extract())
        content = content.replace("\n", " ").replace("\t", " ").replace("\r", " ")
        content = " ".join(content.split())  # Fazla boşlukları temizle

        # Standartlaştırılmış veri yapısı
        standardized_data = {
            "url": response.url,
            "crawled_from": "Le Monde",
            "title": news_data.get("headline", title),
            "description": news_data.get("description", ""),
            "language": language,
            "datePublished": news_data.get("datePublished", date_published),
            "dateModified": news_data.get("dateModified", lastmod),
            "content": content,
            "publisher": {
                "name": news_data.get("publisher", {}).get("name", "Le Monde"),
                "logo": news_data.get("publisher", {}).get("logo", {}).get("url", "")
            },
            "author": [author.get("name", "") for author in news_data.get("author", [])] if "author" in news_data else [],
            "images": [news_data.get("image", {}).get("url", "")],
            "videos": [],
            "keywords": news_data.get("keywords", [])
        }

        # Veri doğrulama
        if not standardized_data["title"] or not standardized_data["datePublished"]:
            logger.info("Incomplete data, skipping article.")
            return

        logger.info(f"Article parsed: {standardized_data['title']}")
        yield standardized_data
