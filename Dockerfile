FROM python:3.10
WORKDIR /app

# Install dependencies
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Copy source code
COPY . .

# Run the app
CMD [ "python", "./Tauticord.py" ]
