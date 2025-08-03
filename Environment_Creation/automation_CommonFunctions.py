import os
import subprocess

def open_cmd(directory, command=None):
    if os.path.isdir(directory):
        if command:
            subprocess.run(["gnome-terminal", "--working-directory", directory, "--", "bash", "-c", f"{command}; exec bash"])
        else:
            subprocess.run(["gnome-terminal", "--working-directory", directory])
    else:
        print("Error: Directory does not exist!!")

def open_cmd_sudo(directory, command=None):
    if os.path.isdir(directory):
        if command:
            subprocess.run(["gnome-terminal", "--", "sudo", "-i", "bash", "-c", f"cd {directory}; {command}; exec bash"])
        else:
            subprocess.run(["gnome-terminal", "--", "sudo", "-i"])
    else:
        print("Error: Directory does not exist!!")
def traffic_server():
    """Start iPerf3 server to receive traffic."""
    print("Starting iPerf3 Server...")

    cmd = ["iperf3", "-s", "-i", "1"]

    # Run iPerf3 server in a separate process
    subprocess.run(cmd)

def setup_network():
    """Configure network routes for UE and Core using os.system."""
    
    # Add route to core network
    os.system("sudo ip route add 10.45.0.0/16 via 10.53.1.2")
    
    # Show routing table
    os.system("sudo ip route")
    
    # Set up UE namespace routing
    os.system("sudo ip netns exec ue1 ip route add default via 10.45.1.1 dev tun_srsue")
    
    # Show UE routing table
    os.system("sudo ip netns exec ue1 ip route")

'''
-------Testing code-----------
open_cmd(os.getcwd())
open_cmd(os.getcwd(), "ls -l")

open_cmd_sudo(os.getcwd())
open_cmd_sudo(os.getcwd(), "ls -l'
'''