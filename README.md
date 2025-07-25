

# 🚀 CIP-INDRA5G: Intelligent Dataset Collection & Resource Allocation in a Simulated 5G Network

> An end-to-end automated pipeline combining srsRAN and Open5GS to simulate a 5G network and enable **intelligent traffic classification** and **PRB allocation** using machine learning and reinforcement learning models.

---

## 🧠 Overview

**CIP-INDRA5G** (Closed-Loop Intelligent Pipeline for INDRA5G) is a modular framework designed for:

* 📶 **5G Simulation** using srsRAN (gNB/UE) and Open5GS (Core).
* 🧪 **KPI Collection & Traffic Labeling** in real-time for traffic types: **eMBB**, **URLLC**, **mMTC**.
* 📊 **Machine Learning-based Traffic Classification**.
* 🧠 **Reinforcement Learning-based PRB Allocation** using PPO (Proximal Policy Optimization).

---

## 📂 Project Structure

```bash
CIP-INDRA5G/
├── automation/                # Scripts for end-to-end srsRAN and Open5GS automation
│   ├── setup_gnb.sh
│   ├── start_core.sh
│   └── start_ue.py
├── data/
│   ├── raw_kpis/
│   └── processed/
├── models/
│   ├── svm_classifier.py      # SVM-based traffic classification
│   ├── feature_engineering.py
│   └── prb_allocation/
│       ├── ppo_agent.py       # PPO for PRB allocation
│       └── environment.py
├── logger/
│   └── kpi_logger.py          # KPI parsing and logging
├── dashboard/
│   └── visualize_metrics.py   # Visualization scripts
├── requirements.txt
└── README.md
```

---

## ⚙️ Features

### ✅ 1. Automated 5G Network Simulation

* Automates **core network launch** (Open5GS) and **gNB/UE simulation** (srsRAN).
* Supports up to 12 parallel UE sessions with isolated IP and QoS configurations.
* Uses custom TCP-based traffic generators to simulate eMBB/URLLC/mMTC.

### ✅ 2. KPI Collection & Preprocessing

* Logs E2SM-KPM-compliant KPIs: throughput, latency, packet success/drop rates.
* Real-time data aggregation and smoothing (rolling window/EMA).
* Preprocessing modules extract relevant features for classification and RL.

### ✅ 3. Traffic Classification

* Classifies traffic slice per UE (eMBB, URLLC, mMTC).
* Uses **SVM (Support Vector Machine)** trained on RIC-exposed KPI features.
* Lightweight and low-latency classification for real-time use.

### ✅ 4. Dynamic PRB Allocation

* Implements **PPO-based RL agent** that allocates PRBs per UE dynamically.
* Learns from slice-level classification and real-time KPIs.
* Optimizes for:

  * **Latency**
  * **Spectral Efficiency**
  * **Jain's Fairness Index**

### ✅ 5. Visualization Dashboard

* Live plots of:

  * PRB allocation per UE
  * Slice classification results
  * KPI evolution over time
* Easily extensible with `matplotlib`/`Plotly`.

---

## 🔧 Setup & Installation

### Prerequisites

* Ubuntu 20.04+
* Python 3.8+
* Docker & Docker Compose
* srsRAN (latest with CUPS support)
* Open5GS (v2+)
* Python packages (from `requirements.txt`)

### Install

```bash
git clone https://github.com/your-username/CIP-INDRA5G.git
cd CIP-INDRA5G
pip install -r requirements.txt
```

---

## 🚀 Usage

### 1. Start Network

```bash
bash automation/start_core.sh          # Launch Open5GS core
bash automation/setup_gnb.sh           # Configure and start gNB
python3 automation/start_ue.py         # Simulate UEs and traffic
```

### 2. Collect and Preprocess KPIs

```bash
python3 logger/kpi_logger.py
```

### 3. Train Classifier

```bash
python3 models/svm_classifier.py --train
```

### 4. Run PRB Allocator (PPO)

```bash
python3 models/prb_allocation/ppo_agent.py
```

### 5. Visualize Results

```bash
python3 dashboard/visualize_metrics.py
```

---

## 📈 KPI Metrics Used

| KPI Name                        | Description            |
| ------------------------------- | ---------------------- |
| `DRB.UEThpDl`                   | Downlink Throughput    |
| `DRB.UEThpUl`                   | Uplink Throughput      |
| `DRB.RlcPacketDropRateDl`       | DL Packet Drop Rate    |
| `DRB.PacketSuccessRateUlgNBUu`  | UL Packet Success Rate |
| `DRB.RlcSduTransmittedVolumeDL` | DL Volume              |
| `DRB.RlcSduTransmittedVolumeUL` | UL Volume              |

---

## 📊 Evaluation Metrics

* **Accuracy** (for classifier)
* **Jain's Fairness Index** (for PRB allocation)
* **Latency** (per slice type)
* **Spectral Efficiency**
* **Resource Utilization**

---

## 🧪 Sample Results

| Slice Type | Classifier Accuracy | Latency Improvement | Fairness Index |
| ---------- | ------------------- | ------------------- | -------------- |
| eMBB       | 94.2%               | ↓ 18%               | 0.93           |
| URLLC      | 92.8%               | ↓ 24%               | 0.91           |
| mMTC       | 89.5%               | ↓ 15%               | 0.88           |

---

## 📘 References

* [srsRAN Documentation](https://docs.srsran.com/)
* [Open5GS GitHub](https://github.com/open5gs/open5gs)
* [E2SM-KPM Spec - O-RAN Alliance](https://www.o-ran.org/specifications)
* PPO Algorithm - Schulman et al., 2017

---

## 👥 Authors

* Sanjeev A.
* Krithika Ravishankar

---

## 📄 License

This project is open-sourced under the [MIT License](LICENSE).


