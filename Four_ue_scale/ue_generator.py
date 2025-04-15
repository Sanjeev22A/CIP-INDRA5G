import csv
import os

template="""
[rf]
freq_offset = 0
tx_gain = 50
rx_gain = 40
srate = 11.52e6
nof_antennas = 1

device_name = zmq
device_args = tx_port=tcp://127.0.0.1:{tx_port},rx_port=tcp://127.0.0.1:{rx_port},base_srate=11.52e6

[rat.eutra]
dl_earfcn = 2850
nof_carriers = 0

[rat.nr]
bands = 3
nof_carriers = 1
max_nof_prb = 52
nof_prb = 52

[pcap]
enable = none
mac_filename = /tmp/ue{id}_mac.pcap
mac_nr_filename = /tmp/ue{id}_mac_nr.pcap
nas_filename = /tmp/ue{id}_nas.pcap

[log]
all_level = info
phy_lib_level = none
all_hex_limit = 32
filename = /tmp/ue{id}.log
file_max_size = -1

[usim]
mode = soft
algo = milenage
opc  = {opc}
k    = {k}
imsi = {imsi}
imei = {imei}

[rrc]
release = 15
ue_category = 4

[nas]
apn = srsapn
apn_protocol = ipv4

[gw]
netns = ue{id}
ip_devname = tun_srsue
ip_netmask = 255.255.255.0

[gui]
enable = false

"""

def generate_ue_configs(csv_path="subscriber_db.csv",output_dir="",base_tx_port=2101,base_rx_port=2100):
    with open(csv_path,newline='') as csvfile:
        reader=csv.DictReader(csvfile)
        for index,row in enumerate(reader):
            id=index
            imsi="00"+row['imsi']
            
            imei=row['imei']
            opc=row['opc']
            print(opc)
            k=row['k']
            print(k)
            
            tx_port=base_tx_port+100*id
            rx_port=base_rx_port+100*id
            config=template.format(
                imsi=imsi,imei=imei,opc=opc,k=k,id=id,tx_port=tx_port,rx_port=rx_port
            )
            ##Command to set the net interface for the ues to connect to
            command=f"sudo ip netns add ue{id}"
            exit_code=os.system(command)
            print("Status : ",exit_code)
            config_filename=f"ue_{id}.conf"

            with open(config_filename,"w") as f:
                f.write(config)
            #print(f"Generated: {config_filename}")

generate_ue_configs()
