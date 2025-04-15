import os


os.system(f"sudo ip ro add 10.45.0.0/16 via 10.53.1.2")
os.system(f"route -n")
for i in range(4):
    os.system(f"sudo ip netns exec ue{i} ip route add default via 10.45.1.1 dev tun_srsue")
    os.system(f"sudo ip netns exec ue{i} route -n")

commands=[
    f"sudo ip netns exec ue0 python3 urllc_1.py",
    f"sudo ip netns exec ue1 python3 urllc_2.py",
    f"sudo ip netns exec ue2 python3 embb_traffic.py",
    f"sudo ip netns exec ue3 python3 mmtc_traffic.py"
]


for i in range(20):
    for a in commands:
        os.system(a)