from cron_check_utils import *
from time import sleep


def check_cron_based_on_state(state, time_sync):
    """
    Check the cron based on the ZC status
    :param state: state to check the cron: str
    :param time_sync: list of timeStamps from the time_sync.log: list of datetime objects
    :return: None
    """
    if state == "reboot":
        logger.info("Checking time sync at reboot")
        time_sync_at_reboot = [_.hour for _ in time_sync]
        last_system_reboot_time = last_reboot_time_in_cron()
        logger.info(f"Last system rebooted at : {last_system_reboot_time} ")
        logger.info(f"Last time sync happened: {time_sync[0]}")
        if last_system_reboot_time.hour in time_sync_at_reboot:
            logger.info("Time Sync at Reboot is working.")
        else:
            logger.info("Time Sync at Reboot is Not working.")
    elif state == "six_hour":
        logger.info("Checking time sync for every six hours")
        six_hrs_time_sync = filter_time_stamp_for_six_hours(time_sync)
        logger.info(f"Last time Sync Happened: {six_hrs_time_sync[0]} hrs")
        if len(six_hrs_time_sync) > 0:
            if six_hrs_time_sync[0].hour % 6 == 0:
                logger.info("Time Sync for every six hours is working.")
        else:
            logger.info("Time Sync for every six hours is not working.")
    elif state == "midnight":
        logger.info("Checking time sync at midnight.")
        time_sync_at_midnight = filter_midnight_time_stamps(time_sync)
        zc_utc_time = (get_zc_time()[1] - timedelta(hours=1)).hour
        logger.info(f"Last time Sync Happened: {time_sync_at_midnight[0]} hrs")
        if len(time_sync_at_midnight) > 0:
            if int(time_sync_at_midnight[0].strftime("%H")) == zc_utc_time:
                logger.info("Time sync at midnight is working.")
        else:
            logger.info("Time sync at midnight is not working.")
    else:
        logger.debug("Default state.")



def time_sync_cron_check():
    """
    Main method to check cron for time_sync
    :param url: IP address of ZC: str
    :param port: Post number to connect the ZC through ssh: int
    :param host_name: ZC Username to login: str
    :param host_password: ZC password to login: str
    :return: None
    """
    logger.info("************* CHECK TIME SYNC CRONJOB STARTED***************")
    while True:
        state = generate_query_time()
        # logger.info(f"Current state: {state}")
        if state != 'default':
            try:
                logger.info(f"Checking time sync at {state}")
                time_sync = last_run_status("time_sync")
                check_cron_based_on_state(state, time_sync)
            except Exception as e:
                logger.error(str(e))
        sleep(time_to_wait)


if __name__ == "__main__":
    time_sync_cron_check()
