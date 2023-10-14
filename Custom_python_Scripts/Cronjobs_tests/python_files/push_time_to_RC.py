from cron_check_utils import *


def check_rc_time_push():
    misc = last_run_status("rc_time_push")
    misc = [_.hour for _ in misc]
    xbee_log = check_xbee_backend_log("HRTS")
    logger.info("Checking rc timepush cron at midnight.")
    zc_utc_time = get_zc_time()[1]
    epoch_time = zc_utc_time.strftime("%s")
    if zc_utc_time.hour in misc:
        if xbee_log["TS"] == epoch_time:
            logger.info("Push time to RC cron is working.")
        else:
            logger.info("Push time to RC cron is not working.")
    else:
        logger.info("Wating for midnight.")


def push_time_to_RC():
    logger.info("************* CHECK RC TIME PUSH CRONJOB STARTED**************")
    while True:
        zc_state = generate_query_time()
        if zc_state == "midnight":
            try:
                logger.info("checking for rc time push cron.")
                check_rc_time_push()
            except Exception as e:
                logger.error(str(e))
                logger.error(traceback.format_exc())
        sleep(time_to_wait)


if __name__ == "__main__":
    push_time_to_RC()
