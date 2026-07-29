#!/bin/bash

# Cloud Computing Gateway deployment script (CI/CD mockup)
# This script stops the current stack, pulls/rebuilds updated Docker containers, and boots them up.

set -e

echo "========================================="
echo " Starting Smart Sensor Gateway Deploy..."
echo "========================================="

# 1. Pull latest images for standard services (InfluxDB, Mosquitto, Portainer)
echo "Step 1: Pulling latest base images..."
docker compose pull mosquitto influxdb portainer watchtower

# 2. Build local custom images (Node-RED, Simulator)
echo "Step 2: Building custom containers (Node-RED, Simulator)..."
docker compose build --no-cache nodered simulator

# 3. Bring down the existing stack if running
echo "Step 3: Stopping active container stack..."
docker compose down --remove-orphans

# 4. Spin up the new stack in detached mode
echo "Step 4: Launching updated stack..."
docker compose up -d

# 5. Provision InfluxDB Dashboard
echo "Step 5: Provisioning InfluxDB Dashboard..."
python3 setup_dashboard.py || python setup_dashboard.py

echo "========================================="
echo " Deployment Completed Successfully!     "
echo " Services are starting up:               "
echo "  - InfluxDB:  http://localhost:8086     "
echo "  - Node-RED:  http://localhost:1880     "
echo "  - Portainer: http://localhost:9000     "
echo "========================================="
