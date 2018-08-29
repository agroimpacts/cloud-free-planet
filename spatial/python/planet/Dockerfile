FROM ubuntu:latest

RUN apt-get update \
  && apt-get install -y python3-pip python3-dev libspatialindex-dev ca-certificates \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip

ENV CURL_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

COPY ./* /opt/planet/

COPY ./cfg /opt/planet/cfg

WORKDIR /opt/planet/

VOLUME /opt/planet/cfg

VOLUME /opt/planet/catalog

RUN cd /opt/planet/; pip install awscli && pip install -r requirements.txt

RUN mkdir -p /opt/planet/catalog/OS && mkdir -p /opt/planet/catalog/GS
