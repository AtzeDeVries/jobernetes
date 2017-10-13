FROM python:3-alpine
MAINTAINER atze.devries@naturalis.nl

RUN apk add --no-cache curl
RUN curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl \
    && chmod +x ./kubectl \
    && mv kubectl /usr/bin/kubectl

RUN mkdir /jobernetes
WORKDIR /jobernetes
ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt
ADD . .
CMD python jobernetes.py

