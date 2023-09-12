""" 
influxdb related methods
"""

from influxdb import InfluxDBClient

import _config

client = None 

def db_exists(dbname):
	dbs = client.get_list_database()
	for db in dbs:
		if db['name'] == dbname:
			return True
	return False

def select_db():    
	global client 
	client = InfluxDBClient(host=_config.current_config["influx_host"],
						port=_config.current_config["influx_port"],
						username=_config.current_config["influx_user"],
						password=_config.current_config["influx_password"])
	dbname = _config.current_config["influx_db"]
	if not db_exists(dbname):
		print (f"Database '{dbname}' doesn't exist. Creating...")
		client.create_database(dbname)
		print (f"Done.")

	client.switch_database(dbname)

def line_to_influx(log_line):
	record = {
		'measurement': 'queue_log',
		'time': log_line.ts,
		'tags': {
			'queue': log_line.queue,
			'action': log_line.action,
			'agent': log_line.agent
		},
		'fields': {
			'callid': log_line.callid
		}
	}

	if log_line.action == 'ABANDON':
		record['fields']['exit_position'] = int(log_line.data1)
		record['fields']['enter_position'] = int(log_line.data2)
		record['fields']['wait_time'] = int(log_line.data3)
	elif log_line.action == 'ADDMEMBER':
		pass
	elif log_line.action == 'AGENTDUMP':
		pass
	elif log_line.action == 'AGENTLOGIN':
		pass
	elif log_line.action == 'AGENTLOGOFF':
		pass
	elif log_line.action == 'COMPLETEAGENT':
		record['fields']['wait_time'] = int(log_line.data1)
		record['fields']['call_length'] = int(log_line.data2)
		record['fields']['enter_position'] = int(log_line.data3)
	elif log_line.action == 'COMPLETECALLER':
		record['fields']['wait_time'] = int(log_line.data1)
		record['fields']['call_length'] = int(log_line.data2)
		record['fields']['enter_position'] = int(log_line.data3)
	elif log_line.action == 'CONFIGRELOAD':
		pass
	elif log_line.action == 'CONNECT':
		record['fields']['wait_time'] = int(log_line.data1)
		record['fields']['ring_time'] = int(log_line.data3)
	elif log_line.action == 'ENTERQUEUE':
		record['fields']['url'] = log_line.data1
		record['fields']['callerid'] = log_line.data2
	elif log_line.action == 'EXITEMPTY':
		record['fields']['exit_position'] = int(log_line.data1)
		record['fields']['enter_position'] = int(log_line.data2)
		record['fields']['wait_time'] = int(log_line.data3)
	elif log_line.action == 'EXITWITHKEY':
		record['fields']['exit_key'] = log_line.data2
		record['fields']['exit_position'] = int(log_line.data2)
		record['fields']['enter_position'] = int(log_line.data3)
		record['fields']['wait_time'] = int(log_line.data4)
	elif log_line.action == 'EXITWITHTIMEOUT':
		record['fields']['exit_position'] = int(log_line.data1)
		record['fields']['enter_position'] = int(log_line.data2)
		record['fields']['wait_time'] = int(log_line.data3)
	elif log_line.action == 'PAUSE':
		pass
	elif log_line.action == 'PAUSEALL':
		pass
	elif log_line.action == 'UNPAUSE':
		pass
	elif log_line.action == 'UNPAUSEALL':
		pass
	elif log_line.action == 'PENALTY':
		pass
	elif log_line.action == 'REMOVEMEMBER':
		pass
	elif log_line.action == 'RINGNOANSWER':
		pass
	elif log_line.action == 'TRANSFER':
		record['fields']['transfer_extension'] = log_line.data1
		record['fields']['wait_time'] = int(log_line.data2)
		record['fields']['call_length'] = int(log_line.data3)
		record['fields']['enter_position'] = int(log_line.data4)
	elif log_line.action ==  'SYSCOMPAT':
		pass

	return record
