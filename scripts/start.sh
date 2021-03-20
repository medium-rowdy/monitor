#!/usr/bin/env bash
#
# /opt/monitor/start.sh - start the monitor daemon
#

LOG=/var/log/monitor.log

echo `date +"%d-%b-%Y %H:%M:%S"` ------------------------------------------------------------------ >> $LOG
echo `date +"%d-%b-%Y %H:%M:%S"` - starting >> $LOG

cd /opt/monitor

echo `date +"%d-%b-%Y %H:%M:%S"` - `pwd` >> $LOG

/usr/bin/env python daemon.py

ps axufw | grep -i python | grep -v grep >> $LOG

