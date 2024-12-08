#!/bin/bash
set -e

# Start the cron service
service cron start

# Run spiders once at startup
cd /app && python run_spiders.py

# Keep the container running and tail the logs
tail -f /var/log/cron.log 