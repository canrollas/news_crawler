# Scrapy News Crawler

This project is a web scraping system built with Scrapy that collects news articles from major international news websites (CNN, El País, Le Monde, and Der Spiegel). The scraped data is stored in MongoDB and exposed through a REST API.

## System Architecture

- **Web Scrapers**: Individual Scrapy spiders for each news source that extract article data
- **MongoDB Database**: Stores the scraped articles with deduplication
- **REST API**: Flask-based API to query and retrieve the collected articles
- **Automated Scheduling**: Cron jobs to regularly run the scrapers

## Key Components

### Scrapy Spiders
- Separate spider for each news source (CNN, El País, Le Monde, Der Spiegel)
- Extracts article URLs, headlines, publication dates, and content
- Handles different HTML structures and languages

### MongoDB Pipeline
- Stores scraped articles in separate collections per source
- Prevents duplicate articles by checking URLs
- Maintains article metadata and content

### REST API Endpoints
- `/api/news/recent` - Get most recent articles across all sources
- Supports pagination and sorting by date
- Authentication required via tokens

### Automation
- Docker container with cron scheduling
- Spiders run automatically at configured intervals
- Logging of scraping jobs and errors

## Setup & Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd news-scraper
   ```

2. Create Python virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure MongoDB connection in `pipelines.py`

5. Run individual spiders:
   ```bash
   scrapy crawl <spider_name>
   ```
   Available spiders: cnn, elpais, lemonde, spiegel

6. Or run all spiders via the automation script:
   ```bash
   python run_spiders.py
   ```

The system will collect articles into MongoDB and make them available through the REST API endpoints.
