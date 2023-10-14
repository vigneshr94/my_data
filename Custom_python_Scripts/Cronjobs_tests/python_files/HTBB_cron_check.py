from cron_check_utils import *
from time import sleep
import requests

def check_HTBB_based_on_state(state):
    toggle_log = last_run_status("toggle")
    xbee_log = check_xbee_backend_log("HTBB")
    if state == "reboot":
        logger.info("checking backtracking at reboot")
        reboot_time = last_reboot_time_in_cron()
        logger.info(f"last_system_rebooted: {reboot_time}")
        logger.info(f"Last HTBB sent: {toggle_log[0]} hrs")
        if xbee_log["VALUE"] == 1:
            if reboot_time in toggle_log:
                logger.info("Successfully HTBB sent at reboot.\t\tPASSED")
        else:
            logger.info("HTBB not sent at Reboot.\t\tFAILED")
    elif state == "midnight":
        logger.info("checking backtracking at midnight")
        toggle_at_midnight = filter_midnight_time_stamps(toggle_log)
        zc_utc_time = (get_zc_time()[1] - timedelta(hours= 1)).hour
        if len(toggle_at_midnight) > 0:
            if xbee_log['VALUE'] == 1:
                if int(toggle_at_midnight[0].strftime("%H")) == zc_utc_time:
                    logger.info("Successfully HTBB sent at midnight.\t\tPASSED")
        else:
            logger.info("HTBB not sent at midnight.\t\tFAILED")
    else:
        logger.debug("Default state.")


def check_service():
    SSH.connect(url, port, host_name, host_password)
    ssh_read = SSH.open_sftp()
    with ssh_read.open("/home/torizon/voyager/verdin/vzc/etc/voyager/tracking/settings.json", "r") as r:
        _tbb_state = r.read().decode("utf-8", errors="ignore")
    SSH.close()
    tbb_state = json.loads(_tbb_state)["terrain_based_backtracking"]
    if tbb_state["SUNPATH_TOGGLE"] != "disabled":
        return True
    else:
        service = requests.post(TOGGLE,
                                   data= {"FEATURE_TYPE": "terrain_based_backtracking", "SUNPATH_TOGGLE": "all"})
        if service.status_code == 200:
            return True
        else:
            return False


def HTBB_cron_check():
    logger.info("************* CHECK HTBB CRONJOB STARTED**************")
    while True:
        tbb_state = check_service()
        if tbb_state:
            state = generate_query_time()
            if (state == "reboot") or (state == "midnight"):
                try:
                    logger.info(f"Checking HTBB cron at {state}")
                    check_HTBB_based_on_state(state)
                except Exception as e:
                    logger.error(str(e))
                    logger.error(traceback.format_exc())
        else:
            logger.info("Backtracking is not Enabled.")
        sleep(time_to_wait)



if __name__ == "__main__":
    HTBB_cron_check()