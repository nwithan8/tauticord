FROM python:latest
WORKDIR /app

# Install dependencies
COPY ../requirements.txt ./
RUN pip3 install -r requirements.txt

# Copy source code
COPY .. /app

# Run the app
CMD [ "python", "./Tauticord.py" ]
