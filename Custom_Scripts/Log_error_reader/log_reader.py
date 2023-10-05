import datetime, os, shutil, paramiko, time
from scp import SCPClient
import pandas as pd


def log_reader(url, port, host_name, host_password):
    logs_path = "/home/torizon/temp"
    ssh.connect(url, port, host_name, host_password)
    ssh.exec_command("docker cp web:/var/log/voyager/ /home/torizon/temp/")
    time.sleep(10)
    stdin, stdout, stderr = ssh.exec_command(f"ls {logs_path}")
    out = stdout.readlines()
    files = [x.strip() for x in out]
    print("Getting log files.....")
    scp = SCPClient(ssh.get_transport())
    for x in files:
        scp.get(f"{logs_path}/{x}", "./logs")

    for file in files:
        log = open(f"./logs/{file}", 'r')

        for line in log:
            if 'ERROR' in line:
                with open("./error.csv", 'a') as wf:
                    wf.write(f"{file} {line}")
    ssh.close()


def check_disk_ram_usage(url, port, uname, passwd):
    print("Getting Disk and Ram Usage....")
    ssh.connect(url, port, uname, passwd)
    stdin1, stdout1, stderr1 = ssh.exec_command("df -h | grep /dev/disk/by-label/otaroot | awk '{print $3}'")
    disk_usage = stdout1.readline()
    ssh.connect(url, port, uname, passwd)
    stdin2, stdout2, stderr2 = ssh.exec_command("free -mh | grep Mem | awk '{print $3}'")
    ram_usage = stdout2.readline()
    return disk_usage.strip(), ram_usage.strip()


# CPU Temperature
def check_cpu_temp(url, port, uname, passwd):
    print("Getting CPU Temparature....")
    ssh.connect(url, port, uname, passwd)
    stdin3, stdout3, stderr3 = ssh.exec_command("cat /sys/class/thermal/thermal_zone0/temp")
    cpu_temp = stdout3.readline().split('\n')[0]
    return int(cpu_temp) / 1000


# Bluetooth
def check_bluetooth(url, port, uname, passwd):
    print("Checking Bluetooth....")
    ssh.connect(url, port, uname, passwd)
    ssh.exec_command("bluetoothctl power on && timeout 15s bluetoothctl scan on")
    stdin4, stdout4, stderr4 = ssh.exec_command('dmesg | grep "Blue"')
    cmd_output = stdout4.readlines()
    if "Bluetooth" in cmd_output[0].strip():
        return "Bluetooth is available."
    else:
        return "Bluetooth is not available."


# SD Card
def check_sd_card(url, port, uname, passwd):
    print("Checking SD Card....")
    ssh.connect(url, port, uname, passwd)
    stdin, stdout, stderr = ssh.exec_command("ls /dev/")
    output = stdout.readlines()
    for line in output:
        if "mmcblk1" in line.split('\n'):
            return "SD Card is available."
    else:
        return "SD Card is not available."


def check_board_temp(url, port, uname, passwd):
    print("Checking Board Temparature.....")
    ssh.connect(url, port, uname, passwd)
    stdin, stdout, stderr = ssh.exec_command("cat /sys/class/hwmon/hwmon0/temp1_input")
    board_temp = int(stdout.readlines()[0])/1000
    return board_temp


def cleaning(url, port, host_name, host_password):
    print("Cleaning work bench......")
    shutil.rmtree("./logs/")
    ssh.connect(url, port, host_name, host_password)
    ssh.exec_command("rm -rf /home/torizon/temp")
    time.sleep(5)
    f = ["error.csv", "error.xlsx"]
    for i in f:
        os.remove(f"./{i}")


def log_data_write_excel(final_file):
    print("Writing log errors to Excel....")
    log_f = []
    date_time = []
    error_msg = []
    df2 = pd.DataFrame()
    with pd.ExcelWriter("./error.xlsx", ) as file:
        pd.read_csv("./error.csv", sep="delimiter", header=None).to_excel(file)
    df1 = pd.read_excel("./error.xlsx", header=None)
    for i in range(1, df1.count()[0] + 1):
        log_f.append(df1[1][i].split()[0])
        try:
            date_time.append((datetime.datetime.strptime(df1[1][i].split()[1] + " " + df1[1][i].split()[2], "%Y-%m-%d %H:%M:%S,%f") + datetime.timedelta(hours=5, minutes=30)))
        except:
            date_time.append(" ")
        try:
            error_msg.append(df1[1][i].split(",")[1])
        except:
            error_msg.append(df1[1][i].split(" ")[1])
    df2["date_time"] = date_time
    df2["log_file"] = log_f
    df2["Error"] = error_msg
    df2.to_excel(final_file, sheet_name="log_errors")


def service_check(url, port, host_name, host_password):
    print("Checking service Status.....")
    df_active = pd.DataFrame()
    df_inactive = pd.DataFrame()
    ser_act = []
    status_act = []
    uptime_act = []
    ser_ina = []
    status_ina = []
    ssh.connect(url, port, host_name, host_password)
    stdin, stdout, stderr = ssh.exec_command("docker exec -t web supervisorctl status")
    time.sleep(5)
    out = [x.strip().split() for x in stdout.readlines()]
    for service in out:
        if service[1] == "RUNNING":
            ser_act.append(service[0])
            status_act.append(service[1])
            uptime_act.append(service[-1])
        else:
            ser_ina.append(service[0])
            status_ina.append(service[1])
    df_active['Service'] = ser_act
    df_active["Status"] = status_act
    df_active["Uptime"] = uptime_act
    df_inactive["Service"] = ser_ina
    df_inactive["Status"] = status_ina
    return df_active, df_inactive


def system_metrics_excel_writer(url, port, host_name, host_password, final_file):
    print("Writing System metrics.....")
    data = {}
    disk_ram = check_disk_ram_usage(url, port, host_name, host_password)
    data["Disk Usage"] = [disk_ram[0]]
    data["RAM Usage"] = [disk_ram[1]]
    data['CPU Temp'] = [check_cpu_temp(url, port, host_name, host_password)]
    data["Bluetooth"] = [check_bluetooth(url, port, host_name, host_password)]
    data["SD Card"] = [check_sd_card(url, port, host_name, host_password)]
    data["Board Temp"] = [check_board_temp(url, port, host_name, host_password)]
    df3 = pd.DataFrame.from_dict(data)
    df3.to_excel(final_file, sheet_name="System Data")


def service_check_excel_writer(url, port, host_name, host_password, final_file):
    print("Writing service status to excel....")
    df_act, df_inact = service_check(url, port, host_name, host_password)
    df_act.to_excel(final_file, sheet_name="Active Services")
    df_inact.to_excel(final_file, sheet_name="Inactive Services")

def main(url, port, host_name, host_password):
    try:
        cleaning(url, port, host_name, host_password)
    except:
        pass
    os.makedirs("./logs")
    log_reader(url, port, host_name, host_password)
    with pd.ExcelWriter(f"./log_errors_system_data_{datetime.datetime.now()}.xlsx") as final_file:
        log_data_write_excel(final_file)
        system_metrics_excel_writer(url, port, host_name, host_password, final_file)
        service_check_excel_writer(url, port, host_name, host_password, final_file)
    cleaning(url, port, host_name, host_password)



url = "192.168.95.7"
port = 22
host_name = "torizon"
host_password = 'sunshine'
ssh = paramiko.SSHClient()
ssh.load_system_host_keys()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
main(url, port, host_name, host_password)
# print(service_check(url, port, host_name, host_password))