from cron_check_utils import *
from random import randint


def create_tmp_file_on_random_day():
    SSH.connect(url, port, host_name, host_password)
    _date = randint(1, 15)
    zc_date = get_zc_time()[0].date
    if zc_date == _date:
        SSH.exec_command('docker exec -t web bash -c "fallocate -l 1G /tmp/test"')
        logger.info("Test 1G file created.")
        SSH.close()
    else:
        logger.info("Test 1G file not created.")
        SSH.close()


def last_old_temp_cron_run():
    tmp_clean = last_run_status("tmp_clean")
    midnight_cron_time = last_midnight_time_in_cron()
    if midnight_cron_time.hour in tmp_clean:
        return True
    else:
        return False


def check_for_test_file_in_tmp_folder():
    SSH.connect(url, port, host_name, host_password)
    stdin, stdout, stderr = SSH.exec_command('docker exec -t web bash -c "ls /tmp"')
    output = stdout.readlines()
    output = [_.strip() for _ in output]
    SSH.close()
    if "test" in output:
        return True
    else:
        return False



def check_clear_old_tmp_cron():
    logger.info("************* CHECK TMP CLEANUP CRONJOB STARTED**************")

    while True:
        tmp_file = check_for_test_file_in_tmp_folder()
        try:
            if tmp_file:
                while True:
                    zc_time = get_zc_time()[0]
                    if int(zc_time.hour) == 1:
                        _tmp_file = check_for_test_file_in_tmp_folder()
                        if not _tmp_file:
                            logger.info("Test 1G file not found. So Tmp cleanup success.")
                        else:
                            logger.info("Test 1G file found. So TMP cleanup failed.")
                    else:
                        logger.info("1G tmp file found.")
                        logger.info("Waiting for midnight")
                    sleep(time_to_wait)
            else:
                logger.info("Test 1G file not found.")
                create_tmp_file_on_random_day()
                _tmp = check_for_test_file_in_tmp_folder()
                if _tmp:
                    wait_time = 24 - get_zc_time()[0].hour
                    sleep((wait_time - 1)*3600)
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
        sleep(time_to_wait)





if __name__ == "__main__":
    check_clear_old_tmp_cron()
