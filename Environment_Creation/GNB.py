import automation_CommonFunctions as Scope
from dotenv import load_dotenv
import os

load_dotenv("5g.env")

def singleUEGNB(filename, outputFile, testModeFile, traceFile, sudo=True):
    config_dir = os.getenv("srsRAN_SingleUE")
    log_dir = os.getenv("Log_Single_UE")
    
    if not config_dir or not log_dir:
        print("Error: Environment variables missing!")
        return
    
    outputFile = f"{log_dir}/{outputFile}"  # gNB logs
    testModeFile = f"{log_dir}/{testModeFile}"  # Test mode logs
    traceFile = f"{log_dir}/{traceFile}"  # Trace logs
    
    print(f"gNB logs: {outputFile}")
    print(f"Test Mode logs: {testModeFile}")
    print(f"Trace logs: {traceFile}")

    # Define gNB logging command
    log_command = f"gnb -c {filename} log --filename {outputFile}"

    # Define gNB test_mode command
    test_mode_command = f"gnb -c {filename} test_mode --enable_json_metrics --pdcp_report_period 1000 --rlc_report_period 1000"

    # Define tracing command
    trace_command = f"gnb -c {filename} log --tracing_filename {traceFile}"

    # Combine all commands and store logs
    full_command = f"{log_command} && {test_mode_command} | tee {testModeFile} && {trace_command}"

    if sudo:
        full_command = f"sudo bash -c '{full_command}'"

    Scope.open_cmd(config_dir, command=full_command)

# Call function
singleUEGNB("gnb_zmq.yaml", "gnb.log", "test_mode.log", "trace.log", True)