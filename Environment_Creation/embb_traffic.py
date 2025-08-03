import subprocess
import os
from dotenv import load_dotenv
load_dotenv("5g.env")

# Configuration for eMBB traffic
SERVER_IP = "10.53.1.1"
dir=os.getenv("Log_Single_UE")
LOG_FILE = "embb_traffic.log"
DURATION = 60  # seconds
path=f"{dir}/{LOG_FILE}"
def generate_embb_traffic():
    """Generate high-throughput TCP traffic for eMBB"""
    print("Starting eMBB Traffic...")

    cmd = ["iperf3", "-c", SERVER_IP, "-i", "1", "-t", str(DURATION)]
    
    # Save logs
    with open(path, "w") as log_file:
        subprocess.run(cmd, stdout=log_file, stderr=log_file,check=True)

    print(f"eMBB Traffic Finished! Logs saved at {path}")


generate_embb_traffic()
