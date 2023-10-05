from main import *


def get_wind_sensor_data(log_dir, log_file):
    for _ in log_file:
        with open(f"{log_dir}/{_}", "r") as data:
            for line in data.readlines():
                if ("originated from wind-sensor" in line) or ("originated from backend-zcEngine" in line):
                    if ("WIND" in line) or ("AUTO" in line):
                        dictionary = get_json(line)
                        dictionary['source'] = line.split("}")[1].strip()
                        wind_sensor.append(dictionary)

def get_dst2_data(log_dir, log_file):
    for _ in log_file:
        with open(f"{log_dir}/{_}", "r") as data:
            for line in data.readlines():
                if "DSTU" in line:
                    try:
                        DSTU.append(get_json(line))
                    except:
                        print(f"Invalid Line...{line}")
                        print(f"Log file the line found: {_}")

def get_dalt_data(log_dir, log_file):
    for _ in log_file:
        with open(f"{log_dir}/{_}", "r") as data:
            for line in data.readlines():
                if ("DALT" in line):
                    try:
                        dalt.append(get_json(line))
                    except:
                        print(f"Invalid Line...{line}")
                        print(f"Log file the line found: {_}")

def divide_wind_cmd(wind_data):
    for _ in wind_data:
        if _["MODE"] == "WIND":
            wind_cmd.append(_)
        elif _["MODE"] == "AUTO":
            auto_cmd.append(_)

def filter_dalt(dalt, wind_start, wind_end, auto_start, auto_end):
    for dalt in dalt:
        if (wind_start['TS'] >= dalt["TS"]) or (dalt["TS"] <= wind_end['TS']):
            filtered_dalt_wind.append(dalt)
        elif (auto_start['TS'] >= dalt["TS"]) or (dalt["TS"] <= auto_end['TS']):
            filtered_dalt_auto.append(dalt)



if __name__ == "__main__":
    for i,_ in enumerate(LOGSDIRs):
        wind_sensor = []
        wind_cmd = []
        auto_cmd = []
        dalt =[]
        filtered_dalt_wind = []
        filtered_dalt_auto = []
        excel_file = f"wind_log_parser_{LOGSDIRs[i]}.xlsx"
        log_files_loc = f"{WORK_DIR}/{LOGSDIRs[i]}"
        logs = os.listdir(log_files_loc)
        get_wind_sensor_data(log_files_loc,logs)
        get_dst2_data(log_files_loc, logs)
        get_dalt_data(log_files_loc, logs)
        divide_wind_cmd(wind_sensor)
        excelWriter(excel_file ,["wind_cmd", "auto_cmd", "dalt"], [wind_cmd, auto_cmd, dalt])