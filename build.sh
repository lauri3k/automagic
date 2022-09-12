#!/bin/bash
docker buildx build --platform linux/amd64,linux/arm64 -t lauri3k/autograde:v0.02 --push .