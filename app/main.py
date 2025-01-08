import logging
import os
import time

import apprise
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("API_KEY")
APPRISE_URLS = os.getenv("APPRISE_URLS", "").strip()

# Initialize Apprise
apobj = apprise.Apprise()
if APPRISE_URLS:
    for url in APPRISE_URLS.split(","):
        apobj.add(url.strip())


def send_notification(title, message):
    """Send notification using Apprise if configured"""
    if APPRISE_URLS:
        apobj.notify(title=title, body=message)
        logger.info(f"Notification sent: {title}")


if not BASE_URL or not API_KEY:
    logger.error("BASE_URL or API_KEY is not set")
    send_notification("Configuration Error", "BASE_URL or API_KEY is not set")
    exit(1)

BASE_URL = BASE_URL + "/api/v2.0"

try:
    response = requests.get(
        f"{BASE_URL}/app", headers={"Authorization": f"Bearer {API_KEY}"}, verify=False
    )
except Exception as e:
    logger.error(f"Failed to get apps: {str(e)}")
    send_notification("Error", f"Failed to get apps on {BASE_URL}: {str(e)}")
    exit(1)

if response.status_code != 200:
    logger.error(f"Failed to get apps: {response.status_code}")
    send_notification(
        "Error", f"Failed to get apps on {BASE_URL}: {response.status_code}"
    )
    exit(1)

apps = response.json()

apps_with_upgrade = [app for app in apps if app["upgrade_available"]]

logger.info(f"Found {len(apps_with_upgrade)} apps with upgrade available")


def await_job(job_id):
    logger.info(f"Waiting for job {job_id} to complete...")
    job = requests.post(
        f"{BASE_URL}/core/job_wait",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json=job_id,
        verify=False,
    )

    if job.status_code != 200:
        logger.error(f"Failed to wait for job {job_id}: {job.status_code}")
        return None

    return job


for app in apps_with_upgrade:
    logger.info(f"Upgrading {app['name']}...")
    response = requests.post(
        f"{BASE_URL}/app/upgrade",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={"app_name": app["id"]},
        verify=False,
    )

    if response.status_code != 200:
        error_msg = f"Failed to upgrade {app['name']}: {response.status_code}"
        logger.error(error_msg)
        send_notification("Upgrade Failed", error_msg)
        continue

    job_id = response.text
    response = await_job(job_id)

    if response.status_code == 200:
        success_msg = f"Upgrade of {app['name']} triggered successfully"
        logger.info(success_msg)
    else:
        error_msg = f"Failed to upgrade {app['name']}: {response.status_code}"
        logger.error(error_msg)
        send_notification("Upgrade Failed", error_msg)

    time.sleep(1)

logger.info("Done")
