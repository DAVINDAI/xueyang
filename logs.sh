#!/bin/bash

echo "========================================="
echo "查看生产环境日志"
echo "========================================="

docker compose -f docker-compose.prod.yml logs -f --tail=100
