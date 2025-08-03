#!/usr/bin/env python3
import datetime 
import argparse
import signal
from lib.xAppBase import xAppBase
import time
import gymnasium as gym
from gymnasium import spaces
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env

# ==============================
# Reward Functions
# ==============================
def estimate_buffer_delay(buffer_size, throughput):
    return buffer_size / (throughput + 1e-3)

def estimate_delay_from_packet_drop(drop_rate):
    return drop_rate * 100

def estimate_t_avg(buffer_size, throughput, drop_rate):
    return estimate_buffer_delay(buffer_size, throughput) + estimate_delay_from_packet_drop(drop_rate)

def urllc_reward(buffer_size, throughput, drop_rate, t_expected):
    t_avg = estimate_t_avg(buffer_size, throughput, drop_rate)
    return max(-1, min(0, (t_expected - t_avg) / t_expected))

def embb_reward(b_avg, b_target):
    return max(-1, min(0, (b_target - b_avg) / b_target))

def mmtc_reward(b_received, b_expected):
    return max(-1, min(0, (b_received - b_expected) / b_expected))


class PRBAllocationEnv(gym.Env):
    def __init__(self, num_ues, total_prbs):
        super(PRBAllocationEnv, self).__init__()
        self.num_ues = num_ues
        self.total_prbs = total_prbs
        # Action space: Discrete 3^num_ues choices
        self.action_space = spaces.Discrete(3 ** num_ues)
        # Observation space: Vector of `num_ues` elements, each ranging from 0 to `total_prbs`
        self.observation_space = spaces.Box(low=0, high=self.total_prbs, shape=(num_ues,), dtype=np.int32)
        self.state = np.ones(self.num_ues) * (self.total_prbs // self.num_ues)

    def reset(self, *, seed=42, options=None):
        # Properly handle seeding
        self.np_random, _ = gym.utils.seeding.np_random(seed)
        # Initialize state
        self.state = np.ones(self.num_ues) * (self.total_prbs // self.num_ues)
        return self.state, {}

    def step(self, action, kpi_dict, slice_type):
        action_arr = self.decode_action(action)
        tentative_state = self.state + action_arr
        tentative_state = np.clip(tentative_state, 0, self.total_prbs)
        
        total_allocated = np.sum(tentative_state)
        if total_allocated > self.total_prbs:
            scaling_factor = self.total_prbs / total_allocated
            tentative_state = np.floor(tentative_state * scaling_factor).astype(int)

        self.state = tentative_state
        reward = self.comput_reward(self.state, kpi_dict, slice_type)
        done = False  # You can add your own logic to determine when the episode ends

        return self.state, reward, done, {}

    def decode_action(self, action):
        action_arr = []
        for i in range(self.num_ues):
            action_arr.append((action // (3 ** (self.num_ues - i - 1))) % 3 - 1)
        return np.array(action_arr)

    def comput_reward(self, state, kpi_dict, slice_type):
        # Update reward calculation for modern versions
        if slice_type == 1:  # URLLC
            reward = urllc_reward(
                buffer_size=kpi_dict['RlcSduTransmittedVolumeUL'],
                throughput=kpi_dict['UEThpUl'],
                drop_rate=1 - kpi_dict['PacketSuccessRateUlgNBUu'],
                t_expected=1
            )
        elif slice_type == 2:  # eMBB
            reward = embb_reward(
                b_avg=kpi_dict['UEThpDl'],
                b_target=8700  # example Mbps threshold
            )
        else:  # mMTC
            reward = mmtc_reward(
                b_received=kpi_dict['RlcSduTransmittedVolumeUL'],
                b_expected=22  # example volume threshold
            )

        return reward

num_ues = 4
total_prbs =52
env = PRBAllocationEnv(num_ues=num_ues, total_prbs=total_prbs)

# Optional: Check your environment conforms to Gym API
check_env(env, warn=True)

# PPO model initialization
model = PPO("MlpPolicy", env, verbose=1)

class IntelligentAllocator(xAppBase):
    def __init__(self, http_server_port, rmr_port):
        super(IntelligentAllocator, self).__init__('', http_server_port, rmr_port)
        self.env = env
        self.model = model
        self.current_state = self.env.reset()

    def my_subscription_callback(self, e2_agent_id, subscription_id, indication_hdr, indication_msg, kpm_report_style, ue_id):
        indication_hdr = self.e2sm_kpm.extract_hdr_info(indication_hdr)
        message_data = self.e2sm_kpm.extract_meas_data(indication_msg)
        meas_data = message_data.get('measData', {})
        
        # Extract KPI values into a dict
        kpi_dict = {}
        for metric_name, value_list in meas_data.items():
            value = value_list[0] if isinstance(value_list, list) and value_list else None
            kpi_dict[metric_name] = value

        # Define slice_type based on UE ID
        slice_type = 1 if ue_id in [0, 1] else (2 if ue_id == 2 else 3)

        # PPO decides action based on the current state
        action, _states = self.model.predict(self.current_state, deterministic=True)

        # Perform environment step and get reward
        next_state, reward, done, _ = self.env.step(action, kpi_dict, slice_type)

        # Train PPO on this single step (online)
        self.model.learn(total_timesteps=1)

        # Update state
        self.current_state = next_state

        # Optionally: Log the current allocation
        print(f"UE: {ue_id}, Slice: {slice_type}, Action: {action}, Reward: {reward}, State: {self.current_state}")

    @xAppBase.start_function
    def start(self, e2_node_id, ue_ids, metric_names):
        report_period = 1000
        granul_period = 1000

        for i in range(len(ue_ids)):
            ue_id = ue_ids[i]
            subscription_callback = lambda agent, sub, hdr, msg, ue_id=ue_id: self.my_subscription_callback(agent, sub, hdr, msg, 2, ue_id)
            self.e2sm_kpm.subscribe_report_service_style_2(
                e2_node_id,
                report_period,
                ue_id,
                metric_names,
                granul_period,
                subscription_callback
            )
ALL_KPM_METRICS = [
    "DRB.UEThpDl",
    "DRB.UEThpUl",
    "DRB.RlcPacketDropRateDl",
    "DRB.PacketSuccessRateUlgNBUu",
    "DRB.RlcSduTransmittedVolumeDL",
    "DRB.RlcSduTransmittedVolumeUL"
]

if __name__=='__main__':
    parser=argparse.ArgumentParser(description="KPI Collector xApp")
    parser.add_argument("--config",type=str,default='',help='Give the path of xApp config files')
    parser.add_argument("--http_server_port",type=int,default=8092,help="Http server port")
    parser.add_argument("--rmr_port",type=int,default=4562,help="RMR port")
    parser.add_argument("--e2_node_id",type=str,default='gnbd_001_001_00019b_0',help="E2/gnb node id")
    parser.add_argument("--ran_func_id",type=int,default=2,help="E2SM RC RAN FUNCTION ID")
    parser.add_argument("--kpm_report_style",type=int,default=1,help="KPM Report Style")
    parser.add_argument("--ue_ids",type=str,default='0,1,2,3',help="UE ID")
    parser.add_argument("--metrics",type=str,default='DRB.UEThpUl,DRB.UEThpDl,RLC.SDUUlDelay',help="Metric Names collected for both uplink and downlink")

    args=parser.parse_args()
    config=args.config
    http_server_port=args.http_server_port
    rmr_port=args.rmr_port
    e2_node_id=args.e2_node_id
    ran_func_id=args.ran_func_id
    kpm_report_style=args.kpm_report_style
    ue_ids = list(map(int, args.ue_ids.split(",")))
    metrics=ALL_KPM_METRICS

   


    ##KpiCollector instance has being created
    print("In Main-initing the KPI Collector xApp")
    intelligentAllocator=IntelligentAllocator(config=config,http_server_port=http_server_port,rmr_port=rmr_port)
    intelligentAllocator.e2sm_kpm.set_ran_func_id(ran_func_id=ran_func_id)

    ##Connecting the exit signals
    signal.signal(signal.SIGQUIT,intelligentAllocator.signal_handler)
    signal.signal(signal.SIGTERM,intelligentAllocator.signal_handler)
    signal.signal(signal.SIGINT,intelligentAllocator.signal_handler)
    ##start the kpiCollector
    intelligentAllocator.start(e2_node_id=e2_node_id,ue_ids=ue_ids,metric_names=metrics)
    