#!/usr/bin/env python3

import argparse
from datetime import datetime
import json
import time
from pygtail import Pygtail

import _config
import _influx

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

def parse_args():
	parser = argparse.ArgumentParser(description='Monitor Asterisk queue_log and send events to influxdb.')
	parser.add_argument('--config', '-c', dest='config_file', action='store',
						default='config.ini',
						help='config file name (default: config.ini)')
	parser.add_argument('--file', '-f', dest='log_file', action='store',
						default=None,
						help='log file to read from (default: /var/log/asterisk/queue_log)')
	parser.add_argument('--one-shot', dest='one_shot', action='store_true',
						help="Just import the file and don't wait for new lines")
	parser.add_argument('--verbose', '-v', dest='verbose', action='store_true',
						help="Output lines as they are processed")
	args = parser.parse_args()

	_config.current_config["config_file"] = args.config_file
	_config.current_config["log_file"] = args.log_file
	_config.current_config["one_shot"] = args.one_shot
	_config.current_config["verbose"] = args.verbose
	
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

def process_line(line):
	if _config.current_config["verbose"]:
		print(line)

	parsed = parse_line(line)
	record = _influx.line_to_influx(parsed)
	if _config.current_config["verbose"]:
		print(json.dumps([record]))

	_influx.client.write_points([record])

def process_input():
	for line in Pygtail(_config.current_config["log_file"]):
		process_line(line)

if __name__ == "__main__":
	parse_args()
	_config.read_config()
	if _config.current_config["verbose"]:
		print (_config.current_config)

	_influx.select_db()
	while not _config.current_config["one_shot"]:
		process_input()
		time.sleep(0.5)
