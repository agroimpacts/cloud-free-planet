#!/usr/bin/env bash

docker-compose run planet-downloader

# or you can use docker directly
# docker run \
#   -v ${PWD}/catalog:/opt/planet/catalog \
#   -v ${PWD}/cfg:/opt/planet/cfg daunnc/planet-downloader:latest python planet_download_tiff.py
  