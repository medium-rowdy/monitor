# monitor installation notes

_These notes are kinda clunky, as Rowdy only ever installed on servers he managed for his own purposes  Should be enough to get you started, though._

## Terminology

To avoid confusion, or perhaps add to it, the computer where the monitor server script is running is referred to as the `server`.

The computer where the client script is running is referred to as the `client`.

Typically these scripts are used to augment another monitoring application, such as Zabbix, in which case the client script will be running on the Zabbix server.

## Server installation

In general all files should be copied to /opt/monitor (in a flat directory structure - they are only separated here for convenience of maintenance).

So you should have something like:

```
root@carbon:~# ls -l /opt/monitor
total 72
-rwxr-xr-x 1 rowdy rowdy  6522 2020-12-08 08:52 client.py
-rwxr--r-- 1 rowdy rowdy  2367 2019-12-25 13:25 daemon.py
-rw-r--r-- 1 rowdy rowdy   180 2020-11-22 15:16 monitor.service
-rw-r--r-- 1 rowdy rowdy 18657 2020-11-22 15:22 server.py
-rwxr--r-- 1 rowdy rowdy   411 2019-12-25 13:00 start.sh
```

monitor can be started from conventional (i.e. non-systemd) scripts by invoking `start.sh` from `/etc/rc.local`.

On systemd-based systems copy `monitor.service` to `/etc/systemd/system`, execute `systemd daemon-reload`, and then use the usual systemd commands to check the status, start/stop, enable/disable `monitor.service`.

In both cases edit `daemon.py` and adjust the directories, systemd flag, address and port near the top of the script.

The selected port should be open in the firewall so the client script can connect.

Either start the systemd service (`systemctl start monitor.service`), or manually run the startup script (`/opt/monitor/start.sh`).

Once started, check the log file (`/var/log/monitor.log` by default) for startup messages.

On the monitor server, you can run the client script and connect to itself to confirm operation.

Use a command like `/opt/monitor/client.py 192.168.2.64 8002 mon_version`, substituting the server's IP address and configured port.  This should respond with the monitor version installed, like this:

```
root@gadolinium:~# /opt/monitor/client.py 192.168.2.64 8002 mon_version
0.1.013
```

## Client installation

There is not really anything to install, as such.

`client.py` is intended to be invoked from other monitoring applications, such as Zabbix.  As Rowdy currently uses Zabbix, these notes will concentrate on that.

Copy `client.py` to the Zabbix external scripts directory, usually `/usr/lib/zabbix/externalscripts`.  Ensure it is executable (in particular by the user that Zabbix is running as).

Add a new item in Zabbix, with the following properties:

  * Name: give it a meaningful name
  * Type: `External check`
  * Key: `client.py[{HOST.CONN},8002,rpi_temp]`
  * Host interface: as appropriate for the host - typically the ADDRESS configured in `daemon.py`
  * Type of information: most stats are `Numeric (unsigned)` or `Numeric (float)`
  * Update interval: choose with care - for example it does not make sense to check for apt updates every 60 seconds (see note below)
  * Applications: select an application, if applicable

That's pretty much it.

Until documented better, to get an idea whether to choose `Numeric (unsigned)` or `Numeric (float)`, run the client script to retrieve teh required metric, and visually inspect the result.  For example `processes` returns a simple int, whereas `rpi_temp` returns a float.

For the update interval, the Zabbix default seems to be 1 minute.  That would be fine for inexpensive checks of metrics that would be expected to change significantly in a 60 second period, such as the number of processes.  For things like disk space and temperature, checking once every 5 minutes should suffice.  For expensive checks like apt/yum updates, checking every 15 or 30 minutes should be more than sufficient.


