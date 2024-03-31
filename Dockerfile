# Node.js 18.19 pre-installed on Alpine Linux 3.19
FROM node:18.19.0-alpine3.19
WORKDIR /app

# Install Python utilities (always installs the latest version of Python 3)
RUN apk add --no-cache --update alpine-sdk wget ca-certificates musl-dev libc-dev gcc python3-dev bash linux-headers python3 py3-pip

# Install pm2
RUN npm install pm2 -g

# Copy requirements.txt from build machine to WORKDIR (/app) folder (important we do this BEFORE copying the rest of the files to avoid re-running pip install on every code change)
COPY requirements.txt requirements.txt

# Create virtual environment for Python
RUN python3 -m venv /app/venv
RUN . /app/venv/bin/activate

# Install Python requirements
RUN /app/venv/bin/pip install --no-cache-dir -r requirements.txt

# Make Docker /config volume for optional config file
VOLUME /config

# Make Docker /logs volume for log file
VOLUME /logs

# Copy source code from build machine to WORKDIR (/app) folder
COPY . .

# Delete unnecessary files in WORKDIR (/app) folder (not caught by .dockerignore)
RUN echo "**** removing unneeded files ****"

# Run the app
CMD [ "pm2-runtime", "start", "ecosystem.config.json"]
