FROM python:3.9-slim

WORKDIR /app

# Install cron and required packages
RUN apt-get update && apt-get install -y cron 
# cron is important to create extensive solution.

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your spider code
COPY . .

# Create the cron job file
RUN echo "0 * * * * cd /app && /usr/local/bin/python /app/run_spiders.py >> /var/log/cron.log 2>&1" > /etc/cron.d/scraping-cron
RUN chmod 0644 /etc/cron.d/scraping-cron

# Apply the cron job
RUN crontab /etc/cron.d/scraping-cron

# Create log file
RUN touch /var/log/cron.log

# Setup entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Use entrypoint script
ENTRYPOINT ["/entrypoint.sh"] 
