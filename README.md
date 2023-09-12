# queuelog_to_influxdb

Script to import Asterisk queue_log into an influxDB database

On first run, the script creates database named "asterisk".

The script monitors the queue_log file (like a "tail -f" command) and inserts any new events into InfluxDB. It detects log rotation and can resume an interrupted export, thanks to the Pygtail module. 

## Install
Install required libraries. (recommended: use a virtualenv)
```
$ pip install -r requirements.txt
```
## Configuration
Edit config.ini according to your installation:

```
[general]
queue_log = /var/log/asterisk/queue_log

[influxdb]
database = asterisk 
host = localhost
port = 8086
user = user
password = password
```

## Usage
Simple usage:
```
$ python queuelog_to_influxdb.py
```

Load a different log file and exit. Don't wait for new lines:
```
$ python queuelog_to_influxdb --one-shot --file /var/log/asterisk/queue_log-20230811
```

