#!/usr/bin/env python3
import logging
import os
import json
import time

from truenas_api_client import Client


UNIX_SOCKET_PREFIX = "ws+unix://"


BASE_ADDRESS = os.getenv("BASE_ADDRESS", "")
API_KEY = os.getenv("API_KEY")
API_PATH = os.getenv("API_PATH", "/api/v25.04.1")
ACTION_STATUS = [status.strip() for status in os.getenv("ACTION_STATUS","ERROR,UNKNOWN").strip().split(",")
                 if status.strip()]
INSTANCE_TYPES = [t.strip() for t in os.getenv("INSTANCE_TYPES","VM").strip().split(",") if t.strip()]
PROTOCOL = os.getenv("PROTOCOL", "wss://")
VERIFY_SSL = bool(json.loads(os.getenv("VERIFY_SSL", "false")))
EXCLUDE_INSTANCES = [instance.strip() for instance in os.getenv("EXCLUDE_INSTANCES", "").strip().split(",")
                     if instance.strip()]
INCLUDE_INSTANCES = [instance.strip() for instance in os.getenv("INCLUDE_INSTANCES", "").strip().split(",")
                     if instance.strip()]
LOGGING_LEVEL_ROOT = os.getenv("LOGGING_LEVEL_ROOT", "INFO")
_TEST_PYTHON_TEST_MODE = bool(json.loads(os.getenv("_TEST_PYTHON_TEST_MODE", "false")))


logging.basicConfig(level=LOGGING_LEVEL_ROOT)
logger = logging.getLogger(__name__)

if _TEST_PYTHON_TEST_MODE:
    # Python test mode ensures that python can execute file and the imports statements work
    # it DOES NOT test that the program actually works
    import sys
    version_info = sys.version_info
    print("\n".join([
        f"major={version_info.major}",
        f"minor={version_info.minor}",
        f"micro={version_info.micro}"
        ])
    )
    exit(0)


if not ACTION_STATUS:
    logger.error("Required at least 1 ACTION_STATUS")
    exit(1)


if EXCLUDE_INSTANCES and INCLUDE_INSTANCES:
    logger.error("Cannot use both EXCLUDE_INSTANCES and INCLUDE_INSTANCES "
                 "simultaneously")
    exit(1)


if BASE_ADDRESS and not PROTOCOL.startswith(UNIX_SOCKET_PREFIX) and not API_KEY:
    logger.error("API_KEY is required when BASE_ADDRESS is set and PROTOCOL is remote websocket")
    exit(1)


if BASE_ADDRESS or PROTOCOL.startswith(UNIX_SOCKET_PREFIX):
    CONNECTION_URI=f"{PROTOCOL}{BASE_ADDRESS}{API_PATH}"

    # Create the arguments to Client
    client_init_params = dict(
        uri=CONNECTION_URI,
        verify_ssl=VERIFY_SSL
    )
    logger.debug("Will connect to: %(uri)s with verify ssl: %(verify_ssl)s",
                 client_init_params)
else:
    # Local IPC mode is setup by passing no uri
    client_init_params = dict()
    logger.debug("Running in Local IPC mode")


with Client(**client_init_params) as c:
    if BASE_ADDRESS and not PROTOCOL.startswith(UNIX_SOCKET_PREFIX):
        # Login with API key
        # Local IPC mode doesn't require auth
        c.call("auth.login_with_api_key", API_KEY)

    # Create the filters
    filters = [
        [
            "status",
            "in",
            ACTION_STATUS
        ],
        [
            "type",
            "in",
            INSTANCE_TYPES
        ]
    ]

    if INCLUDE_INSTANCES:
        filters.append([
            "name",
            "in",
            INCLUDE_INSTANCES
        ])

    if EXCLUDE_INSTANCES:
        filters.append([
            "name",
            "nin",
            EXCLUDE_INSTANCES
        ])

    # Make the call
    logger.debug("Calling with filter %s", filters)
    instances = c.call("virt.instance.query", filters)
    logger.debug("virt.instance.query: %s", instances)

    if not instances:
        logger.info("No instances found matching filter criteria")

    # Process each matching instance
    for instance in instances:
        logger.info("Going to force stop instance: %(name)s", instance)
        logger.debug("Instance id: %(id)s", instance)
        result = c.call("virt.instance.stop", instance["id"], {"force": True})
        logger.debug("virt.instance.stop: %s", result)
        if not result:
            logger.warn("Failed to stop instance with id: %(id)s with stop "
                        "status: %s", instance, result)
            continue

        # Wait for the instance to be stopped
        while instance['status'] != 'STOPPED':
            time.sleep(1)
            instance = c.call("virt.instance.get_instance", instance["id"])
            logger.debug("virt.instance.get_instance: %s", instance)
        logger.info("Instance: %(name)s is now in status: %(status)s. "
                    "Starting it again", instance)
        # Start the instance again
        result = c.call("virt.instance.start", instance["id"])
        logger.debug("virt.instance.start:%s", result)
        if not result:
            logger.warn("Failed to start instance with id: %(id)s with start "
                        "status: %s", instance, result)
            continue

        # Wait for the instance to be started
        while instance['status'] == 'STOPPED':
            time.sleep(1)
            instance = c.call("virt.instance.get_instance", instance["id"])
            logger.debug("virt.instance.get_instance: %s", instance)
        logger.info("Instance with id: %(id)s is no longer stopped. It "
                    "is now in status: %(status)s", instance)

    logger.info("Done")
