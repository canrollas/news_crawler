import scrapy
import json
import xml.etree.ElementTree as ET
import logging as logger


class SpiegelSpider(scrapy.Spider):
    name = "spiegel"
    allowed_domains = ["spiegel.de"]
    start_urls = ["https://www.spiegel.de/sitemaps/news-de.xml"]

    def parse(self, response):
        logger.info("Parsing Spiegel sitemap")
        root = ET.fromstring(response.text)

        for url in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
            loc = url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text
            news_data = url.find('{http://www.google.com/schemas/sitemap-news/0.9}news')

            if news_data is not None:
                title = news_data.find('{http://www.google.com/schemas/sitemap-news/0.9}title').text
                publication_date = news_data.find('{http://www.google.com/schemas/sitemap-news/0.9}publication_date').text
                keywords = news_data.find('{http://www.google.com/schemas/sitemap-news/0.9}keywords').text if news_data.find('{http://www.google.com/schemas/sitemap-news/0.9}keywords') is not None else ""
                language = news_data.find('{http://www.google.com/schemas/sitemap-news/0.9}publication').find('{http://www.google.com/schemas/sitemap-news/0.9}language').text

                if language != "de":  # Sadece Almanca haberleri işle
                    continue

                logger.info(f"Found article: {title}")
                yield scrapy.Request(
                    loc,
                    callback=self.parse_article,
                    meta={
                        'title': title,
                        'publication_date': publication_date,
                        'keywords': keywords,
                        'language': language
                    }
                )

    def parse_article(self, response):
        title = response.meta.get('title', '')
        publication_date = response.meta.get('publication_date', '')
        keywords = response.meta.get('keywords', '')
        language = response.meta.get('language', '')

        # JSON-LD verisini çek
        json_ld_scripts = response.css('script[type="application/ld+json"]::text').extract()
        news_data = {}
        for script in json_ld_scripts:
            try:
                data = json.loads(script)
                # Eğer JSON bir liste ise her bir elemanı kontrol et
                if isinstance(data, list):
                    for item in data:
                        if item.get('@type') == "NewsArticle":
                            news_data = item
                            break
                elif data.get('@type') == "NewsArticle":  # JSON bir sözlük ise
                    news_data = data
                    break
            except json.JSONDecodeError as e:
                logger.warning(f"JSON parsing error: {e}")
                continue

        # İçerik çekimi
        content = " ".join(response.css("p::text").extract()).replace("\n", " ").replace("\t", " ").replace("\r", " ").strip()

        # Standartlaştırılmış veri yapısı
        standardized_data = {
            "url": response.url,
            "crawled_from": "Der Spiegel",
            "title": news_data.get("headline", title),
            "description": news_data.get("description", ""),
            "language": language,
            "datePublished": news_data.get("datePublished", publication_date),
            "dateModified": news_data.get("dateModified", ""),
            "content": content,
            "publisher": {
                "name": news_data.get("publisher", {}).get("name", "DER SPIEGEL"),
                "logo": news_data.get("publisher", {}).get("logo", {}).get("url", "")
            },
            "author": news_data.get("author", {}).get("name", ""),
            "images": news_data.get("image", []) if "image" in news_data else [],
            "keywords": keywords.split(", ") if keywords else []
        }

        # Veri doğrulama
        if not standardized_data["title"] or not standardized_data["datePublished"]:
            logger.info("Incomplete data, skipping article.")
            return

        logger.info(f"Article parsed: {standardized_data['title']}")
        yield standardized_data
