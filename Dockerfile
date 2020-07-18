FROM python:3

WORKDIR /app

COPY requirements.txt ./

RUN pip3 install -r requirements.txt

COPY ./ /app

CMD [ "python", "./Tauticord.py" ]
