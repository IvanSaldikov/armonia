# Use the official Python image as the base image
FROM python:3.11-bookworm

ARG HOME=/home/app
ARG APP_HOME="${HOME}/web"
ARG VENV_PATH="${HOME}/venv"
ARG MEDIA_FOLDER_PATH="/mnt/media"
ARG STATIC_FOLDER_PATH="/mnt/static"

# Set environment variables for Python buffering and pip
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    LC_ALL=en_US.UTF-8 \
    LANG=en_US.UTF-8 \
    CRYPTOGRAPHY_DONT_BUILD_RUST=1 \
    PATH="${VENV_PATH}/bin:${PATH}" \
    APP_HOME="${APP_HOME}"

# Set the working directory in the container
WORKDIR $APP_HOME

USER root

# Copy the requirements file to the working directory
COPY app/requirements*.txt ./
# Copy entrypoint to check dependency running
COPY entrypoint.sh /entrypoint.sh

SHELL ["/bin/bash", "-x", "-e", "-u", "-o", "pipefail", "-c"]

ENV SETUPTOOLS_USE_DISTUTILS=stdlib

RUN apt-get update \
 && apt-get install --no-install-recommends -y \
      g++ \
      gcc \
      libffi-dev \
      musl-dev \
      python3-dev \
      netcat-traditional \
 && adduser \
      --system \
      --disabled-password \
      --disabled-login \
      --group \
      --shell /bin/bash \
      --home /home/app \
      --uid 911 app \
 && mkdir -p "${STATIC_FOLDER_PATH}" \
 && mkdir -p "${MEDIA_FOLDER_PATH}" \
 && python3 -m venv "${VENV_PATH}" \
 && ${VENV_PATH}/bin/python3 -m pip install --no-cache-dir --upgrade pip \
 && ${VENV_PATH}/bin/python3 -m pip install --no-cache-dir -r requirements.txt \
 # Make entrypoint executable
 && chmod +x /entrypoint.sh \
 # Fix $HOME, media and static folders permissions
 # && chown app:app "${HOME}" \
 && chown app:app "${STATIC_FOLDER_PATH}" \
 && chown app:app "${MEDIA_FOLDER_PATH}" \
 # Clean
 && apt-get autoremove \
 && apt-get clean \
 && rm -rf /tmp/* \
 && rm -rf /var/lib/apt/lists/*

# Fix app permission
COPY --chown=app:app app/ ${APP_HOME}

# Fix app permission
RUN chown -R app:app ${APP_HOME}

ADD docker_scripts/* ${HOME}/docker_scripts/
RUN chmod +x ${HOME}/docker_scripts/*

USER app

ENTRYPOINT ["/entrypoint.sh"]
