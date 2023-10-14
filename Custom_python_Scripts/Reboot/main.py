# Importing necessary libraries
import paramiko, time, sys, datetime


# initilize SSH client
def reboot(url, port, host_name, host_password):
    ssh.connect(url, port, host_name, host_password)
    stdin, stdout, stderr = ssh.exec_command("sudo -S reboot")
    stdin.write("sunshine\n")
    stdin.flush()
    time.sleep(5)

# Function to Checking backend services
def services(url, port, host_name, host_password):
    service = ['bq', 'collectionsCheck', 'commandQueue', 'mcuCollector', 'miscAlerts', 'modbus', 'periodicRequests', 'processHealthMonitor', 'timePublisher', 'webApp', 'xbeeBackendApi', 'zcEngine', 'zcMqttHelper']
    ssh.connect(url, port, host_name, host_password)
    stdin, stdout, stderr = ssh.exec_command("docker exec -t web supervisorctl status")
    out = [x.strip().split() for x in stdout.readlines()]
    active = []
    inactive = []
    for s in out:
        if s[1] == 'RUNNING':
            active.append(s[0])
        else:
            inactive.append(s[0])
    for act in active:
        if act in service:
            return True, active, inactive
        else:
            return False, active, inactive

# Function to check log files backup before and after restarting
def log_backup_check(url, port, host_name, host_password):
    ssh.connect(url, port, host_name, host_password)
    stdin, stdout, stderr = ssh.exec_command("docker exec -t web ls -lh /var/log/voyager")
    flist = [x.strip() for x in stdout.readlines()][1:]
    fname = [y.split()[8] for y in flist]
    fcdate = [' '.join(z.split()[5:7]) for z in flist]
    out = {}
    for name in fname:
        for date in fcdate:
            out[name] = date
    return out

# Function to validate the log file backup check
def validating_log_files(before_reboot, after_reboot):
    if before_reboot == after_reboot:
        return set(before_reboot.values()) == set(after_reboot.values())
    else:
        return False


# Function to write the report to a file
def write_file(data, i, log_files_check):
    file = open(f"./Output/Report_{url}_{str(datetime.datetime.now()).replace(':','_').split('.')[0]}.txt", 'a')
    file.write(f"Reboot time: {datetime.datetime.now()}")
    file.write("\t\t")
    file.write(f"ZC URL: {url}")
    file.write("\n")
    file.write(f"Reboot Test {i} state: {data[0]}")
    file.write("\n")
    file.write(f"Reboot Test {i} active services: {data[1]}")
    file.write("\n")
    file.write(f"Reboot Test {i} inactive services: {data[2]}")
    file.write("\n")
    file.write(f"Log files status after reboot ZC: {log_files_check}")
    file.write("\n")
    file.write(f"***** Reboot Test {i} is completed *****")
    file.write("\n")
    file.write("\n")


# Main Function to run all above functions
def main(url, port, host_name, host_password, loop_runs):
    for i in range(0, loop_runs):
        print(f"Reboot: {i+1}")
        b_reboot = log_backup_check(url, port, host_name, host_password)
        reboot(url, port, host_name, host_password)
        print("Rebooting the ZC......")
        print("ZC is Rebooting wait for 7 minutes.")
        for j in range(7):
            print(f"Wait for {7-j} minutes...")
            time.sleep(60)
        try:
            try:
                print("Trying to reconnect...")
                print("Checking services after Reboot.....")
                data = services(url, port, host_name, host_password)
                a_reboot = log_backup_check(url, port, host_name, host_password)
            except:
                print("Reconnect failed wait for 10 minutes...")
                for k in range(4):
                    print(f"Waiting for {4-k} minutes...")
                    time.sleep(60)
                data = services(url, port, host_name, host_password)
                print("Checking services after Reboot.....")
                a_reboot = log_backup_check(url, port, host_name, host_password)
            log_file_check = validating_log_files(b_reboot, a_reboot)
            write_file(data, i+1, log_file_check)
        except:
            print("ZC is not accessible.")


# initilize Varilable
url = sys.argv[1]
port = 22
host_name = "torizon"
host_password = "sunshine"
loop_runs = 1
ssh = paramiko.SSHClient()
ssh.load_system_host_keys()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())


if __name__ == "__main__":
    main(url, port, host_name, host_password, loop_runs)

