#!/bin/bash
docker run -v "$PWD"/secrets:/secrets -t hydra-permission-updater:latest