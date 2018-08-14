FROM ubuntu:latest

RUN apt-get update \
  && apt-get install -y python3-pip python3-dev libspatialindex-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip

COPY ./* /opt/planet/

WORKDIR /opt/planet/

VOLUME /opt/planet/cfg

VOLUME /opt/planet/catalog

RUN cd /opt/planet/; pip install awscli && pip install -r requirements.txt
