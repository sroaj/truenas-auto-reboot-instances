# TrueNAS Auto Update

Yes, I know what you're thinking - "You shouldn't auto-update your TrueNAS apps!" And you're probably right. But if you're feeling adventurous and want to live on the edge, this Docker container will automatically update your TrueNAS SCALE apps whenever updates are available.

## Environment Variables

- `BASE_URL`: Your TrueNAS SCALE instance URL (e.g., `https://truenas.local`)
- `API_KEY`: Your TrueNAS API key (can be generated in the UI under System Settings → API Keys)
- `CRON_SCHEDULE`: Cron schedule for when to check for updates (e.g., `0 4 * * *` for daily at 4 AM)

## Getting Started

1. Generate an API key in your TrueNAS SCALE UI:

   - Go to System Settings → API Keys
   - Click "Add"
   - Give it a name and save

2. Run the container:

```bash
docker run -e BASE_URL=https://your-truenas-url \
          -e API_KEY=your-api-key \
          -e CRON_SCHEDULE="0 4 * * *" \
          ghcr.io/marvinvr/truenas-auto-update
```

## Disclaimer

This tool automatically updates your TrueNAS SCALE apps without manual intervention. While convenient, this could potentially lead to issues if an update introduces problems. Use at your own risk and make sure you have proper backups!

Cheers,
[marvinvr](https://github.com/marvinvr)
