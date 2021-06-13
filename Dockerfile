FROM python:3
LABEL maintainer=cyb3rgh05t
LABEL org.opencontainers.image.source https://github.com/cyb3rgh05t/tauticord

WORKDIR /app

COPY requirements.txt requirements.txt

RUN python3 -m pip install --upgrade pip \
    && python3 -m pip install --no-warn-script-location --upgrade --force-reinstall --no-deps --user -r requirements.txt \
    && rm -rf /tmp/* && rm -rf requirements.txt /root/.cache /root/.lib  /root/.local

COPY ./ /app

CMD [ "python", "./Tauticord.py" ]
