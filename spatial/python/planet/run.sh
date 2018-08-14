#!/usr/bin/env bash

docker run \
  -v ${PWD}/catalog:/opt/planet/catalog \
  -v ${PWD}/cfg:/opt/planet/cfg daunnc/planet-downloader:latest python planet_download_tiff.py
