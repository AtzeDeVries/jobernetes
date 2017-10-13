FROM python:3
MAINTAINER atze.devries@naturalis.nl
ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt
ADD . .
CMD python jobernetes.py

