#!/bin/bash


if [ $# -eq 0 ]; then
    echo "Error: Please provide a version number."
    echo "Usage: $0 <version>"
    exit 1
fi

VERSION=$1

docker buildx build --platform linux/amd64 -t gitlab-registry.selectel.org/radchenko.v/unspoken:${VERSION} -f frontend.Dockerfile .
docker buildx build --platform linux/amd64 -t gitlab-registry.selectel.org/radchenko.v/unspoken:latest -f frontend.Dockerfile .
docker push gitlab-registry.selectel.org/radchenko.v/unspoken:${VERSION}
docker push gitlab-registry.selectel.org/radchenko.v/unspoken:latest