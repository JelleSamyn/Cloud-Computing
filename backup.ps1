# Cloud Computing Gateway backup script for Windows (PowerShell)
# Backs up InfluxDB databases and Node-RED flows to a local timestamped directory.

$ErrorActionPreference = "Stop"

$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupDir = "./backups/backup_$Timestamp"
New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host " Starting Smart Sensor Gateway Backup..." -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# 1. Backup Node-RED flows
Write-Host "Step 1: Backing up Node-RED flow configuration..." -ForegroundColor Yellow
if (Test-Path "./nodered/data/flows.json") {
    Copy-Item "./nodered/data/flows.json" "$BackupDir/nodered_flows.json"
    Write-Host "Saved Node-RED flows to: $BackupDir/nodered_flows.json"
} else {
    Write-Host "Warning: Node-RED flows.json not found locally. Skipping." -ForegroundColor DarkYellow
}

# 2. Backup InfluxDB time-series data
Write-Host "Step 2: Backing up InfluxDB time-series database..." -ForegroundColor Yellow
$Containers = docker ps --format "{{.Names}}"
if ($Containers -contains "gateway_influxdb") {
    # Create temp directory inside container for backup
    docker exec gateway_influxdb mkdir -p /tmp/influx_backup
    
    # Run backup inside container
    docker exec gateway_influxdb influx backup --token my-super-secret-admin-token-123456789 /tmp/influx_backup
        
    # Copy from container to host
    docker cp gateway_influxdb:/tmp/influx_backup "$BackupDir/influx_db"
    
    # Clean up temp folder inside container
    docker exec gateway_influxdb rm -rf /tmp/influx_backup
    Write-Host "Saved InfluxDB backup to: $BackupDir/influx_db/" -ForegroundColor Green
} else {
    Write-Host "Error: InfluxDB container (gateway_influxdb) is not running. Cannot perform DB backup." -ForegroundColor Red
    exit 1
}

Write-Host "=========================================" -ForegroundColor Green
Write-Host " Backup Completed Successfully!          " -ForegroundColor Green
Write-Host " Files saved to: $BackupDir" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
