FROM python:3.8-slim-buster

WORKDIR /

COPY slave.py slave.py 
COPY server/const.py server/const.py

CMD [ "python3", "slave.py"]
