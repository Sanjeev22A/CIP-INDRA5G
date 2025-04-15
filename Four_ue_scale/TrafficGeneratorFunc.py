import socket 
import time
import threading
import random

def embb_traffic_generator(source_ip, dest_ip, port=5069, duration=30):
    """Generate high-throughput traffic of 10Mbps or higher using UDP socket"""
    print(f"[eMBB] Starting high-throughput stream from {source_ip} to {dest_ip}:{port}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Use UDP socket
    sock.bind((source_ip, 0))  # Bind to source IP with any available port

    pps = (10 * 1024 * 1024) // (8 * 1024)  # 10 Mbps, divided by 8 to convert to bits
    size=random.randint(pps-(pps//1024),(pps+pps//1024))
    packet = b'x' * 1024   # 1KB packet
    
    start_time = time.time()

    try:
        while time.time() - start_time < duration:
           for _ in range(size):
            sock.sendto(packet, (dest_ip, port))  # Use sendto for UDP
           time.sleep(1) 
            # After sending 10Mbps, sleep for 1 second
             
    finally:
        sock.close()
        print("[eMBB] Traffic ended")

def urllc_traffic_generator(source_ip,dest_ip,port=5002,duration=30):
    """Low-latency,small and frequent packets using UDP"""
    print(f"[URLLC] Starting low-latency stream from {source_ip} to {dest_ip}:{port}")
    sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    sock.bind((source_ip,0))
    size=random.randint(110,140)
    packet=b'u'*size ##size bytes og packet

    start_time=time.time()
    try:
        while time.time()-start_time<duration:
            sock.sendto(packet,(dest_ip,port))
            time.sleep(0.005)  #messages sent frequently
    finally:
        sock.close()
        print("[URLLC] traffic ended")
    

def mmtc_traffic_generator(source_ip,dest_ip,port=5003,device_count=50,duration=60):
    """Sparse, bursty traffic from many simulated devices - UDP"""
    print(f"[mMTC] Simulating {device_count} IoT devices from {source_ip} to {dest_ip}:{port}")
    
    def send_burst(device_id):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Bind to source IP
        sock.bind((source_ip, 0))  # 0 = any source port

        packet = f"device_{device_id}:data".encode()
        for _ in range(3):
            sock.sendto(packet, (dest_ip, port))
            time.sleep(random.uniform(0.1, 1.0))
        sock.close()

    start_time = time.time()
    while time.time() - start_time < duration:
        threading.Thread(target=send_burst, args=(random.randint(1, device_count),)).start()
        time.sleep(0.2)  # new device every 200ms

    print("[mMTC] Traffic simulation ended")

