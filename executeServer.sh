#!/bin/bash

docker run -d --name server diogogomes/cd2021
sleep 1
docker logs server