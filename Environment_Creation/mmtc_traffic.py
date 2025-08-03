import subprocess
import os
from dotenv import load_dotenv
load_dotenv("5g.env")

# Configuration for mMTC traffic
SERVER_IP = "10.53.1.1"
dir=os.getenv("Log_Single_UE")
LOG_FILE = "mmtc_traffic.log"
DURATION = 120  # seconds
BANDWIDTH = "100K"  # 100 Kbps
PACKET_SIZE = 512  # Medium packets
path=f"{dir}/{LOG_FILE}"
def generate_mmtc_traffic():
    """Generate low-data-rate UDP traffic for mMTC"""
    print("Starting mMTC Traffic...")

    cmd = [
        "iperf3", "-c", SERVER_IP, "-i", "1", "-t", str(DURATION),
        "-u", "-b", BANDWIDTH, "-l", str(PACKET_SIZE)
    ]

    # Save logs
    with open(path, "w") as log_file:
        subprocess.run(cmd, stdout=log_file, stderr=log_file)

    print(f"mMTC Traffic Finished! Logs saved at {path}")

if __name__ == "__main__":
    generate_mmtc_traffic()
