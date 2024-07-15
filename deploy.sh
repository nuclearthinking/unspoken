#!/bin/bash

IP_ADDRESS=$(hostname -I | awk '{print $1}')
echo "Host address: $IP_ADDRESS"
echo "Building frontend with api backed address as: $IP_ADDRESS."
VITE_API_HOST=$IP_ADDRESS docker compose build frontend
echo "Running transcriber components containers."
docker compose up -d