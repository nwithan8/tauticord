# Node.js 18.19 pre-installed on Alpine Linux 3.19 (Python 3.11.x)
FROM node:18.19.0-alpine3.19
WORKDIR /app

# Install Python utilities
# Refs:
# Pillow install on Alpine: https://github.com/python-pillow/docker-images/blob/main/alpine/Dockerfile
# numpy install on Alpine: https://stackoverflow.com/a/50443531
RUN echo "@testing http://dl-cdn.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories
RUN apk add --no-cache --update  \
    alpine-sdk  \
    wget  \
    ca-certificates  \
    musl-dev  \
    libc-dev gcc  \
    python3-dev  \
    bash  \
    linux-headers  \
    python3  \
    py3-pip  \
    cargo  \
    make  \
    cmake  \
    py3-numpy \
    freetype-dev \
    fribidi-dev \
    harfbuzz-dev \
    jpeg-dev \
    lcms2-dev \
    libimagequant-dev \
    openjpeg-dev \
    tcl-dev \
    tiff-dev \
    tk-dev \
    zlib-dev

# Install pm2
RUN npm install pm2 -g

# Copy requirements.txt from build machine to WORKDIR (/app) folder (important we do this BEFORE copying the rest of the files to avoid re-running pip install on every code change)
COPY requirements.txt requirements.txt

# Create virtual environment for Python
RUN python3 -m venv /app/venv
RUN . /app/venv/bin/activate

# Install Python requirements
# Ref: https://github.com/python-pillow/Pillow/issues/1763
RUN LIBRARY_PATH=/lib:/usr/lib /bin/sh -c "/app/venv/bin/pip install --no-cache-dir setuptools_rust" # https://github.com/docker/compose/issues/8105#issuecomment-775931324
RUN LIBRARY_PATH=/lib:/usr/lib /bin/sh -c "/app/venv/bin/pip install --no-cache-dir -r requirements.txt"

# Set up environment variables
ENV AM_I_IN_A_DOCKER_CONTAINER=Yes

# Make Docker /config volume for optional config file
VOLUME /config

# Make Docker /logs volume for log file
VOLUME /logs

# Copy source code from build machine to WORKDIR (/app) folder
COPY . .

# Delete unnecessary files in WORKDIR (/app) folder (not caught by .dockerignore)
RUN echo "**** removing unneeded files ****"

# Run entrypoint.sh script
ENTRYPOINT ["sh", "entrypoint.sh"]
