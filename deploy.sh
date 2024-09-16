#!/bin/bash

# Try to get IP address using hostname -I first (for Linux)
IP_ADDRESS=$(hostname -I 2>/dev/null | awk '{print $1}')

# If hostname -I fails, try ifconfig or ip addr (for macOS or other systems)
if [ -z "$IP_ADDRESS" ]; then
    IP_ADDRESS=$(ifconfig 2>/dev/null | grep 'inet ' | grep -v '127.0.0.1' | awk '{print $2}' | head -n 1)
fi

# If ifconfig fails, try ip addr
if [ -z "$IP_ADDRESS" ]; then
    IP_ADDRESS=$(ip addr 2>/dev/null | grep 'inet ' | grep -v '127.0.0.1' | awk '{print $2}' | cut -d'/' -f1 | head -n 1)
fi

# If we still don't have an IP address, exit with an error
if [ -z "$IP_ADDRESS" ]; then
    echo "Error: Unable to determine IP address"
    exit 1
fi

echo "Host address: $IP_ADDRESS"
echo "Building frontend with api backed address as: $IP_ADDRESS."
VITE_API_HOST=$IP_ADDRESS docker compose build frontend
echo "Running transcriber components containers."
docker compose --profile frontend up -d