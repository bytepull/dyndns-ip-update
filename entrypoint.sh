#!/bin/bash
set -e

# Validate configuration
: "${DYNDNS_DOMAIN:?DYNDNS_DOMAIN is required}"
: "${DYNDNS_USERNAME:?DYNDNS_USERNAME is required}"
: "${DYNDNS_PASSWORD:?DYNDNS_PASSWORD is required}"

# Default schedule: every 5 minutes
CRON_SCHEDULE="${CRON_SCHEDULE:-*/5 * * * *}"

# Validate schedule format (five fields, safe characters)
if ! [[ "$CRON_SCHEDULE" =~ ^[0-9*/,-]+[[:space:]]+[0-9*/,-]+[[:space:]]+[0-9*/,-]+[[:space:]]+[0-9*/,-]+[[:space:]]+[0-9*/,-]+$ ]]; then
    echo "ERROR: Invalid CRON_SCHEDULE"
    exit 1
fi

# Export environment variables for cron.
# Use Python shell quoting to safely handle special characters.
python - <<'PY'
import os
import shlex

keys = [
    "DYNDNS_DOMAIN",
    "DYNDNS_USERNAME",
    "DYNDNS_PASSWORD"
]

with open("/app/dyndns.env", "w") as f:
    for key in keys:
        f.write(f"export {key}={shlex.quote(os.environ[key])}\n")

os.chmod("/app/dyndns.env", 0o600)
PY

# Create cron job
echo "$CRON_SCHEDULE root . /app/dyndns.env; /usr/local/bin/python /app/dyndns_update.py >> /proc/1/fd/1 2>&1" > /etc/cron.d/dyndns

chmod 0644 /etc/cron.d/dyndns

echo "DynDNS updater started."
echo "Domain: $DYNDNS_DOMAIN"
echo "Schedule: $CRON_SCHEDULE"

# Start cron in foreground
exec cron -f
