# monitor
System monitoring scripts written in Python.

This project was started many years ago as a way to extend [Cacti](https://github.com/cacti/), then [Nagios](https://github.com/NagiosEnterprises/nagioscore), and more recently [Zabbix](https://github.com/zabbix/zabbix).

The Cacti and Nagios functionality may not still work, as it is a long time since _monitor_ was used in those environments.

Currently the server utility is intended to be run, typically via systemd (although that is not a requirement), on one or more remote servers, and the client utility to be invoked as an external command from Zabbix.

Generally the server part requires [psutil](https://github.com/giampaolo/psutil), and for Raspberry Pi environment monitoring via a BMP280 sensor, the [BMP280](https://github.com/pimoroni/bmp280-python) library.

The client part needs nothing other than the standard Python libraries.

It was developed on Python 2, but probably works on both Python 2 and 3.

