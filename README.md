# TrueNAS Auto Reboot Instances

This docker image is used to periodically check the status of the instances vms on a TrueNAS system, and then stop and start the instance if the instance vm is in one of the specified action statuses.

This image uses TrueNAS JSON-RPC 2.0 over WebSocket API via [TrueNAS API Client](https://github.com/truenas/api_client), but is only tested on a 25.04.01 system with the incus virtual machines so far.

Using local IPC execution mode is recommended when this image is being run on the same host as the TrueNAS instance. As this will avoid needing to create API keys and handling SSL/TLS certificates. See [API Key Security](#api-key-security) for more details.

Code heavily based on:

- [marvinvr](https://github.com/marvinvr)'s [TrueNAS Auto Update](https://github.com/marvinvr/truenas-auto-update)

## Environment Variables

The environment variable `BASE_ADDRESS` and `API_KEY` should be provided, unless operation in Local IPC mode is desired which requires presence of `middlewared.sock` locally and doesn't require any environment variable be passed.

- `BASE_ADDRESS` (_optional_): Your TrueNAS SCALE api address (e.g., `192.168.0.111` or `192.168.0.111:8443`). If not set, local IPC will be used.
- `API_KEY`: Your TrueNAS API key (can be generated in the UI under System Settings → API Keys). This is required when `BASE_ADDRESS` is set nad `PROTOCOL` is not `ws+unix://`.
- `CRON_SCHEDULE` (_optional_): Cron schedule for when to check instance status (e.g., `*/2 * * * *` for every 2nd minute). If not set, the script will run once and then exit.
- `ACTION_STATUS` (_optional_): Comma-separated list of statuses of instances to perform stop and start on. The full list is available at [virt.instance.query → Return Value → status](https://api.truenas.com/v25.04.1/api_methods_virt.instance.query.html). If not set, `ERROR,UNKNOWN` will be used.
- `EXCLUDE_APPS` (_optional_): Comma-separated list of app names to skip during updates (e.g., `app1,app2`). This is useful if you want to exclude certain apps from being updated automatically.
- `INCLUDE_APPS` (_optional_): Comma-separated list of app names to include during updates (e.g., `app1,app2`). This is useful if you want to only update certain apps and skip the rest.
- `INSTANCE_TYPES` (_optional_): Comma-separated list of types of instances to perform stop and start on. The full list is available at [virt.instance.query → Return Value → type](https://api.truenas.com/v25.04.1/api_methods_virt.instance.query.html). If not set, `VM` will be used.
- `PROTOCOL`: The WebSocket uri protocol prefix to use. If not set, `wss://` will be used. See [API Key Security](#api-key-security) for details.
- `VERIFY_SSL` (_optional_): Whether to verify the SSL/TLS certificate of the `BASE_ADDRESS` when connecting using `wss` WebSocket. If not set, `false` will be used. See [API Key Security](#api-key-security) for details.
- `LOGGING_LEVEL_ROOT` (_optional_): The logging level to use. If not set `INFO` will be used.

NOTE: The `EXCLUDE_APPS` and `INCLUDE_APPS` variables are mutually exclusive. If both are set, the application will error out.

## API Key Security

Reference:
- https://www.truenas.com/docs/scale/25.04/scaletutorials/toptoolbar/managingapikeys

From TrueNAS 25.04 onwards, SSL/TLS transport security is required for TrueNAS API authentication using API keys. TrueNAS automatically revokes any user-linked API keys passed as part of an authentication attempt via insecure (HTTP) transport.

This container can operate in 2 modes:

1. WebSocket API
2. Local IPC

The operation mode can be set to Local IPC by either not providing `BASE_ADDRESS`, or providing `ws+unix://` as the `PROTOCOL` environment and specifying .

WebSocket API mode will, by default, connect to SSL/TLS WebSocket API, but will NOT verify the certificate. This is to facilitate usage in simple or testing environment where no externally signed SSL/TLS certificate or roots are setup.

Local IPC mode requires `middlewared.sock` to be present locally. This, as of TrueNAS 25.04.1, is located at `/var/run/middleware/middlewared.sock` and can be [bind mounted](https://docs.docker.com/engine/storage/bind-mounts/) into the container at runtime.

## Getting Started

This image has been tested to run in 3 ways:

1. Local direct execution in a shell or cron
2. Docker
3. Custom App

### Local direct execution

This repository should be checked out and uploaded to a Datastore on the TrueNAS server.

The `app/main.py` file should be chmod to executable, if not already. Then the `app/main.py` can be run with no arguments. Execution can be customized by setting the corresponding environment variables. As per usual if no environment variable are set, Local IPC will be used.

### Docker

Using Local IPC

```bash
docker run --name truenas-auto-reboot-instances \
         --restart unless-stopped \
         -e CRON_SCHEDULE="*/2 * * * *" \
         -v /var/run/middleware/middlewared.sock:/var/run/middleware/middlewared.sock
         sroaj/truenas-auto-reboot-instances
```

Using WebSocket API

1. Generate an API key in your TrueNAS SCALE UI:

   - Go to System Settings → API Keys
   - Click "Add"
   - Give it a name and save
   - Copy the API key to your clipboard
   
2. Deploy the container:
- Run the container on any Docker host:

```bash
docker run --name truenas-auto-reboot-instances \
         --restart unless-stopped \
         -e BASE_ADDRESS=192.168.0.111 \
         -e API_KEY=your-api-key \
         -e CRON_SCHEDULE="*/2 * * * *" \
         sroaj/truenas-auto-reboot-instances
```

### Custom App

1. Go to the Apps page in SCALE
2. Click "Discover Apps" in the top right
3. Click "Custom App" in the top right
4. Set the following values:
   - Name: `truenas-auto-reboot-instances`
   - Repository: `sroaj/truenas-auto-reboot-instances`
   - Tag: `latest`
   - Environment Variables (As described above)
   - Restart Policy: `Unless Stopped`
   - Storage Configuration (Skip if using WebSocket API):
      - Type: `Host Path (Path that already exists on the system)`
      - Mount Path: `/var/run/middleware/middlewared.sock`
      - Host Path: `/var/run/middleware/middlewared.sock`
5. Install the app
6. (_optional_) Review the app logs to ensure it's working as expected

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

