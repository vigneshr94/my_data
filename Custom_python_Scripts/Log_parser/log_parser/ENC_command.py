from main import *

def get_HZBC_data(log_dir, log_file):
    for _ in log_file:
        with open(f"{log_dir}/{_}", "r") as data:
            for line in data.readlines():
                if ("originated from web-app" in line):
                    if ("HZBC" in line):
                        dictionary = get_json(line)
                        HZBC.append(dictionary)

def get_DACK_data(log_dir, log_file, HZBC_data):
    for _ in log_file:
        with open(f"{log_dir}/{_}", "r") as data:
            for line in data.readlines():
                if ("DACK" in line):
                    for i in HZBC_data:
                        if i['DID'] in line:
                            dictionary = get_json(line)
                            DACK.append(dictionary)
                            
def filter_DACK(DACKs, HZBC_start, HZBC_end):
    for dack in DACKs:
        if (HZBC_start['TS'] <= dack['TS']) or (dack["TS"] >= HZBC_end['TS']): 
            filtered_DACK.append(dack)


def to_dataframe(list_data):
    df = pd.DataFrame(list_data)
    return df

def group_by_did(df, to_match):
    grouped = df[df["DID"] == to_match]
    return grouped

if __name__ == "__main__":
    for i, _ in enumerate(LOGSDIRs):
        HZBC = []
        DACK = []
        filtered_DACK = []
        did = []
        excel_file = f"ENC_DATA.xlsx"
        log_files_loc = f'{WORK_DIR}/{LOGSDIRs[i]}'
        logs = os.listdir(log_files_loc)
        get_HZBC_data(log_files_loc, logs)
        print(HZBC[0:10])
        print(len(HZBC))
        get_DACK_data(log_files_loc, logs, HZBC)
        print(DACK[0:10])
        print(len(DACK))
        filter_DACK(DACK, HZBC[0], HZBC[-1])
        print(filtered_DACK[10])
        print(len(filtered_DACK))
        excelWriter(excel_file, ["HZBC", "DACK", "filtered_DACK"], [HZBC, DACK, filtered_DACK])