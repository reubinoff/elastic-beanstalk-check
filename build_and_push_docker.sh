#!/bin/bash

# This is a simple script to build and push a docker image to github registry

# check if arg exist
if [ -z "$1" ]
  then
    echo "No tag supplied"
    exit 1
fi

TAG=v$1

echo $CR_PAT | docker login ghcr.io -u $GH_UNAME --password-stdin 

docker build -t ghcr.io/reubinoff/elastic-beanstalk-check:$TAG .
docker push ghcr.io/reubinoff/elastic-beanstalk-check:$TAG

docker logout ghcr.io