import subprocess
import os
from dotenv import load_dotenv
load_dotenv("5g.env")

# Configuration for URLLC traffic
SERVER_IP = "10.53.1.1"
dir=os.getenv("Log_Single_UE")
LOG_FILE = "urllc_traffic.log"
DURATION = 10  # seconds
BANDWIDTH = "10M"  # 10 Mbps
PACKET_SIZE = 256  # Small packets
path=f"{dir}/{LOG_FILE}"
def generate_urllc_traffic():
    """Generate low-latency UDP traffic for URLLC"""
    print("Starting URLLC Traffic...")

    cmd = [
        "iperf3", "-c", SERVER_IP, "-i", "1", "-t", str(DURATION),
        "-u", "-b", BANDWIDTH, "-l", str(PACKET_SIZE)
    ]

    # Save logs
    with open(path, "w") as log_file:
        subprocess.run(cmd, stdout=log_file, stderr=log_file)

    print(f"URLLC Traffic Finished! Logs saved at {path}")

if __name__ == "__main__":
    generate_urllc_traffic()
