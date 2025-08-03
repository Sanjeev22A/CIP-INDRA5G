#!/bin/bash

# Load environment variables from 5g.env
export $(grep -v '^#' 5g.env | xargs)

# Ensure required variables are set
if [[ -z "$srsRAN_SingleUE" || -z "$Log_Single_UE" || -z "$password" ]]; then
    echo "Error: Environment variables missing!"
    exit 1
fi

# Configuration
CONFIG_DIR="$srsRAN_SingleUE"
LOG_DIR="$Log_Single_UE"
FILENAME="$CONFIG_DIR/gnb_zmq.yaml"
OUTPUT_FILE="$LOG_DIR/gnb.log"

echo "Logging to: $OUTPUT_FILE"

# Wait before execution
echo "Sleeping for 5 seconds..."
sleep 5
echo "Woken up"

# Command to run gNB with sudo and log output
CMD="echo $password | sudo -S bash -c 'gnb -c $FILENAME | tee $OUTPUT_FILE; exec bash'"

# Open in a new terminal window using x-terminal-emulator
x-terminal-emulator -e bash -c "$CMD"
