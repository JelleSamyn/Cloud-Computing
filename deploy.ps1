# Cloud Computing Gateway deployment script for Windows (PowerShell)
# This script stops the current stack, pulls/rebuilds updated Docker containers, and boots them up.

$ErrorActionPreference = "Stop"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host " Starting Smart Sensor Gateway Deploy..." -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# 1. Pull latest images for standard services
Write-Host "Step 1: Pulling latest base images..." -ForegroundColor Yellow
docker compose pull mosquitto influxdb portainer watchtower

# 2. Build local custom images
Write-Host "Step 2: Building custom containers (Node-RED, Simulator)..." -ForegroundColor Yellow
docker compose build --no-cache nodered simulator

# 3. Bring down the existing stack if running
Write-Host "Step 3: Stopping active container stack..." -ForegroundColor Yellow
docker compose down --remove-orphans

# 4. Spin up the new stack in detached mode
Write-Host "Step 4: Launching updated stack..." -ForegroundColor Yellow
docker compose up -d

# 5. Provision InfluxDB Dashboard
Write-Host "Step 5: Provisioning InfluxDB Dashboard..." -ForegroundColor Yellow
python setup_dashboard.py

Write-Host "=========================================" -ForegroundColor Green
Write-Host " Deployment Completed Successfully!     " -ForegroundColor Green
Write-Host " Services are starting up:               " -ForegroundColor Green
Write-Host "  - InfluxDB:  http://localhost:8086     " -ForegroundColor Green
Write-Host "  - Node-RED:  http://localhost:1880     " -ForegroundColor Green
Write-Host "  - Portainer: http://localhost:9000     " -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
