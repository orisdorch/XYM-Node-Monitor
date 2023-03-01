# Completely optional -- sample of how to prepare and run with a custom docker image
FROM python:3.9
RUN apt-get update -y
RUN pip install --upgrade pip
RUN pip install requests python-dotenv


# To build this docker image:
##docker build -t node-monitor /folder/containing/yourDockerfile

## Sample script for cron scheduling
# #!/bin/bash
# docker run --rm -v /folder/containing/yourScriptandEnvs:/script:rw node-monitor python /script/nodemonitor.py

## Sample cron scheduling period (10 min): */10 * * * *