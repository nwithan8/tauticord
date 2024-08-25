#!/bin/sh

# Delete all /tmp files on container start
echo "Deleting all /tmp files on container start"
rm -rf /tmp/charts/* || true

# Create cron directory
mkdir -p /etc/cron.d

# Cron schedule for cleaning up old files (every hour)
CLEANUP_CRON_SCHEDULE="0 * * * *" # Every hour
CLEANUP_CRON_FILE="/etc/cron.d/cleanup_temp_files"

# Schedule cron job with supplied cron schedule
echo "Scheduling cleanup cron job"
echo "$CLEANUP_CRON_SCHEDULE find /tmp -type f -mmin +60 -delete > /proc/1/fd/1 2>/proc/1/fd/2" > $CLEANUP_CRON_FILE

# Give execution rights on the cron job
chmod 0644 $CLEANUP_CRON_FILE

# Apply cleanup cron job
echo "Applying cleanup cron job"
crontab $CLEANUP_CRON_FILE

# Start cron and start the application
crond && pm2-runtime start ecosystem.config.json
