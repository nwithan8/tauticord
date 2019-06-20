FROM python:3
ADD Tauticord.py /
RUN pip3 install discord PlexAPI requests asyncio
CMD [ "python", "./Tauticord_working.py" ]
