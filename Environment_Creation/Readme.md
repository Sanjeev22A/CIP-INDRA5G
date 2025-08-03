
# UE-to-gNB Connection and 5G Core Integration (srsRAN Setup)

This README describes the architecture and process used to establish user equipment (UE) connections to the gNB, form IP tunnels using `tun_srsue`, and route traffic through to the 5G Core and RIC (RAN Intelligent Controller).

---

## 📶 Overview

This setup simulates multiple UEs (UE0 to UE3) using Linux network namespaces and the srsRAN software suite. Each UE connects to the gNB via a virtual interface and IP tunnel, and traffic is routed into the 5G Core.

---

## 🧩 Components

- **UEs (`ue0`, `ue1`, `ue2`, `ue3`)**  
  - Simulated using Linux **network namespaces**
  - Communicate using a virtual IP interface: `tun_srsue`

- **TUN Interface (`tun_srsue`)**  
  - A **Layer 3 virtual interface** created by `srsUE`
  - Handles UE's IP traffic and connects to the gNB
  - Acts as a gateway for UE namespaces

- **gNB (CU/DU split)**  
  - Connects UE traffic to the 5G Core using NG (Next Generation) interface
  - Forwards packets via GTP-U to UPF (User Plane Function)

- **5G Core**  
  - Provides mobility management, session handling, and IP assignment
  - Assigns UE IPs (e.g., 10.45.0.0/16)

- **RIC (RAN Intelligent Controller)**  
  - Optionally monitors or controls RAN behavior via E2 interface
  - Receives telemetry or applies control policies to gNB

---

## 🔄 Connection Flow

### 1. **Namespace Setup**
```bash
ip netns add ue0
ip netns add ue1
...
````

### 2. **TUN Interface & Routing**

Each UE uses the `tun_srsue` device as its default route:

```python
sudo ip netns exec ue0 ip route add default via 10.45.1.1 dev tun_srsue
```

* This tells the UE to route all outbound traffic to the gNB via `tun_srsue`.

### 3. **Tunnel Establishment**

`srsUE` sets up a TUN interface that:

* Interfaces with the gNB
* Encapsulates IP packets for forwarding via GTP-U

### 4. **gNB-to-Core Communication**

The gNB connects to the core network:

* N2 interface for control-plane (AMF)
* N3 interface for user-plane (UPF)

Example route to reach UE subnet:

```bash
sudo ip route add 10.45.0.0/16 via 10.53.1.2
```

(`10.53.1.2` is likely the gNB-CU IP)

### 5. **RIC Integration**

The gNB connects to the RIC via the **E2 interface**, allowing:

* Performance monitoring
* Real-time control
* Closed-loop optimization

---

## 🧪 Traffic Generation

Each UE runs traffic generation scripts with different service types:

```bash
sudo ip netns exec ue0 python3 urllc_1.py
sudo ip netns exec ue1 python3 urllc_2.py
sudo ip netns exec ue2 python3 embb_traffic.py
sudo ip netns exec ue3 python3 mmtc_traffic.py
```

* `urllc_*.py`: Ultra-Reliable Low-Latency Communication
* `embb_traffic.py`: Enhanced Mobile Broadband
* `mmtc_traffic.py`: Massive Machine-Type Communication

---

## 📌 Summary

This setup simulates a 5G end-to-end data path:

```
UE (netns) → tun_srsue → gNB → 5G Core (UPF) → Internet
```

With optional RIC integration for control and optimization of the RAN.

---

## 🔧 Requirements

* Linux with `iproute2` tools (`ip netns`, `ip route`)
* Python 3, `srsRAN`, 5G Core stack (e.g., free5GC, Open5GS)
* sudo/root access

```

---

Let me know if you want this customized to your exact script names, IPs, or platform (e.g., if you’re using `srsRAN 23.x`, `Open5GS`, or `free5GC`).
```
