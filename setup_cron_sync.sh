#!/bin/bash
# Setup cron job to auto-sync team activities every minute

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CRON_COMMAND="* * * * * cd $SCRIPT_DIR && ./auto_sync_activities.sh >> sync.log 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "auto_sync_activities.sh"; then
    echo "Cron job already exists"
else
    # Add cron job
    (crontab -l 2>/dev/null; echo "$CRON_COMMAND") | crontab -
    echo "✓ Added cron job to sync activities every minute"
    echo "Cron job: $CRON_COMMAND"
fi

echo ""
echo "To view current cron jobs: crontab -l"
echo "To remove this cron job: crontab -e (then delete the line)"
echo ""
echo "Activities will now sync automatically every minute!"
