# The code is importing the necessary libraries for data manipulation and file handling in Python.
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import re
import json

# The code is initializing variables `WORK_DIR`, `LOGSDIRs`, `HST2`, `DST2`, and `DSTU`.
WORK_DIR = os.getcwd() + "/logs_dir"
try:
    os.remove(f"{WORK_DIR}/.DS_Store")
except:
    pass
LOGSDIRs = os.listdir(WORK_DIR)
print(LOGSDIRs)


def get_json(to_match):
    """
    The function `get_json` extracts a JSON object from a string and returns it, or returns an empty
    JSON object if no match is found.

    :param to_match: The `to_match` parameter is a string that contains some text. The function is
    designed to search for a JSON object within this text and return it as a Python dictionary. If no
    JSON object is found, an empty dictionary is returned
    :return: The function `get_json` returns a JSON object. If a valid JSON object is found within the
    `to_match` string, it is returned as a Python dictionary using the `json.loads()` function. If an
    invalid JSON object is found, an error message is printed and an empty dictionary is returned.
    """
    match = re.search("{.+?}", to_match)
    try:
        return json.loads(match.group())
    except:
        # print(f"Invalid line found: {match}")
        return json.loads(str({}))


def get_periodic_request_data(log_dir, log_file):
    """
    The function reads log files from a specified directory and extracts data based on specific
    keywords.

    :param log_dir: The `log_dir` parameter is the directory where the log files are located. It is a
    string that specifies the path to the directory
    :param log_file: The `log_file` parameter is the name of the log file that contains the data you
    want to process
    """
    for _ in log_file:
        with open(f"{log_dir}/{_}", "r") as data:
            for line in data.readlines():
                if "HST2" in line:
                    HST2.append(get_json(line))
                elif "DST2" in line:
                    DST2.append(get_json(line))
                elif "DSTU" in line:
                    DSTU.append(get_json(line))
                elif "HST3" in line:
                    HST3.append(get_json(line))
                elif "DST3" in line:
                    line = line.replace("\n", "") + '"}'
                    DST3.append(get_json(line))
                elif "DALT" in line:
                    DALT.append(get_json(line))


def get_dataframe(_data):
    """
    The function takes in a dictionary of data, converts the "TS" column to datetime format, and returns
    a pandas DataFrame.

    :param _data: The parameter `_data` is a variable that represents the data that you want to convert
    into a pandas DataFrame. It can be any data structure that is compatible with creating a DataFrame,
    such as a list of dictionaries or a dictionary of lists
    :return: a pandas DataFrame object.
    """
    data_frame = pd.DataFrame(_data)
    try:
        data_frame["TS"] = pd.to_datetime(data_frame["TS"], unit="s")
        return data_frame
    except:
        pass


def prepare_to_plot(sheet_name, __data):
    """
    The function "prepare_to_plot" takes a sheet name and data as input, and returns a modified
    dataframe based on the sheet name.

    :param sheet_name: The `sheet_name` parameter is a string that specifies the name of the sheet in a
    spreadsheet. It is used to determine which data processing steps to apply
    :param __data: The parameter "__data" is likely a variable that contains the data needed for
    plotting. It is passed to the function "get_dataframe" to convert it into a pandas DataFrame. The
    resulting DataFrame is then processed based on the value of the "sheet_name" parameter
    :return: a dataframe after performing certain operations based on the value of the sheet_name
    parameter.
    """
    try:
        if sheet_name == "HST3" or "HST2":
            to_dataframe = get_dataframe(__data).drop("CID", axis=1)
            return to_dataframe
        elif sheet_name == "DST3" or "DST3":
            to_dataframe = get_dataframe(__data).drop(columns=["CID", "VALUES"])
            return to_dataframe
        elif sheet_name == "DSTU":
            to_dataframe = get_dataframe(__data).drop(
                columns=["MODE", "PANGLE", "CANGLE", "BTEMP", "BATV"]
            )
            return to_dataframe
    except:
        pass


def prepareExcel(writer, sheet_name, Data):
    """
    The function prepares and writes data to an Excel file using a specified writer, sheet name, and
    data.

    :param writer: The "writer" parameter is an object that represents the Excel file that you want to
    write to. It could be an instance of the `pandas.ExcelWriter` class
    :param sheet_name: The sheet_name parameter is the name of the sheet in the Excel file where the
    data will be written
    :param Data: The "Data" parameter is the input data that you want to write to an Excel file. It can
    be in any format that can be converted to a pandas DataFrame
    """
    try:
        to_dataframe = get_dataframe(Data).drop("CID", axis=1)
    except:
        to_dataframe = get_dataframe(Data)
    try:
        to_dataframe.to_excel(writer, sheet_name=sheet_name, index=False)
    except:
        pass


def excelWriter(file_name, sheet_names, data_s):
    """
    The function `excelWriter` takes in a file name, sheet names, and data, and writes the data to an
    Excel file using the openpyxl engine.

    :param file_name: The name of the Excel file you want to create or modify
    :param sheet_names: The parameter "sheet_names" is a list of strings that represents the names of
    the sheets in the Excel file. Each string in the list corresponds to a sheet name
    :param data_s: The parameter `data_s` is a list of dataframes. Each dataframe represents the data
    that will be written to a separate sheet in the Excel file. The order of the dataframes in the list
    corresponds to the order of the sheet names in the `sheet_names` parameter
    """
    writer = pd.ExcelWriter(file_name, engine="openpyxl")
    for i, _ in enumerate(sheet_names):
        prepareExcel(writer, sheet_names[i], data_s[i])
    writer.close()


def sorting_dataframes(dataframe, df_type):
    """
    The function `sorting_dataframes` takes a dataframe and a dataframe type as input, and returns the
    dataframe with its columns sorted based on the dataframe type.

    :param dataframe: The `dataframe` parameter is a pandas DataFrame object that contains the data you
    want to sort
    :param df_type: The `df_type` parameter is a string that specifies the type of dataframe. It can
    have two possible values: "HST2" or "DST2"
    :return: a modified dataframe with the columns rearranged based on the given df_type.
    """
    cols = dataframe.columns.to_list()
    if df_type == "HST2":
        cols = ["TS"] + cols[0:2]
    elif df_type == "DST2":
        cols = cols[1:] + ["TS"]
    return dataframe[cols]


def filter_dataframe_by_timeStamp(cmd, dataframe1, dataframe2):
    """
    The function `filter_dataframe_by_timeStamp` takes two dataframes as input and returns a new
    dataframe that contains information about the count of commands sent and received at each timestamp.

    :param dataframe1: dataframe1 is a pandas DataFrame containing data related to HST2 commands. It has
    columns such as 'TS' (timestamp) and 'DID' (device ID)
    :param dataframe2: The parameter `dataframe2` is a pandas DataFrame containing data related to DST2
    commands
    :return: a pandas DataFrame that contains information about the count of commands sent and received
    at different timestamps. It also includes the commands missed count, which is the difference between
    the count of commands sent and received.
    """
    count_df = pd.DataFrame()
    list_count_df = []
    if cmd == "HST3":
        for i, _ in enumerate(dataframe1["TS"]):
            sample_dic = {}
            sample_dic["TS"] = dataframe1["TS"][i]
            hst2_filtered = dataframe1[dataframe1["TS"] == dataframe1["TS"][i]]
            sample_dic["HST3_SENT_DID"] = hst2_filtered["DID"].values
            sample_dic["HST3 Command Count"] = hst2_filtered.shape[0]
            dst2_filetered = dataframe2[dataframe2["TS"] == dataframe1["TS"][i]]
            sample_dic["DST3_RECEIVED_DID"] = dst2_filetered["DID"].values
            sample_dic["DST3 Command Count"] = dst2_filetered.shape[0]
            list_count_df.append(sample_dic)
        count_df = pd.DataFrame(list_count_df)
        count_df = count_df.drop_duplicates(subset="TS")
        count_df["Commands missed count"] = (
            count_df["HST3 Command Count"] - count_df["DST3 Command Count"]
        )
    elif cmd == "HST2":
        for i, _ in enumerate(dataframe1["TS"]):
            sample_dic = {}
            sample_dic["TS"] = dataframe1["TS"][i]
            hst2_filtered = dataframe1[dataframe1["TS"] == dataframe1["TS"][i]]
            sample_dic["HST2_SENT_DID"] = hst2_filtered["DID"].values
            sample_dic["HST2 Command Count"] = hst2_filtered.shape[0]
            dst2_filetered = dataframe2[dataframe2["TS"] == dataframe1["TS"][i]]
            sample_dic["DST2_RECEIVED_DID"] = dst2_filetered["DID"].values
            sample_dic["DST2 Command Count"] = dst2_filetered.shape[0]
            list_count_df.append(sample_dic)
            count_df = pd.DataFrame(list_count_df)
            count_df = count_df.drop_duplicates(subset="TS")
            count_df["Commands missed count"] = (
                count_df["HST2 Command Count"] - count_df["DST2 Command Count"]
            )
    return count_df


def prepare_plot(cmd, plot_name, _dataframe):
    if cmd == "HST3":
        value = ["HST3 Command Count", "DST3 Command Count"]
        y_label = "HST3 Sent and DST3 Received Count"
        _title = "HST3 vs DST3"
    elif cmd == "HST2":
        value = (["HST2 Command Count", "DST2 Command Count"],)
        y_label = "HST2 Sent and DST2 Received Count"
        _title = "HST2 vs DST2"
    _dataframe["TS"] = _dataframe["TS"].dt.date
    pivot_table = _dataframe.pivot_table(values=value, index="TS", aggfunc=sum)
    fig = plt.gcf()
    fig.set_size_inches(100, 5)
    ax = pivot_table.plot(kind="bar", width=0.8, figsize=(15, 15))
    ax.legend(loc="lower left")
    ax.set_yticks([])
    ax.set_yticklabels([])
    plt.xlabel("Date")
    plt.ylabel(y_label)
    plt.title(_title)
    for cont in ax.containers:
        ax.bar_label(
            cont,
            fmt="%.0f",
            label_type="edge",
        )
    plt.savefig(plot_name)


def for_hst2(data_list):
    excelWriter(excel_file, ["HST2", "DST2", "DSTU", "DALT"], [HST2, DST2, DSTU, DALT])
    hst2 = prepare_to_plot("HST2", get_dataframe(HST2))
    dst2 = prepare_to_plot("DST2", get_dataframe(DST2))
    final_Df = filter_dataframe_by_timeStamp("HST2", hst2, dst2)
    plot_name = f"HST2_vs_DST2_of_{LOGSDIRs[i]}.png"
    prepare_plot(plot_name, final_Df)


def for_hst3(data_list):
    excelWriter(excel_file, ["HST3", "DST3", "DSTU", "DALT"], [HST3, DST3, DSTU, DALT])
    hst3 = prepare_to_plot("HST3", get_dataframe(HST3))
    dst3 = prepare_to_plot("DST3", get_dataframe(DST3))
    final_Df = filter_dataframe_by_timeStamp("HST3", hst3, dst3)
    plot_name = f"HST3_vs_DST3_of_{LOGSDIRs[i]}.png"
    prepare_plot(plot_name, final_Df)


# The code block `if __name__ == "__main__":` is a common Python idiom that allows a script to be
# executed as a standalone program or imported as a module.
if __name__ == "__main__":
    for i, _ in enumerate(LOGSDIRs):
        HST2 = []
        DST2 = []
        DSTU = []
        HST3 = []
        DST3 = []
        DALT = []
        hst2 = None
        dst2 = None
        dst3 = None
        hst3 = None
        final_Df = None
        log_files_loc = f"{WORK_DIR}/{LOGSDIRs[i]}"
        logs = os.listdir(log_files_loc)
        excel_file = f"periodic_request_{LOGSDIRs[i]}.xlsx"
        excel_file_plots = f"periodic_request_plot_{LOGSDIRs[i]}.xlsx"
        dstu_plot = f"dstu_{LOGSDIRs[i]}"
        dalt_plot = f"dalt_{LOGSDIRs[i]}"
        get_periodic_request_data(log_files_loc, logs)
        # call the requried function here
