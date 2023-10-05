# Importing requried libraries
import os
import traceback
import paramiko
import logging
import json
import sys
import subprocess
import pytz
from time import sleep
from logging.handlers import RotatingFileHandler
from datetime import datetime
from datetime import timedelta
from urllib.request import urlopen
import re

# Declaring Global Variables
global SSH
global TIMEZONE
global time_to_wait
global TOGGLE

# Initialising required Variables
url = sys.argv[1]  # IP address of the Zone Controller
# url = "192.168.1.125"
port = 22  # ssh port
host_name = "torizon"  # Zone Controller User name
host_password = "sunshine"  # Zone Controller Password
time_to_wait = 3600  # Time to wait for next cron check in seconds
log_file = sys.argv[2]
# log_file = "pull_hw_clk"
SSH = paramiko.SSHClient()  # Intializing SSH client
SSH.load_system_host_keys()  # Loading System host keys for known_hosts file
subprocess.run(f"ssh-keygen -R {url}", shell=True)  # Removing old ssh keys for the ZC IP address
sleep(5)
SSH.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # Adding New ssh-key for the ZC IP address
TIMEZONE = f"http://{url}/flask/time/get"  # Get API for getting Zone Controller time
TOGGLE = f"http://{url}/flask/tracking"


def last_reboot_time_in_cron():
    """
    Get the last reboot time from the cron.log from the ZC
    :return: Last ZC rebooted time:datetime object
    """
    try:
        SSH.connect(url, port, host_name, host_password)
        cron_log = SSH.open_sftp().open("/home/torizon/log/cron.log", 'r').readlines()
        for line in cron_log[::-1]:
            if "Running crons at reboot." in line:
                _time = datetime.strptime(line.split(",")[0], "%Y-%m-%d %H:%M:%S")
                SSH.close()
                return _time
    except Exception as e:
        logger.error(str(e))


def last_midnight_time_in_cron():
    try:
        SSH.connect(url, port, host_name, host_password)
        cron_log = SSH.open_sftp().open("/home/torizon/log/cron.log", 'r').readlines()
        for line in cron_log[::-1]:
            if "Running crons on midnight." in line:
                _time = datetime.strptime(line.split(",")[0], "%Y-%m-%d %H:%M:%S")
                SSH.close()
                return _time
    except Exception as e:
        logger.error(str(e))


def last_run_status(log_name):
    """
    Gets last time sync timestamp from time_sync.log
    :param log_name: log file name to check:str
    :return: List of time stamps in the log file:List of datetime objects
    """
    SSH.connect(url, port, host_name, host_password)
    if log_name == "time_sync":
        try:
            ssh_read = SSH.open_sftp()
            with ssh_read.open("/home/torizon/log/time_sync.log", 'r') as r:
                time_sync_log = r.readlines()
            _time = [datetime.strptime(line.split(",")[0], "%Y-%m-%d %H:%M:%S") for line in time_sync_log[::-1] if
                     "Calling GPS" in line]
            SSH.close()
            return _time
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
    elif log_name == "pullhwclk":
        try:
            pull_clk = SSH.open_sftp().open("/home/torizon/log/pullTimeFromHWclock.log", "r").readlines()
            _time = datetime.strptime(pull_clk[-2].strip().split("+")[0].split(".")[0], "%Y-%m-%d %H:%M:%S").hour
            SSH.close()
            return _time
        except Exception as e:
            logger.error(str(e))
    elif log_name == "toggle":
        try:
            ssh_read = SSH.open_sftp()
            with ssh_read.open("/home/torizon/log/backtracking_cronjob.log", "r") as r:
                toggle = r.readlines()
            _time = [datetime.strptime(line.split(",")[0], "%Y-%m-%d %H:%M:%S") for line in toggle[::-1] if
                     "Running cron for the day" in line]
            SSH.close()
            return _time
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
    elif log_name == "shutdown":
        try:
            ssh_read = SSH.open_sftp()
            with ssh_read.open("/home/torizon/log/check_shutdown_status.log", "r") as shutdown_log:
                shutdown_log = shutdown_log.readlines()
            _time = [datetime.strptime(line.split(",")[0], "%Y-%m-%d %H:%M:%S") for line in shutdown_log[::-1]]
            SSH.close()
            return _time
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
    elif log_name == "tmpcleanup":
        try:
            ssh_read = SSH.open_sftp()
            with ssh_read.open("/home/torizon/log/tmpCleanup.log", "r") as r:
                tmpclean = r.readlines()
            _time = [datetime.strptime(line.split(",")[0], "%Y-%m-%d %H:%M:%S") for line in tmpclean[::-1] if
                     ("tmp size greater than 1 GB, so rebooting ZC" in line) or
                     ("tmp size lesser than 1 GB, so OK." in line)]
            SSH.close()
            return _time
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
    elif log_name == "rc_time_push":
        try:
            ssh_read = SSH.open_sftp()
            with ssh_read.open("/home/torizon/log/misc.log", "r") as r:
                misc_log = r.readlines()
            _time = [datetime.strptime(line.split(",")[0], "%Y-%m-%d %H:%M:%S") for line in misc_log[::-1] if
                     ("Setting ZC time to all rovers" in line)]
            SSH.close()
            return _time
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())



def filter_time_stamp_for_six_hours(time_stamps):
    """
    Gets timeStamp from log file for six hours
    :param time_stamps: List of timeStamps:List of datetime object
    :return: List of timeStamps with 6 hours interval:List of datetime object
    """
    six_hrs_time_stamps = []
    for _ in time_stamps:
        _time = int(_.hour)
        if _time % 6 == 0:
            six_hrs_time_stamps.append(_)
    return six_hrs_time_stamps


def filter_midnight_time_stamps(time_stamps):
    """
    Get timeStamp from log file for every midnight
    :param time_stamps: List of timeStamps:List of datetime object
    :return: List of timeStamps:List of datetime object
    """
    utc_time = (get_zc_time()[1] - timedelta(hours=1)).hour
    midnight_time_stamps = []
    for _ in time_stamps:
        _time = int(_.hour)
        if _time == utc_time:
            midnight_time_stamps.append(_)
    return midnight_time_stamps


def get_zc_time():
    """
    Gets time on zone controller
    :return: list of timeStamps:List of datetime object
            0: UI time 1: backend time
    """
    with urlopen(TIMEZONE) as r:
        _time_from_api = json.loads(r.read().decode())['message']
    zc_UI_time = datetime.strptime(_time_from_api, "%a, %b %d %Y %H:%M:%S")
    zc_backend_time = zc_UI_time.astimezone(pytz.UTC)
    return zc_UI_time, zc_backend_time


def check_for_zc_reboot():
    """
    Check the ZC uptime to check the reboot cron
    :return: timeStamp in minutes:datetime object
    """
    SSH.connect(url, port, host_name, host_password)
    stdin, stdout, stderr = SSH.exec_command("echo $(awk '{print $1}' /proc/uptime) / 60 | bc")
    output = stdout.readline()
    SSH.close()
    up_time = int(output.strip())
    return up_time


def generate_query_time():
    """
    Generates the state for checking cron at reboot, every 6 hrs and midnight
    :return: state string:str
    """
    _time = get_zc_time()[0]
    # logger.info(f"Time in ZC: {_time}")
    up_time = check_for_zc_reboot()
    # logger.info(f"ZC Uptime: {up_time} mins")
    if up_time <= 20:
        return "reboot"
    elif int(_time.hour) % 6 == 0:
        return "six_hour"
    elif _time.hour == "01":
        return "midnight"
    else:
        return "default"

def check_xbee_backend_log(cmd):
    SSH.connect(url, port, host_name, host_password)
    xbee_backend = SSH.open_sftp().open("/home/torizon/log/xbee_backend.log", "r").readlines()
    htbb = []
    SSH.close()
    for _ in xbee_backend[::-1]:
        match = re.search("Sent unicast: {.+?}", _)
        if match:
            _json = re.search("{.+?}", match.group())
            _string = json.loads(_json.group())
            if _string["CMD"] == cmd:
                htbb.append(_string)

# Logging setup
log_formatter = logging.Formatter("%(asctime)s %(levelname)s " + log_file  + "(%(lineno)d): %(message)s")
logFile = os.getcwd() + f"/log/{log_file}.log"
rotatingFileHandler = RotatingFileHandler(logFile, mode='a', maxBytes=5 * 1024 * 1024, backupCount=5, encoding=None,
                                          delay=0)
rotatingFileHandler.setFormatter(log_formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(rotatingFileHandler)
