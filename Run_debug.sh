#!/bin/bash

# docker-compose 명령어를 사용하여 컨테이너 빌드 및 실행 - 디버그 모드
docker-compose -f docker-compose.yml -f docker-compose.debug.yml up -d --build
