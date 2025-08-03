import automation_CommonFunctions as Scope
from dotenv import load_dotenv
import os
import subprocess
import time
load_dotenv("5g.env")

def singleUEGNB(filename, outputFile, sudo=True):
    config_dir = os.getenv("srsRAN_SingleUE")
    log_dir = os.getenv("Log_Single_UE")
    password = os.getenv("password")
    
    if not config_dir or not log_dir:
        print("Error: Environment variables missing!")
        return
    
    filename = f"{filename}"
    outputFile = f"{log_dir}/{outputFile}"
    print(f"Logging to: {outputFile}")
    
    if sudo:
       
        command = f"sudo srsue {filename} | tee {outputFile}"

    else:
        command = f"sudo srsue {filename} | tee {outputFile}"
    #Scope.open_cmd(config_dir,command=commandThrow)
    Scope.open_cmd(config_dir,command=command)
    
singleUEGNB("ue_zmq.conf", "ue.log", True)
