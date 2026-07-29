#!/bin/bash

# Cloud Computing Gateway backup script
# Backs up InfluxDB databases and Node-RED flows to a local timestamped directory.

set -e

BACKUP_DIR="./backups/backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "========================================="
echo " Starting Smart Sensor Gateway Backup..."
echo "========================================="

# 1. Backup Node-RED flows
echo "Step 1: Backing up Node-RED flow configuration..."
if [ -f "./nodered/data/flows.json" ]; then
    cp "./nodered/data/flows.json" "$BACKUP_DIR/nodered_flows.json"
    echo "Saved Node-RED flows to: $BACKUP_DIR/nodered_flows.json"
else
    echo "Warning: Node-RED flows.json not found locally. Skipping."
fi

# 2. Backup InfluxDB time-series data
echo "Step 2: Backing up InfluxDB time-series database..."
if docker ps | grep -q gateway_influxdb; then
    # Create temp directory inside container for backup
    docker exec gateway_influxdb mkdir -p /tmp/influx_backup
    
    # Run backup inside container
    docker exec gateway_influxdb influx backup \
        --token my-super-secret-admin-token-123456789 \
        /tmp/influx_backup
        
    # Copy from container to host
    docker cp gateway_influxdb:/tmp/influx_backup "$BACKUP_DIR/influx_db"
    
    # Clean up temp folder inside container
    docker exec gateway_influxdb rm -rf /tmp/influx_backup
    echo "Saved InfluxDB backup to: $BACKUP_DIR/influx_db/"
else
    echo "Error: InfluxDB container (gateway_influxdb) is not running. Cannot perform DB backup."
    exit 1
fi

echo "========================================="
echo " Backup Completed Successfully!          "
echo " Files saved to: $BACKUP_DIR"
echo "========================================="
