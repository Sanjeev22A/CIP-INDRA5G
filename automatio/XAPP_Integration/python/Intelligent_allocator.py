import datetime 
import argparse
import signal
from lib.xAppBase import xAppBase
import time
import gym
from gym import spaces
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
    def __init__(self,num_ues,total_prbs):
        super(PRBAllocationEnv,self).__init__()
        self.num_ues=num_ues
        self.total_prbs=total_prbs
        self.action_space=spaces.Discrete(3**num_ues)
        self.observation_space = spaces.Box(low=0, high=self.total_prbs, shape=(num_ues,), dtype=np.int32)
        self.state=np.ones(self.num_ues)*(self.total_prbs//self.num_ues)

    def reset(self):
        self.state=np.ones(self.num_ues)*(self.total_prbs//self.num_ues)
        return self.state
    def step(self, action, kpi_dict, slice_type):
        action_arr = self.decode_action(action)
        tentative_state = self.state + action_arr
        tentative_state = np.clip(tentative_state, 0, self.total_prbs)
        
        total_allocated = np.sum(tentative_state)
        if total_allocated > self.total_prbs:
            scaling_factor = self.total_prbs / total_allocated
            tentative_state = np.floor(tentative_state * scaling_factor).astype(int)

        self.state = tentative_state
        reward = self.compute_reward(self.state, kpi_dict, slice_type)
        done = False

        return self.state, reward, done, {}

    def decode_action(self,action):
        action_arr = []
        for i in range(self.num_ues):
            action_arr.append((action // (3 ** (self.num_ues - i - 1))) % 3 - 1) 
        return np.array(action_arr)
    def compute_reward(self, state, kpi_dict, slice_type):
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
                b_expected=22 # example volume threshold
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
