FROM ubuntu:latest

RUN apt-get update \
  && apt-get install -y python3-pip python3-dev libspatialindex-dev ca-certificates \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip install --upgrade pip

ENV CURL_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

COPY ./* /opt/planet/

COPY ./cfg /opt/planet/cfg

RUN mkdir -p /opt/planet/catalog/analytic/OS && \ 
    mkdir -p /opt/planet/catalog/analytic/GS && \
    mkdir -p /opt/planet/catalog/analytic_sr/OS && \ 
    mkdir -p /opt/planet/catalog/analytic_sr/GS && \
    mkdir -p /opt/planet/catalog/analytic_xml/OS && \ 
    mkdir -p /opt/planet/catalog/analytic_xml/GS && \
    mkdir -p /opt/planet/catalog/visual/OS && \ 
    mkdir -p /opt/planet/catalog/visual/GS

WORKDIR /opt/planet/

VOLUME /opt/planet/cfg

VOLUME /opt/planet/catalog

RUN cd /opt/planet/; pip install awscli --upgrade && pip install -r requirements.txt
