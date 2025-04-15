#!/usr/bin/env python3

import datetime
from datetime import datetime as dt
import argparse
import signal
from lib.xAppBase import xAppBase
import time
import numpy as np
import os
import gymnasium as gym
from gymnasium import spaces
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
import csv

# =======================
# Reward function definitions
# =======================

num_prbs = 52

def estimate_buffer_delay(buffer_size, throughput):
    return buffer_size / (throughput + 1e-3)

def estimate_delay_from_packet_drop(drop_rate):
    return drop_rate

def estimate_t_avg(buffer_size, throughput, drop_rate):
    return estimate_buffer_delay(buffer_size, throughput) + estimate_delay_from_packet_drop(drop_rate)

def urllc_reward(buffer_size, throughput, drop_rate, t_expected):
    t_avg = estimate_t_avg(buffer_size, throughput, drop_rate)
    return max(-1,min((t_expected-t_avg)/t_expected,0))

def embb_reward(b_avg, b_target):
    return max(-1,min((b_avg-b_target)/b_target,0))


def mmtc_reward(b_received, b_expected):
    return max(-1,min((b_received-b_expected)/b_expected,0))


# ===============================
# Environment for the RL agent
# ===============================
class PRBAllocationEnv(gym.Env):
    def __init__(self, num_ues=4, total_prbs=52):
        super(PRBAllocationEnv, self).__init__()
        self.num_ues = num_ues
        self.total_prbs = total_prbs

        self.action_space = spaces.Box(low=0, high=1, shape=(self.num_ues,), dtype=np.float32)
        self.observation_space = spaces.Box(low=0, high=np.inf, shape=(self.num_ues * 6,), dtype=np.float32)

        self.kpi_state = np.zeros((self.num_ues, 6))
        self.slice_types = [1, 1, 2, 3]  # URLLC, URLLC, eMBB, mMTC
        self._seed()

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.kpi_state = self._simulate_initial_kpis()
        return self.kpi_state.flatten(), {}

    def step(self, action, updated_ue_indices=None):
        action = np.clip(action, 0, 1)
        prb_allocations = self._scale_action_to_prbs(action)
        self.kpi_state = self._simulate_kpi_update(prb_allocations)

        if updated_ue_indices is None:
            updated_ue_indices = range(self.num_ues)

        total_reward = 0
        for i in updated_ue_indices:
            total_reward += self._compute_reward(i, self.kpi_state[i], self.slice_types[i])
        
        filename = "reward.csv"

      

        # Check if the file exists
        file_exists = os.path.isfile(filename)

        # Open the file in append mode
        with open(filename, mode='a', newline='') as csvfile:
            writer = csv.writer(csvfile)

            # Optionally write a header if file doesn't exist
            if not file_exists:
                writer.writerow(['total_reward'])

            # Write the single reward value
            writer.writerow([int(total_reward)])
        done = False
        return self.kpi_state.flatten(), total_reward, done, False, {}

    def render(self):
        for i in range(self.num_ues):
            print(f"UE {i + 1}: {self.kpi_state[i]}")

    def _scale_action_to_prbs(self, action):
        scaled = action / np.sum(action) if np.sum(action) > 0 else np.ones_like(action) / len(action)
        return np.round(scaled * self.total_prbs).astype(int)

    def _simulate_initial_kpis(self):
        return np.array([
            [5, 986, 0, 100, 5, 978],
            [5, 953, 0, 100, 5, 946],
            [28, 2170, 0, 100, 27, 2160],
            [2, 23, 0, 100, 2, 21],
        ], dtype=np.float32)

    def _simulate_kpi_update(self, prb_allocations):
        kpis = []
        for prb in prb_allocations:
            ue_thp_dl = prb * 0.7
            ue_thp_ul = prb * 0.5
            rlc_drop_rate_dl = max(0.0, 1.0 - prb * 0.03)
            pkt_success_ul = min(1.0, prb * 0.02)
            sdu_vol_dl = prb * 0.6
            sdu_vol_ul = prb * 0.4
            kpis.append([ue_thp_dl, ue_thp_ul, rlc_drop_rate_dl, pkt_success_ul, sdu_vol_dl, sdu_vol_ul])
        return np.array(kpis)

    def _compute_reward(self, ue_index, kpis, slice_type):
        thp_dl, thp_ul, drop_dl, success_ul, vol_dl, vol_ul = kpis
        if slice_type == 1:
            return urllc_reward(vol_ul, thp_ul, 100 - success_ul, t_expected=1)
        elif slice_type == 2:
            return embb_reward(thp_ul, b_target=8670)
        elif slice_type == 3:
            return mmtc_reward(vol_ul, 22)
        else:
            return 0

    def _seed(self, seed=None):
        np.random.seed(seed)

# RL Model Setup
env = DummyVecEnv([lambda: PRBAllocationEnv(num_ues=4, total_prbs=num_prbs)])
model = PPO("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=10000)
model.save("prb_allocator_model")


class Controller(xAppBase):
    def __init__(self, config, http_server_port, rmr_port, report_interval=5):
        super(Controller, self).__init__(config, http_server_port, rmr_port)
        self.model = PPO.load("prb_allocator_model")
        self.kpi_data = {f"ue{i}": {'buffer': [], 'average': np.zeros(6)} for i in range(4)}
        self.report_interval = report_interval  # Time interval (in seconds) for averaging KPIs
        self.start_time = dt.now()

    def my_subscription_callback(self, e2_agent_id, subscription_id, indication_hdr, indication_msg, kpm_report_style, ue_id):
        indication_hdr = self.e2sm_kpm.extract_hdr_info(indication_hdr)
        message_data = self.e2sm_kpm.extract_meas_data(indication_msg)
        meas_data = message_data.get('measData', {})
        metric_row = {metric: (values[0] if isinstance(values, list) and values else 0)
                      for metric, values in meas_data.items()}

        # Append new data to the buffer for the respective UE
        self.kpi_data[f"ue{ue_id}"]['buffer'].append([
            metric_row.get('DRB.UEThpDl', 0),
            metric_row.get('DRB.UEThpUl', 0),
            metric_row.get('DRB.RlcPacketDropRateDl', 0),
            metric_row.get('DRB.PacketSuccessRateUlgNBUu', 100),
            metric_row.get('DRB.RlcSduTransmittedVolumeDL', 0),
            metric_row.get('DRB.RlcSduTransmittedVolumeUL', 0),
        ])

        # Check if it's time to compute the average (every report_interval seconds)
        cur_time = dt.now()
        if (cur_time - self.start_time).total_seconds() >= self.report_interval:
            self.start_time = cur_time
            self._compute_average_kpis()

            # Once the average is computed, call the PPO model and predict PRB allocations
            obs_vector = []
            silent_ues=[]
            for i in range(4):
                # Add the average KPI values for each UE
                avg_kpi = self.kpi_data[f"ue{i}"]['average']
                obs_vector.extend(avg_kpi)
                if np.allclose(avg_kpi,0.0):
                    silent_ues.append(i) 
            env_state = np.array(obs_vector, dtype=np.float32).reshape(1, -1)
            action, _ = self.model.predict(env_state)
            for i in silent_ues:
                action[0][i]=0.0
            prb_allocations = self._scale_action_to_prbs(action)
            for i in range(len(prb_allocations[0])):
                ##Allocation line here
                val=int(prb_allocations[0][i])
                
                self.e2sm_rc.control_slice_level_prb_quota(e2_agent_id, ue_id, min_prb_ratio=val,max_prb_ratio=val, dedicated_prb_ratio=100, ack_request=1)
            print(f"Predicted PRB allocation: {prb_allocations}")

    def _compute_average_kpis(self):
        # For each UE, compute the average of the KPIs over the last report_interval seconds
        for ue_id in range(4):
            kpi_buffer = self.kpi_data[f"ue{ue_id}"]['buffer']
            if kpi_buffer:
                # Compute average for the current buffer
                kpi_array = np.array(kpi_buffer)
                self.kpi_data[f"ue{ue_id}"]['average'] = np.mean(kpi_array, axis=0)
                # Clear the buffer for the next interval
                self.kpi_data[f"ue{ue_id}"]['buffer'] = []

    def _scale_action_to_prbs(self, action):
        action = np.clip(action, 0, 1)
        total = np.sum(action)
        if total > 0:
            scaled = action / total
        else:
            # All UEs silent, allocate zero PRBs
            return np.zeros_like(action, dtype=int)
        return np.round(scaled * num_prbs).astype(int)

    @xAppBase.start_function
    def start(self, e2_node_id, ue_ids, metric_names):
        report_period = 1000
        granul_period = 1000
        for i in range(4):
            ue_id = ue_ids[i]
            cb = lambda agent, sub, hdr, msg, ue_id=ue_id: self.my_subscription_callback(agent, sub, hdr, msg, 2, ue_id)
            self.e2sm_kpm.subscribe_report_service_style_2(
                e2_node_id, report_period, ue_id, metric_names, granul_period, cb
            )

ALL_KPM_METRICS = [
    "DRB.UEThpDl", "DRB.UEThpUl", "DRB.RlcPacketDropRateDl",
    "DRB.PacketSuccessRateUlgNBUu", "DRB.RlcSduTransmittedVolumeDL", "DRB.RlcSduTransmittedVolumeUL"
]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="KPI Collector xApp")
    parser.add_argument("--config", type=str, default='')
    parser.add_argument("--http_server_port", type=int, default=8092)
    parser.add_argument("--rmr_port", type=int, default=4562)
    parser.add_argument("--e2_node_id", type=str, default='gnbd_001_001_00019b_0')
    parser.add_argument("--ran_func_id", type=int, default=2)
    parser.add_argument("--kpm_report_style", type=int, default=1)
    parser.add_argument("--ue_ids", type=str, default='0,1,2,3')
    args = parser.parse_args()

    controller = Controller(config=args.config, http_server_port=args.http_server_port, rmr_port=args.rmr_port)
    controller.e2sm_kpm.set_ran_func_id(ran_func_id=args.ran_func_id)
    signal.signal(signal.SIGQUIT, controller.signal_handler)
    signal.signal(signal.SIGTERM, controller.signal_handler)
    signal.signal(signal.SIGINT, controller.signal_handler)
    controller.start(e2_node_id=args.e2_node_id, ue_ids=list(map(int, args.ue_ids.split(","))), metric_names=ALL_KPM_METRICS)
