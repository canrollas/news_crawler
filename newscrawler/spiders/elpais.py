import scrapy
import json
import xml.etree.ElementTree as ET
import logging as logger

class ElpaisSpider(scrapy.Spider):
    name = "elpais"
    allowed_domains = ["elpais.com"]
    start_urls = ["https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada"]



    def parse(self, response):
        logger.info("Parsing RSS feed")
        root = ET.fromstring(response.text)
        for item in root.findall('.//item'):
            link = item.find('link').text
            title = item.find('title').text
            pub_date = item.find('pubDate').text if item.find('pubDate') is not None else None
            description = item.find('description').text if item.find('description') is not None else None

            logger.info(f"Following URL: {link}")
            yield scrapy.Request(
                link,
                callback=self.parse_article,
                meta={'title': title, 'pub_date': pub_date, 'description': description}
            )

    def parse_article(self, response):
        title = response.meta.get('title', '')
        pub_date = response.meta.get('pub_date', '')
        description = response.meta.get('description', '')

        # JSON-LD veri çekimi
        json_ld_script = response.css('script[type="application/ld+json"]::text').get()
        json_data = {}
        if json_ld_script:
            try:
                json_data = json.loads(json_ld_script)
                # Eğer json_data bir liste ise, ilk öğeyi al
                if isinstance(json_data, list):
                    json_data = json_data[0]
            except json.JSONDecodeError as e:
                logger.warning(f"JSON parsing error: {e}")
                return

        # Haber içeriği
        content = " ".join(response.css("p::text").extract())
        content = content.replace("\n", " ").replace("\t", " ").replace("\r", " ")
        content = " ".join(content.split())  # Fazla boşlukları temizle

        # Standartlaştırılmış veri yapısı
        standardized_data = {
            "url": response.url,
            "crawled_from": "El País",
            "title": title,
            "description": json_data.get("description", description),
            "language": json_data.get("inLanguage", ""),
            "datePublished": json_data.get("datePublished", pub_date),
            "dateModified": json_data.get("dateModified", ""),
            "content": content,
            "publisher": {
                "name": json_data.get("publisher", {}).get("name", "El País"),
                "logo": json_data.get("publisher", {}).get("logo", "")
            },
            "author": [author.get("name", "") for author in json_data.get("author", [])],
            "images": json_data.get("image", {}).get("url", []),
            "videos": json_data.get("video", {}).get("contentUrl", []),
            "keywords": json_data.get("keywords", [])
        }

        # Veri doğrulama
        if not standardized_data["description"] or not standardized_data["datePublished"]:
            logger.info("Incomplete data, skipping article.")
            return

        logger.info(f"Article parsed: {standardized_data['title']}")
        yield standardized_data

