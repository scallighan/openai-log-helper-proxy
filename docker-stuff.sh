#!/bin/bash
docker stop openaiproxy
docker container rm openaiproxy
docker build -t openaiproxy .
docker run -p 8888:80 -d --env-file .env --name openaiproxy openaiproxy
docker logs -f openaiproxy
