# monitor
System monitor scripts written in Python.

This project was started many years ago as a way to extend [Cacti](https://github.com/cacti/), then [Nagios](https://github.com/NagiosEnterprises/nagioscore), and lately [Zabbix](https://github.com/zabbix/zabbix).

The Cacti and Nagios functionality may not even work, as it is a long time since _monitor_ was used in those environments.

Currently it is intended to be run, typically via systemd (although that is not a requirement) on one or more remote server, and the client utility to be invoked as an external command from Zabbix.

Generally the server part it requires [psutil](https://github.com/giampaolo/psutil), and for Raspberry Pi environment monitoring via a BMP280 sensor, the [BMP280 library](https://github.com/pimoroni/bmp280-python).

The client part needs nothing outside of the standard Python libraries.

It was developed on Python 2, but probably still works on both Python 2 and 3.

