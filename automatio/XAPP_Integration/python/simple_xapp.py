#!/usr/bin/env python3
import argparse
import signal
import time
import os
from lib.xAppBase import xAppBase
import csv
from datetime import datetime, timezone

class KpiCollector(xAppBase):
    def __init__(self,config,http_server_port,rmr_port):
        super(KpiCollector,self).__init__(config,http_server_port,rmr_port)
        self.kpi_data={}

    

    def my_subscription_callback(self, e2_agent_id, subscription_id, indication_hdr, indication_msg, kpm_report_style, ue_id):
        print("Subscription callback triggered : ", kpm_report_style)
        print(f"UE-id:ue{ue_id}")
        print()

        indication_hdr = self.e2sm_kpm.extract_hdr_info(indication_hdr)
        message_data = self.e2sm_kpm.extract_meas_data(indication_msg)

        # Create output directory
        os.makedirs("dataset", exist_ok=True)

        # Define output file
        filename = f"dataset/ue{ue_id}.csv"

        # Get current timestamp
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

        # Extract and flatten data
        meas_data = message_data.get('measData', {})
        granul_period = message_data.get('granulPeriod', None)

        # Prepare row dictionary
        metric_row = {'timestamp': timestamp, 'granulPeriod': granul_period}
        for metric_name, value_list in meas_data.items():
            value = value_list[0] if isinstance(value_list, list) and value_list else None
            metric_row[metric_name] = value

        # Write to CSV
        file_exists = os.path.isfile(filename)
        with open(filename, mode='a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=metric_row.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(metric_row)

        print("Data written!")
        print("\n\n\n")

    @xAppBase.start_function
    def start(self,e2_node_id,ue_ids,metric_names):
        report_period=1000
        granul_period=1000

        ##Style 2 callback
        print(f"Before call : Subscribed to E2 node ID: {e2_node_id}, RAN func: e2sm_kpm, Report Style: 2, metrics: {metric_names}")
        for i in range(4):
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
    kpiCollector=KpiCollector(config=config,http_server_port=http_server_port,rmr_port=rmr_port)
    kpiCollector.e2sm_kpm.set_ran_func_id(ran_func_id=ran_func_id)

    ##Connecting the exit signals
    signal.signal(signal.SIGQUIT,kpiCollector.signal_handler)
    signal.signal(signal.SIGTERM,kpiCollector.signal_handler)
    signal.signal(signal.SIGINT,kpiCollector.signal_handler)
    ##start the kpiCollector
    kpiCollector.start(e2_node_id=e2_node_id,ue_ids=ue_ids,metric_names=metrics)
    
