# TrueNAS Auto Update

Yes, I know what you're thinking - "You shouldn't auto-update your TrueNAS apps!" And you're probably right. But if you're feeling adventurous and want to live on the edge, this Docker container will automatically update your TrueNAS SCALE apps whenever updates are available.

## Environment Variables

- `BASE_URL`: Your TrueNAS SCALE instance URL (e.g., `https://truenas.local`)
- `API_KEY`: Your TrueNAS API key (can be generated in the UI under System Settings → API Keys)
- `CRON_SCHEDULE`: Cron schedule for when to check for updates (e.g., `0 4 * * *` for daily at 4 AM). If not set, the script will run once and then exit.
- `APPRISE_URLS`: Apprise URLs to send notifications to (e.g., `https://example.com/apprise,https://example.com/apprise2`) More info on [Apprise](https://github.com/caronc/apprise)
- `NOTIFY_ON_SUCCESS`: Set to "true" to receive notifications when apps are successfully updated (default: "false")

## Getting Started

1. Generate an API key in your TrueNAS SCALE UI:

   - Go to System Settings → API Keys
   - Click "Add"
   - Give it a name and save

2. Run the container:

```bash
docker run --name truenas-auto-update \
         --restart unless-stopped \
         -e BASE_URL=https://your-truenas-url \
         -e API_KEY=your-api-key \
         -e CRON_SCHEDULE="0 4 * * *" \
         -e APPRISE_URLS="https://example.com/apprise,https://example.com/apprise2" \
         -e NOTIFY_ON_SUCCESS="true" \
         ghcr.io/marvinvr/truenas-auto-update
```

## Disclaimer

This tool automatically updates your TrueNAS SCALE apps without manual intervention. While convenient, this could potentially lead to issues if an update introduces problems. Use at your own risk and make sure you have proper backups!

Cheers,
[marvinvr](https://github.com/marvinvr)
