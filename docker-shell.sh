#!/bin/bash
docker run --rm -it --entrypoint bash -v "$PWD"/secrets:/secrets -t hydra-permission-updater:latest