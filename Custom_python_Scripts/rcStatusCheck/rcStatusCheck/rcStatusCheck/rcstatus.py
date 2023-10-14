import requests
import pandas as pd
import csv
from datetime import datetime
import time
from collections.abc import MutableMapping
#from pytz import timezone, utc
#from timezonefinder import TimezoneFinder

def flatten(d):
    items = []
    for k, v in d.items():
        if isinstance(v, MutableMapping):
            items.extend(flatten(v).items())
        else:
            items.append((k, v))
    return dict(items)

def download_status_data(data):
	urls = ['http://' + data['IP Address'] + ':5000/rover/get','http://' + data['IP Address'] + '/flask/rover/get', 'http://' + data['IP Address'] + '/flask/rover/get/no_time_diff']
	result = {}
	for url in urls:
		if result=={} or ('success' in result and result['success']==False):
			try:
				r = requests.get(url,timeout=5)
				result['success'] = True
				result['api'] = '5000' if url==urls[0] else 'flask'
				details = []
				for row in r.json()['message']:
					row['alertMap']['Offline'] = False if row['online'] else True
					del row['online']
					row['Site'] = data['Site']
					row['Zone'] = data['Array']
					row['IP Address'] = data['IP Address']
					details.append(flatten(row))
				result['details'] = details
			except Exception as e:
				result['success'] = False
				result['api'] = None
				result['details'] = e
	return result

def get_zc_version(data,api):
	urls = ['http://' + data['IP Address'] + ':5000/version/get','http://' + data['IP Address'] + '/flask/version/get']
	if api=='flask':
		urls.pop(0)
	result = {}
	for url in urls:
		if result=={} or ('success' in result and result['success']==False):
			try:
				r = requests.get(url,timeout=5)
				result['success'] = True
				result['version'] = r.json()['message']['sVersion']
			except Exception as e:
				result['success'] = False
				result['version'] = None
	return result

def get_ntp_status(data,api):
	urls = ['http://' + data['IP Address'] + ':5000/ntp/status/get','http://' + data['IP Address'] + '/flask/ntp/status/get']
	if api=='flask':
		urls.pop(0)
	result = {}
	for url in urls:
		if result=={} or ('success' in result and result['success']==False):
			try:
				r = requests.get(url,timeout=5)
				result['success'] = True
				result['ntp_last_attempt'] = r.json()['message']['lastAttempt']
				result['ntp_last_sync'] = r.json()['message']['lastSuccessfulSync']
				result['ntp_sync_in_last_24hrs'] = True if int(time.time())-result['ntp_last_sync'] < 24*60*60 else False
				result['ntp_address'] = r.json()['message']['serverAddress']
			except Exception as e:
				result['success'] = False
				result['ntp_last_attempt'] = None
				result['ntp_last_sync'] = None
				result['ntp_sync_in_last_24hrs'] = None
				result['ntp_address'] = None
	return result

def get_zc_name(data,api):
	urls = ['http://' + data['IP Address'] + ':5000/zoneID/get','http://' + data['IP Address'] + '/flask/zoneID/get']
	if api=='flask':
		urls.pop(0)
	result = {}
	for url in urls:
		if result=={} or ('success' in result and result['success']==False):
			try:
				r = requests.get(url,timeout=5)
				result['success'] = True
				result['zone_name'] = r.json()['message']
			except Exception as e:
				result['success'] = False
				result['zone_name'] = None
	return result

def get_utc_offset(lat,long):
	today = datetime.now()
	tf = TimezoneFinder()
	tz_target = timezone(tf.certain_timezone_at(lng=long, lat=lat))
	if tz_target is not None:
		today_target = tz_target.localize(today)
		today_utc = utc.localize(today)
		return (today_utc - today_target).total_seconds() / (60*60)

def get_plant_data(data,api):
	urls = ['http://' + data['IP Address'] + ':5000/plantData/get','http://' + data['IP Address'] + '/flask/plantData/get']
	if api=='flask':
		urls.pop(0)
	result = {}
	for url in urls:
		if result=={} or ('success' in result and result['success']==False):
			try:
				r = requests.get(url,timeout=5)
				result['success'] = True
				result['site_name'] = r.json()['message']['name']
				result['lat'] = r.json()['message']['latitude']
				result['lon'] = r.json()['message']['longitude']
				#result['utc_offset'] = get_utc_offset(result['lat'],result['lon'])
			except Exception as e:
				result['success'] = False
				result['site_name'] = None
				result['lat'] = None
				result['lon'] = None
				#result['utc_offset'] = None
	return result

def get_zc_alerts(data,api):
	urls = ['http://' + data['IP Address'] + ':5000/alerts/zone/getLatest','http://' + data['IP Address'] + '/flask/alerts/zone/getLatest']
	if api=='flask':
		urls.pop(0)
	result = {}
	for url in urls:
		if result=={} or ('success' in result and result['success']==False):
			try:
				r = requests.get(url,timeout=5)
				result['success'] = True
				result['details'] = r.json()['message']
			except Exception as e:
				result['success'] = False
				result['details'] = {}
	return result

def get_zc_data(data,api):
	result = (get_zc_alerts(data,api))
	plant_data = get_plant_data(data,api)
	ntp_status = get_ntp_status(data,api)
	result['details']['site_name'] = [plant_data['site_name']]
	result['details']['lat'] = [plant_data['lat']]
	result['details']['lon'] = [plant_data['lon']]
	#result['details']['utc_offset'] = [plant_data['utc_offset']]
	result['details']['zone_name'] = [get_zc_name(data,api)['zone_name']]
	result['details']['version'] = [get_zc_version(data,api)['version']]
	result['details']['ntp_last_attempt'] = [ntp_status['ntp_last_attempt']]
	result['details']['ntp_last_sync'] = [ntp_status['ntp_last_sync']]
	result['details']['ntp_sync_in_last_24hrs'] = [ntp_status['ntp_sync_in_last_24hrs']]
	result['details']['ntp_address'] = [ntp_status['ntp_address']]
	result['details']['Site'] = data['Site']
	result['details']['Zone'] = data['Array']
	result['details']['IP Address'] = data['IP Address']
	return result

def export_csvs(rcDF,zcDF,progressDF):
	# rearrange some columns
	zc_cols_to_move = ['Site','Zone']
	zcDF = zcDF[zc_cols_to_move + [col for col in zcDF.columns if col not in zc_cols_to_move ]]
	rc_cols_to_move = ['Site','Zone','rowNumber','deviceID']
	rcDF = rcDF[rc_cols_to_move + [col for col in rcDF.columns if col not in rc_cols_to_move ]]
	rcDF.to_csv('rows.csv',index=False)
	zcDF.to_csv('zones.csv',index=False)
	progressDF.to_csv('progress.csv',index=False)

def create_df_of_rc_data(ipArray,rcDF=None,zcDF=None,progressDF=None,exportCSVs=False):
	offlineZCDF = pd.DataFrame()
	i = 1
	now = datetime.now()
	dt = now.strftime("%d/%m/%Y %H:%M:%S")
	log = 'Script started at ' + dt + '\n'
	for item in ipArray:
		#msg = f'Contacting {item["Site"]} Array {item["Array"]}...'
		msg = "Contacting " + item['Site'] + " Array " + item['Array'] + "..."
		log += msg
		print(msg, end='')
		timestamp = int(datetime.now().timestamp())
		rc_data = download_status_data(item)
		if rc_data['success']:
			print('success')
			log += 'success\n'
			# update RC data
			newRCData = pd.DataFrame.from_dict(rc_data['details'])
			if 'IP Address' in rcDF.columns and rcDF['IP Address'].str.contains(item['IP Address']).any():
				rcDF.loc[rcDF['IP Address'].isin(newRCData['IP Address'])] = newRCData
			else:
				rcDF = pd.concat([rcDF,newRCData])
			# update ZC data
			zc_data = get_zc_data(item,rc_data['api'])
			newZCData = pd.DataFrame.from_dict(zc_data['details'])
			if 'IP Address' in zcDF.columns and zcDF['IP Address'].str.contains(item['IP Address']).any():
				zcDF.loc[zcDF['IP Address'].isin(newZCData['IP Address'])] = newZCData
			else:
				zcDF = pd.concat([zcDF,newZCData])
			if exportCSVs:
				# update progress data
				newProgressData = pd.DataFrame(data={'Site':item['Site'],'Array':item['Array'],'IP Address':item['IP Address'],'Status':'success','Last Updated':timestamp},index=[0])
				progressDF = update_progress_df(progressDF,newProgressData,item['IP Address'])
				export_csvs(rcDF,zcDF,progressDF)
		else:
			print('error')
			log += 'error\n'
			if exportCSVs:
				newProgressData = pd.DataFrame(data={'Site':item['Site'],'Array':item['Array'],'IP Address':item['IP Address'],'Status':'error','Last Updated':timestamp},index=[0])
				progressDF = update_progress_df(progressDF,newProgressData,item['IP Address'])
			offlineZCDF = pd.concat([offlineZCDF,pd.DataFrame.from_dict({k: [v] for k, v in item.items()})])
		i += 1
	now = datetime.now()
	dt = now.strftime("%d/%m/%Y %H:%M:%S")
	log += 'Script ended at ' + dt
	return {'RCStatus': rcDF, 'ZCStatus': zcDF, 'OfflineZCs': offlineZCDF, 'log': log, 'progress': progressDF}

def update_progress_df(progressDF,newProgressData,ipAddress):
	if 'IP Address' in progressDF.columns and progressDF['IP Address'].str.contains(ipAddress).any():
		progressDF.loc[progressDF['IP Address'].isin(newProgressData['IP Address'])] = newProgressData
	else:
		progressDF = pd.concat([progressDF,newProgressData])
	return progressDF

def add_issue_filters(result):
	issues = {
		'MNB':'Minimum_battery_voltage_Fault_02',
		'MSF':'Motor_stall_Fault_06',
		'OFF':'Offline',
		'OVC':'Over_current_Fault_01',
		'OTA':'OTA_Fault_11',
		'RTC':'RTC_Fault_13',
		'ZGB':'Zigbee_Fault_07',
		'INC':'Inclinometer_Fault_09',
		'EPR':'EEPROM_Fault_12',
		'COM':'Communication_Fault_08',
		'BRD':'Board_temperature_exceed_Fault_04',
		'MOF':'Mechanical_Overload_Fault_18',
		'SCF':'Set_Command_Flag_34',
		'LBS':'Low_Battery_Stow_17',
		'LSF':'Locking_system_Fault_15',
		'MOV':'Mechanical_Overload_Occurred_35',
		'INC':'Inclinometer_Fault_09',
		'LTM':'Locked_track_move_Fault_16',
		'MB':'Maintainence_block_33',
		'SPI':'SPI_Flash_Memory_Fault_10'
	}
	for key in issues:
		if issues[key] in result['RCStatus'].columns:
			result[key] = result['RCStatus'][result['RCStatus'][issues[key]]==True]

	return result

def run_script(inputFile,outputFile,rcDF=None,zcDF=None,progressDF=None,exportCSVs=False):
	with open(inputFile) as f:
		inputData = [{k: v for k, v in row.items()} for row in csv.DictReader(f, skipinitialspace=True)]
	result = create_df_of_rc_data(inputData,rcDF,zcDF,progressDF,exportCSVs=exportCSVs)
	rcDF = result['RCStatus'].copy(deep=True)
	zcDF = result['ZCStatus'].copy(deep=True)
	if exportCSVs:
		progressDF = result['progress'].copy(deep=True)
	# rearrange some columns
	zc_cols_to_move = ['Site','Zone','IP Address']
	result['ZCStatus'] = result['ZCStatus'][zc_cols_to_move + [col for col in result['ZCStatus'].columns if col not in zc_cols_to_move ]]
	rc_cols_to_move = ['Site','Zone','IP Address','rowNumber','deviceID']
	result['RCStatus'] = result['RCStatus'][rc_cols_to_move + [col for col in result['RCStatus'].columns if col not in rc_cols_to_move ]]
	# add filtered issue dataframes to the results
	result = add_issue_filters(result)
	outputLog = open('output.log','w')
	outputLog.write(result['log'])
	outputLog.close()

	writer = pd.ExcelWriter(outputFile, engine='openpyxl')
	for key in result:
		if key not in ['log','progress'] and not result[key].empty:
			result[key].to_excel(writer,sheet_name=key,index=False)
	writer.save()

	return rcDF,zcDF,progressDF

runForever = False
rcDF = pd.DataFrame()
zcDF = pd.DataFrame()
if runForever:
	progressDF = pd.DataFrame()
	while True:
		rcDF,zcDF,progressDF = run_script(inputFile='input.csv', outputFile='output.xlsx', rcDF=rcDF, zcDF=zcDF, progressDF=progressDF,exportCSVs=True)
else: # run once
	run_script(inputFile='input.csv', outputFile='output.xlsx', rcDF=rcDF, zcDF=zcDF)