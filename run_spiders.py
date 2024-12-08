import subprocess
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def run_spiders():
    spiders = ['cnn', 'elpais', 'lemonde', 'spiegel']
    
    logging.info(f"Starting spider run at {datetime.now()}")
    
    for spider in spiders:
        try:
            logging.info(f"Running spider: {spider}")
            subprocess.run(['scrapy', 'crawl', spider], check=True)
            logging.info(f"Successfully completed spider: {spider}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error running spider {spider}: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error with spider {spider}: {str(e)}")
    
    logging.info(f"Completed all spiders at {datetime.now()}")

if __name__ == "__main__":
    run_spiders() 