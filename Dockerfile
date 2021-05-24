FROM python:3
LABEL maintainer=cyb3rgh05t
LABEL org.opencontainers.image.source https://github.com/cyb3rgh05t/tauticord

WORKDIR /app

COPY requirements.txt ./

RUN pip3 install -r requirements.txt

COPY ./ /app

CMD [ "python", "./Tauticord.py" ]
