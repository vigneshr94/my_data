import paramiko, json, time, os, datetime, re
import pandas as pd


def cleaning_workbench(url, port, host_name, host_password):
    ssh.connect(url, port, host_name, host_password)
    try:
        ssh.exec_command(f"rm {remote_log_file}")
    except:
        pass


def get_log_data(url, port, host_name, host_password):
    ssh.connect(url, port, host_name, host_password)
    ssh.exec_command(f"docker cp web:/var/log/voyager/xbee_backend.log {remote_log_file}")
    time.sleep(10)
    out = ssh.open_sftp().open(remote_log_file, "r").readlines()
    xbee_backend = [x.strip() for x in out]
    return xbee_backend


def filtering_dst2_response(data):
    dst2_response = []
    for x in data:
        found = re.search("Received:{.*}", x)
        if found:
            rec = json.loads(re.search("{.*}", found.group()).group())
            if rec["CMD"] == "DST2":
                dst2_response.append(rec)
        else:
            continue
    return dst2_response


def writing_to_excel(data, file):
    code_dict = {1: "Over current fault", 2: 'Minimum Battery Voltage fault', 4: 'Overboard temperature fault',
                 6: "Motor stall fault", 7: ' Zigbee fault', 8: 'Communication fault', 9: 'Inclinometer Fault',
                 10: " SPI Flash Memory Error", 11: " OTA Fault", 12: " EEPROM Fault", 13: ' RTC Fault',
                 14: 'Unknown Fault', 15: ' Locking System Fault', 16: ' Locked Track Move Fault',
                 17: 'Low Battery Stow Fault', 18: 'Mechanical Overload Fault', 19: 'Battery Charger Fault',
                 20: 'Estop Fault', 21: 'BLE Fault', 22: 'External EEPROM Fault', 33: 'ZC Blocked State Enabled',
                 34: 'Set Command Flag Enabled', 35: ' Mechanical Overload Occurred'
                 }
    df = pd.DataFrame()
    ts = []
    did = []
    cmd = []
    cid = []
    val = []
    mode = []
    error_code = []
    code = []
    for i, x in enumerate(data):
        ts.append(datetime.datetime.fromtimestamp(int(x["TS"])))
        did.append(x["DID"])
        cmd.append(x['CMD'])
        cid.append(x['CID'])
        val.append(x["VALUES"])
        mode.append(val[i].split(",")[0][1:])
        code.append(val[i].split(",")[3])
    for j in code:
        code_bin = bin(int(j, 16))[2:][::-1]
        code_rep = []
        for n, k in enumerate(code_bin):
            if k == "1":
                code_rep.append(code_dict[n])
        error_code.append(code_rep)
    df["Time"] = ts
    df["Device ID"] = did
    df["Command"] = cmd
    df["CID"] = cid
    df["Mode"] = mode
    df["Error_code"] = error_code
    df["Values"] = val
    df.to_excel(file, sheet_name=str(datetime.datetime.fromisoformat(str(datetime.datetime.now()))).replace(":", "_"),
                index=False)


url, port, host_name, host_password = ["192.168.95.7", 22, "torizon", "sunshine"]
ssh = paramiko.SSHClient()
ssh.load_system_host_keys()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
wd = os.getcwd()
remote_log_file = "/home/torizon/xbee_backend"

if __name__ == "__main__":
    cleaning_workbench(url, port, host_name, host_password)
    data = filtering_dst2_response(get_log_data(url, port, host_name, host_password))
    with pd.ExcelWriter(f"dst2_command_{url}_{(str(datetime.datetime.fromisoformat(str(datetime.datetime.now()))).replace(':', '_')).split('.')[0]}.xlsx") as file:
        writing_to_excel(data, file)
