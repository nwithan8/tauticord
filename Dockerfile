FROM keymetrics/pm2:18-alpine
WORKDIR /app

# Install Python and other utilities
RUN apk add --no-cache --update alpine-sdk git wget python3 python3-dev ca-certificates musl-dev libc-dev gcc bash nano linux-headers && \
    python3 -m ensurepip && \
    pip3 install --upgrade pip setuptools

# Install pm2-logrotate
RUN pm2 install pm2-logrotate

# Install script requirements
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Copy source code
COPY . .

# Run the app
CMD [ "pm2-runtime", "start", "ecosystem.config.json" ]
