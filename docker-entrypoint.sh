#!/bin/bash

if [ -n "$CRON_SCHEDULE" ]; then
    # Set up environment variables for cron
    printenv | grep -v "no_proxy" >> /etc/environment

    # Process the crontab file with environment variables
    envsubst < /etc/cron.d/app-cron > /etc/cron.d/app-cron.tmp
    sed -i -e 's|\"||g' /etc/cron.d/app-cron
    mv /etc/cron.d/app-cron.tmp /etc/cron.d/app-cron
    chmod 0644 /etc/cron.d/app-cron

    # Install cron job
    crontab /etc/cron.d/app-cron

    # Start cron service
    service cron start

    echo "Cron job installed with schedule: $CRON_SCHEDULE"
    echo "Watching logs..."
    tail -f /var/log/cron.log
else
    echo "No CRON_SCHEDULE set, running script once..."
    python main.py
fi
