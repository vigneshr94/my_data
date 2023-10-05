from main import *


def get_DACK(log_dir, log_file):
    for _ in log_file:
        with open(f"{log_dir}/{_}", "r") as data:
            for line in data.readlines():
                if ("Received" in line) and ("DACK" in line):
                    _dictionary = get_json(line)
                    DACK.append(_dictionary)



if __name__ == "__main__":
    for i,_ in enumerate(LOGSDIRs):
        DACK = []
        excel_file = "DACK.xlsx"
        log_files_loc = f'{WORK_DIR}/{LOGSDIRs[i]}'
        logs = os.listdir(log_files_loc)
        get_DACK(log_files_loc, logs)
        excelWriter(excel_file, ["DACK"], [DACK])