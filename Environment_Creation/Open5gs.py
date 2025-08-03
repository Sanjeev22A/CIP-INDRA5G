import automation_CommonFunctions as Scope
from dotenv import load_dotenv
import os
load_dotenv("5g.env")


def start_open5gs_core(sudoEnabled=False,build=False):
    srsRAN_Project=os.getenv("srsRAN_Project")
    srsRAN_Docker=os.getenv("srsRAN_Core_Docker")
    srsRAN_Open5gs=os.getenv("srsRAN_Core_open5gs")
    password=os.getenv("password")
    if(sudoEnabled):

        if(build):command=f"echo {password} | sudo -S docker compose up --build 5gc"
        else:
            command=f"echo {password} | sudo -S docker compose up 5gc"
    else:
        if(build):command="docker compose up --build 5gc"
        else:
            command="docker compose up 5gc"
    Scope.open_cmd(srsRAN_Docker,command=command)

start_open5gs_core(True,True)