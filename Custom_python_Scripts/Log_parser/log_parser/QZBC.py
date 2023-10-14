from main import *

def get_QZBC_sent(log_dir, log_file):
    for _ in log_file:
        with open(f"{log_dir}/{_}", 'r') as data:
            for line in data.readlines():
                if ("originated from web-app" in line) and ("QZBC" in line):
                    _dictionary = get_json(line)
                    QZBC_sent.append(_dictionary)

def get_QZBC_received(log_dir, log_file):
    for _ in log_file:
        with open(f"{log_dir}/{_}", "r") as data:
            for line in data.readlines():
                if ("Received" in line) and ("QZBC" in line):
                    _dictionary = get_json(line)
                    QZBC_received.append(_dictionary)

def get_DACK(log_dir, log_file):
    for _ in log_file:
        with open(f"{log_dir}/{_}", "r") as data:
            for line in data.readlines():
                if ("Received" in line) and ("DACK" in line):
                    _dictionary = get_json(line)
                    DACK.append(_dictionary)

def drop_duplicated(list_data):
    df = pd.DataFrame(list_data)
    return df.drop_duplicates(subset=["DID"])


if __name__ == "__main__":
    for i,_ in enumerate(LOGSDIRs):
        QZBC_sent = []
        QZBC_received = []
        DACK = []
        excel_file = "QZBC.xlsx"
        log_files_loc = f'{WORK_DIR}/{LOGSDIRs[i]}'
        logs = os.listdir(log_files_loc)
        get_QZBC_sent(log_files_loc, logs)
        get_QZBC_received(log_files_loc, logs)
        get_DACK(log_files_loc, logs)
        excelWriter(excel_file, ["QZBC_sent", "QZBC_received", "DACK"], [QZBC_sent, QZBC_received, DACK])