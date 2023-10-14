from cron_check_utils import *


def check_shutdown_status():
    logger.info("Checking shutdown status cron at reboot.")
    shutdown_log = last_run_status("shutdown")
    shutdown_time = list(set(_.hour for _ in shutdown_log))
    cron_reboot = last_reboot_time_in_cron()
    logger.info(f"Last system Rebooted at {cron_reboot}")
    if cron_reboot.hour in shutdown_time:
        logger.info("Cron for check shutdown is working.")
    else:
        logger.info("Cron for check shutdown is not working.")


def shutdown_status_cron_check():
    logger.info("************* CHECK SHUTDOWN CRONJOB STARTED**************")
    while True:
        zc_reboot = check_for_zc_reboot()
        logger.info(f"Last ZC rebooted at {zc_reboot} mins.")
        if zc_reboot < 30:
            try:
                logger.info("ZC Reboot detected.")
                check_shutdown_status()
            except Exception as e:
                logger.error(str(e))
        sleep(time_to_wait)



if __name__ == "__main__":
    shutdown_status_cron_check()
