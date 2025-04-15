#!/usr/bin/env python3
import datetime
import argparse
import signal
from lib.xAppBase import xAppBase
import time
from RLAgent import RLAgent


class PrbAllocator(xAppBase):
    def __init__(self,config,http_server,rmr_port):
      
        print("Initializing the PRB Allocator xApp")
    
        super(PrbAllocator,self).__init__(config=config,http_server_port=http_server,rmr_port=rmr_port)
    

    def my_subscription_callback(self,e2_agent_id,subscription_id,indication_hdr,indication_msg,kpm_report_style,ue_id):
       
       indication_hdr=self.e2sm_kpm.extract_hdr_info(indication_hdr)
       message_data=self.e2sm_kpm.extract_meas_data(indication_msg)

       print(f"E2SM_KPM RIC Indication Content: {indication_hdr}")
       print(f"Message Data: {message_data}")
       print("\n\n\n")
    ##e2_node_id- id of the gnb
    ##ue_id-id of the ue
    @xAppBase.start_function
    def start(self,e2_node_id,ue_id):
        print("Starting the PRB Allocator xApp")
        while self.running:
            min_prb_ratio=1
            max_prb_ratio=5
            current_time=datetime.datetime.now()
            print(f"Send RIC Control request to E2 node: {e2_node_id} for the UE : {ue_id}")
            self.e2sm_rc.control_slice_level_prb_quota(e2_node_id,ue_id,min_prb_ratio=min_prb_ratio,max_prb_ratio=max_prb_ratio,dedicated_prb_ratio=100,ack_request=1)
            time.sleep(5)



            min_prb_ratio=1
            max_prb_ratio=40
            current_time=datetime.datetime.now()
            print(f"Send RIC Control request to E2 node: {e2_node_id} for the UE : {ue_id}")
            self.e2sm_rc.control_slice_level_prb_quota(e2_node_id,ue_id,min_prb_ratio=min_prb_ratio,max_prb_ratio=max_prb_ratio,dedicated_prb_ratio=100,ack_request=1)
            time.sleep(5)


            min_prb_ratio=1
            max_prb_ratio=100
            current_time=datetime.datetime.now()
            print(f"Send RIC Control request to E2 node: {e2_node_id} for the UE : {ue_id}")
            self.e2sm_rc.control_slice_level_prb_quota(e2_node_id,ue_id,min_prb_ratio=min_prb_ratio,max_prb_ratio=max_prb_ratio,dedicated_prb_ratio=100,ack_request=1)
            time.sleep(5)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description="PRB allocation framework")
    parser.add_argument("--config",type=str,default='',help='Here have the path of xApp config files')
    parser.add_argument("--http_server_port",type=int,default=8090,help="Http server port for REST listens here....")
    parser.add_argument("--rmr_port",type=int,default=4560,help="RMR port listens here...")
    parser.add_argument("--e2_node_id",type=str,default='gnbd_001_001_00019b_0',help="E2/gnb node id...")
    parser.add_argument("--ran_func_id",type=int,default=3,help="E2SM RC RAN FUNCTION ID")
    parser.add_argument("--ue_id", type=int, default=0, help="UE ID")

    args=parser.parse_args()
    config=args.config
    http_server_port=args.http_server_port
    rmr_port=args.rmr_port
    e2_node_id=args.e2_node_id
    ue_id=args.ue_id
    ran_func_id=args.ran_func_id
    
    ##prbAllocator instance has been created
    print("In Main-initing the PRB Allocator xApp")
    prbAllocator=PrbAllocator(config=config,http_server=http_server_port,rmr_port=rmr_port)
    prbAllocator.e2sm_rc.set_ran_func_id(ran_func_id=ran_func_id)

    ##Connecting the exit signals
    signal.signal(signal.SIGQUIT,prbAllocator.signal_handler)
    signal.signal(signal.SIGTERM,prbAllocator.signal_handler)
    signal.signal(signal.SIGINT,prbAllocator.signal_handler)

    ##start the prbAllocator
    prbAllocator.start(e2_node_id=e2_node_id,ue_id=ue_id)

