""" 
Runtime config variables
"""

import configparser

current_config = {
	"config_file": "",
	"one_shot": False,
	"verbose": False,
	"log_file": None,
	"influx_db": "",
	"influx_host": "",
	"influx_port": 0,
	"influx_user": None,
	"influx_password": None
}

def read_config():
	config = configparser.ConfigParser()
	config.read(current_config["config_file"])
	if current_config["log_file"] == None:
		current_config["log_file"] = config["general"].get("queue_log")
	current_config["influx_db"] = config["influxdb"].get("database", "asterisk")
	current_config["influx_host"] = config["influxdb"].get("host", "localhost")
	current_config["influx_port"] = config["influxdb"].get("port", 8086)
	current_config["influx_user"] = config["influxdb"].get("user", None)
	current_config["influx_password"] = config["influxdb"].get("password", None)
