#!bin/bash

# Set env
source ../.env

# Logging
echo "[$(date +"%Y-%m-%dT%H:%M:%S%z")] ### STARTED SNMP-MANAGER" >> "$LOGFILEDIR/snmp-manager-$(date +"%Y-%m-%d").log"

# Execute python script
python3 ./main.py

# Logging
echo "[$(date +"%Y-%m-%dT%H:%M:%S%z")] ### FINISHED SNMP-MANAGER CYCLE" >> "$LOGFILEDIR/snmp-manager-$(date +"%Y-%m-%d").log"