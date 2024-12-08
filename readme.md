# Scrapy News Crawler

This project is a web scraping tool built using Scrapy, designed to fetch news articles and related data from various
prominent news websites across different languages. The data can be used for data mining, analysis, or other purposes.

## Features

- Crawls news websites in multiple languages (English, Arabic, French, German, Russian, and Spanish).
- Extracts URLs, headlines, publication dates, and content.
- Structured output for easy analysis and processing.
- Modular spiders for each site.

## Prerequisites

- Python 3.7 or higher
- Scrapy framework
- A working internet connection

## Installation

1. Clone the repository:
   ```bash
   git clone repo_url
    cd scrapy-news-crawler
    ```
2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ``` 

3. Install the required packages:
   ```bash
    pip install -r requirements.txt
    ```

4. Run the spider:
   ```bash
   scrapy crawl <spider_name>
   ``` 
   Replace `<spider_name>` with the name of the spider you want to run (e.g., `bbc`, `cnn`, `aljazeera`, etc.).

