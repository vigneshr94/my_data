## Periodic requests plotter

## Pre-requisites
    - Python 3.10
    - venv -- Python virtual environment creator

## Create Virtual Environment and install dependencies
    - Open terminal in the share folder or in the script folder
    - And run the below command to create environment
            `python3 -m venv env`
    - Once environment is created run the below command
            `source env/bin/activate`
    - Once the environment is activated. Now install the depencencies with following command
            `pip3 install -r requirements.txt`
    - After installing the dependencies to run the script use the below command
            `python3 main.py`

## Post execution of the script
    This script will create two excel files for each array of logs in the same directory
        for example if you give two array's xbee_backend the script gives 4 excel file 2 for each
    This script also plot the pivot chart which also stored in the same directory in png format

### To reduce the run time of the script please reduce the number of log files by keeping only the required data

### The log files should be kept under "logs_dir" in the same directory and each array should be in each folder