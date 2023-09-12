#!/usr/bin/env python3

import configparser
from datetime import datetime, timezone
import json
import sys
import time
from influxdb import InfluxDBClient
from pygtail import Pygtail

class QueueLogLine:
	ts: 0
	callid: None
	queue: None
	agent: None
	action: None 
	data1: None 
	data2: None
	data3: None 
	data4: None 

config = configparser.ConfigParser()
config.read('config.ini')

influx_config = config['influxdb']

client = InfluxDBClient(host=influx_config.get('host', 'localhost'), 
						port=influx_config.get('port', 8086),
						username=influx_config.get('user', None),
						password=influx_config.get('password', None))

def db_exists(dbname):
	dbs = client.get_list_database()
	for db in dbs:
		if db['name'] == dbname:
			return True
	return False

def select_db():    
	dbname = influx_config['database']
	if not db_exists(dbname):
		print (f"Database '{dbname}' doesn't exist. Creating...")
		client.create_database(dbname)
		print (f"Done.")

	client.switch_database(dbname)

def parse_line(line):
	tokens = line.split("|")
	parsed = QueueLogLine()
	dt = datetime.fromtimestamp(int(tokens[0]), tz=datetime.now().astimezone().tzinfo)
	parsed.ts = dt.isoformat()
	parsed.callid = tokens[1]
	parsed.queue = tokens[2]
	parsed.agent = tokens[3]
	parsed.action = tokens[4]
	if len(tokens) > 5:
		parsed.data1 = tokens[5]
	if len(tokens) > 6:
		parsed.data2 = tokens[6]
	if len(tokens) > 7:
		parsed.data3 = tokens[7]
	if len(tokens) > 8:
		parsed.data4 = tokens[8]
	return parsed

def line_to_influx(parsed):
	record = {
		'measurement': 'queue_log',
		'time': parsed.ts,
		'tags': {
			'queue': parsed.queue,
			'action': parsed.action,
			'agent': parsed.agent
		},
		'fields': {
			'callid': parsed.callid
		}
	}

	if parsed.action == 'ABANDON':
		record['fields']['exit_position'] = int(parsed.data1)
		record['fields']['enter_position'] = int(parsed.data2)
		record['fields']['wait_time'] = int(parsed.data3)
	elif parsed.action == 'ADDMEMBER':
		pass
	elif parsed.action == 'AGENTDUMP':
		pass
	elif parsed.action == 'AGENTLOGIN':
		pass
	elif parsed.action == 'AGENTLOGOFF':
		pass
	elif parsed.action == 'COMPLETEAGENT':
		record['fields']['wait_time'] = int(parsed.data1)
		record['fields']['call_length'] = int(parsed.data2)
		record['fields']['enter_position'] = int(parsed.data3)
	elif parsed.action == 'COMPLETECALLER':
		record['fields']['wait_time'] = int(parsed.data1)
		record['fields']['call_length'] = int(parsed.data2)
		record['fields']['enter_position'] = int(parsed.data3)
	elif parsed.action == 'CONFIGRELOAD':
		pass
	elif parsed.action == 'CONNECT':
		record['fields']['wait_time'] = int(parsed.data1)
		record['fields']['ring_time'] = int(parsed.data3)
	elif parsed.action == 'ENTERQUEUE':
		record['fields']['url'] = parsed.data1
		record['fields']['callerid'] = parsed.data2
	elif parsed.action == 'EXITEMPTY':
		record['fields']['exit_position'] = int(parsed.data1)
		record['fields']['enter_position'] = int(parsed.data2)
		record['fields']['wait_time'] = int(parsed.data3)
	elif parsed.action == 'EXITWITHKEY':
		record['fields']['exit_key'] = parsed.data2
		record['fields']['exit_position'] = int(parsed.data2)
		record['fields']['enter_position'] = int(parsed.data3)
		record['fields']['wait_time'] = int(parsed.data4)
	elif parsed.action == 'EXITWITHTIMEOUT':
		record['fields']['exit_position'] = int(parsed.data1)
		record['fields']['enter_position'] = int(parsed.data2)
		record['fields']['wait_time'] = int(parsed.data3)
	elif parsed.action == 'PAUSE':
		pass
	elif parsed.action == 'PAUSEALL':
		pass
	elif parsed.action == 'UNPAUSE':
		pass
	elif parsed.action == 'UNPAUSEALL':
		pass
	elif parsed.action == 'PENALTY':
		pass
	elif parsed.action == 'REMOVEMEMBER':
		pass
	elif parsed.action == 'RINGNOANSWER':
		pass
	elif parsed.action == 'TRANSFER':
		record['fields']['transfer_extension'] = parsed.data1
		record['fields']['wait_time'] = int(parsed.data2)
		record['fields']['call_length'] = int(parsed.data3)
		record['fields']['enter_position'] = int(parsed.data4)
	elif parsed.action ==  'SYSCOMPAT':
		pass

	return record

def process_line(line):
	parsed = parse_line(line)
	record = line_to_influx(parsed)
	print(json.dumps([record]))
	client.write_points([record])

def process_input():
	for line in Pygtail("queue_log"):
		sys.stdout.write(line)    
		process_line(line)

if __name__ == "__main__":
	select_db()
	while True:
		process_input()
		time.sleep(0.5)
