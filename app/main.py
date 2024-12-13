import logging
import os
import time

import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("API_KEY")

if not BASE_URL or not API_KEY:
    logger.error("BASE_URL or API_KEY is not set")
    exit(1)

BASE_URL = BASE_URL + "/api/v2.0"

response = requests.get(
    f"{BASE_URL}/app", headers={"Authorization": f"Bearer {API_KEY}"}, verify=False
)

apps = response.json()

apps_with_upgrade = [app for app in apps if app["upgrade_available"]]

logger.info(f"Found {len(apps_with_upgrade)} apps with upgrade available")


def await_job(job_id):
    logger.info(f"Waiting for job {job_id} to complete...")
    return requests.post(
        f"{BASE_URL}/core/job_wait",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json=job_id,
        verify=False,
    )


for app in apps_with_upgrade:
    logger.info(f"Upgrading {app['name']}...")
    response = requests.post(
        f"{BASE_URL}/app/upgrade",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={"app_name": app["id"]},
        verify=False,
    )

    job_id = response.text
    response = await_job(job_id)

    if response.status_code == 200:
        logger.info(f"Upgrade of {app['name']} triggered successfully")
    else:
        logger.error(f"Failed to upgrade {app['name']}: {response.status_code}")

    time.sleep(1)

logger.info("Done")
