FROM python:3.15.0a2-slim
# The above versions should be automatically updated by dependabot
# Hence minor versions are used to ensure a more frequent build to
# catch regressions from new minor version earlier

LABEL org.opencontainers.image.source=https://github.com/sroaj/truenas-auto-reboot-instances
LABEL org.opencontainers.image.description="Automatically restart TrueNAS instances that are in ERROR or other status"
LABEL org.opencontainers.image.licenses=MIT

# Set working directory
WORKDIR /app

# Copy the application
COPY app docker-entrypoint.sh run-script.sh .

# Copy crontab file
COPY crontab /etc/cron.d/app-cron

# Install required packages and run required cmds
RUN --mount=target=/var/lib/apt/lists,type=cache,sharing=locked \
    --mount=target=/var/cache/apt,type=cache,sharing=locked \
    --mount=target=/root/.cache/pip,type=cache \
    rm -f /etc/apt/apt.conf.d/docker-clean \
    && apt-get update \
    && apt-get -y --no-install-recommends install \
    cron \
    gettext-base && \
    rm -rf /var/lib/apt/lists/* && \
    touch /var/log/cron.log && \
    pip install https://github.com/truenas/api_client/archive/master.zip && \
    chmod --verbose +x docker-entrypoint.sh run-script.sh main.py

ENTRYPOINT ["/app/docker-entrypoint.sh"]
