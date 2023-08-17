#!/bin/bash
docker buildx build --platform linux/amd64,linux/arm64 -t quay.io/ntnu/autograde:v0.06 --push .