FROM alpine:latest
MAINTAINER Andrea Carriero <info@andreacarriero.com>

RUN apk add --no-cache python3
RUN python3 -m ensurepip
RUN rm -r /usr/lib/python*/ensurepip
RUN pip3 install --upgrade pip setuptools
RUN rm -r /root/.cache

COPY . /opt/app
RUN pip3 install --upgrade pip
RUN pip3 install -r /opt/app/requirements.txt
WORKDIR /opt/app
CMD python3 server.py

EXPOSE 5000