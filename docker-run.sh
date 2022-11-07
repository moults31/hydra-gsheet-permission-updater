#!/bin/bash
docker run --rm \
-v "$PWD"/secret_user_emails:/secret_user_emails \
-v "$PWD"/secret_name_filters:/secret_name_filters \
-v "$PWD"/secret_cred:/secret_cred \
-t hydra-permission-updater:latest