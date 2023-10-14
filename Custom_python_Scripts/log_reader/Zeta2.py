# Importing the necessary modules
import datetime, os, shutil, paramiko
from scp import SCPClient
import pandas as pd
import sys

# Declaring Global Variables
global LOG_PATH
global files
global final_file

# Declaring Local Variables
url = "192.168.95.25"
LOG_PATH = "/var/log/voyager"
port = 22
host_name = "pi"
host_password = 'sunshine'


# Downloading the logs from the Zone Controller
def getting_log_files(url):
    # os.makedirs("./logs")
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.connect(url, port, host_name, host_password)
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    stdin, stdout, stderr = ssh.exec_command(f"ls {LOG_PATH}")
    out = stdout.readlines()
    files = [x.strip() for x in out]
    # scp = SCPClient(ssh.get_transport())
    # for x in files:
    #     print(f"Downloading the log file {x}")
    #     scp.get(f"{LOG_PATH}/{x}", "./logs")
    return files

# Reading the Downloaded log file
def get_error_message_from_logs(files):
    for file in files:
        try:
            log = open(f"./logs/{file}", 'r')
            for line in log:
                if 'ERROR' in line:
                    with open("./logs/error.csv", 'a') as wf:
                        wf.write(f'{file} {line}')
        except:
            continue

# Creating the excel file with the errror messages
def creating_excel_file(url):
    log_f = []
    date_time = []
    error_msg = []
    df2 = pd.DataFrame()
    with pd.ExcelWriter("./logs/error.xlsx") as file:
        pd.read_csv("./logs/error.csv", sep="delimiter", header=None).to_excel(file)
        file.save()
    df1 = pd.read_excel("./logs/error.xlsx", header=None, index_col=False, sep="delimiter")
    for i in range(1, df1.count()[0] + 1):
        try:
            log_f.append(df1[1][i].split()[0])
            date_time.append((datetime.datetime.strptime(df1[1][i].split()[1] + " " + df1[1][i].split()[2], "%Y-%m-%d %H:%M:%S,%f") + datetime.timedelta(hours=5, minutes=30)))
            error_msg.append(df1[1][i].split(",")[1])
        except:
            continue
    df2["date_time"] = date_time
    df2["log_file"] = log_f
    df2["Error"] = error_msg
    with pd.ExcelWriter(f"./log_errors_{url}_{str(datetime.datetime.now()).replace(':','_').split('.')[0]}.xlsx") as final_file:
        df2.to_excel(final_file)

# Cleaning up the work directory after/before starting the script
def work_desk_cleanup():
    shutil.rmtree("./logs/")


# main funcion to run the script
def main(url):
    # try:
    #     work_desk_cleanup()
    # except:
    #     print("No files to clean.")
    #     print("Going on to get the logs....")
    # print("Downloading the logs from ZC....")
    files = getting_log_files(url)
    print("Logs successfully downloaded....")
    print("Reading the log files for errors....")
    get_error_message_from_logs(files)
    print("All logs read successfully....")
    print("Generating the excell file....")
    creating_excel_file(url)
    print(f"Excel file successfully created with name log_errors_{url}_{str(datetime.datetime.now()).replace(':','_').split('.')[0]}.xlsx....")
    print("Cleaning the work desk...")
    work_desk_cleanup()
    print("Task finished successfully.")


if __name__ == "__main__":
    main(url)
