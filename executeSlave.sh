#!/bin/bash

docker build --tag projecto_final .

docker run -d --name slave projecto_final

sleep 1

docker logs slave