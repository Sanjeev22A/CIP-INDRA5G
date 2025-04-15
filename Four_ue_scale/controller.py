import os
import random
import subprocess
import time
##Establishing the gateway route - route from the core
os.system(f"sudo ip ro add 10.45.0.0/16 via 10.53.1.2")
os.system(f"route -n")

for i in range(4):
    os.system(f"sudo ip netns exec ue{i} ip route add default via 10.45.1.1 dev tun_srsue")
    os.system(f"sudo ip netns exec ue{i} route -n")
    ##os.system(f"sudo ip netns exec ue{i} apt-get update")
    ##os.system(f"sudo ip netns exec ue{i} apt-get install python3 python3-pip")

commands=[
    f"sudo ip netns exec ue0 python3 urllc_1.py",
    f"sudo ip netns exec ue1 python3 urllc_2.py",
    f"sudo ip netns exec ue2 python3 embb_traffic.py",
    f"sudo ip netns exec ue3 python3 mmtc_traffic.py"
]

while True:
    selected=random.sample(commands,3)
    print(f"Running:{selected[0]} , {selected[1]} and {selected[2]}\n")
    procs = [subprocess.Popen(cmd, shell=True) for cmd in selected]
    time.sleep(70)

    for proc in procs:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
    print("Cycle completed,Restarting...\n")
