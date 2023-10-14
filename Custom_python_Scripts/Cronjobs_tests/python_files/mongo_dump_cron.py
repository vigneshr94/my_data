from cron_check_utils import *

dump_path = "/home/torizon/voyager/verdin/vzc/install/app_config/dump/voyagerDB"


def get_last_modified_mongo_dump():
    SSH.connect(url, port, host_name, host_password)
    stdin, stdout, stderr = SSH.exec_command(f'date -r {dump_path} -u +"%Y-%m-%d %H:%M:%S"')
    output = stdout.readline()
    SSH.close()
    output = datetime.strptime(output.strip(), "%Y-%m-%d %H:%M:%S")
    return output


def check_mongo_dump_cron():
    logger.info("************* CHECK MONGO DUMP CRONJOB STARTED**************")
    while True:
        state = generate_query_time()
        try:
            if state == "midnight":
                last_dump_happened = get_last_modified_mongo_dump()
                logger.info(f"Last mongo DB created: {last_dump_happened}")
                zc_utc_time = get_zc_time()[1] - timedelta(hours=1)
                if last_dump_happened.hour == zc_utc_time.hour:
                    logger.info("Mongo DB dump created at midnight.")
                else:
                    logger.info("Mongo DB dump not created at midnight.")
            else:
                logger.info("Waiting for midnight.")
        except Exception as e:
            logger.error(str(e))
        sleep(time_to_wait)




if __name__ == "__main__":
    check_mongo_dump_cron()
