## monitor release notes

### 14-Sep-2011 version ?.?.???

server and client: original implementation

### 16-Sep-2011 version ?.?.???

server and client: added `processes`, `users`, `load`, `proc_mem`

### 19-Sep-2011 version ?.?.???

server and client: added `network` (for Windows)

### 22-Sep-2011 version ?.?.???

server and client: added `disk_space_mb` (report in MB rather than GB)

### 12-Oct-2012 version ?.?.???

server and client: added `apt_updates` (Linux only)

### 05-Jul-2013 version ?.?.???

server: added `mdstat()`

### 13-Sep-2013 version ?.?.???

server: enhanced `mdstat()` to cater for recovery situations (e.g. replaced HDD)

### 04-Nov-2013 version 0.1.001

server: added `mailq_size()` (Linux only)

### 14-Mar-2014 version 0.1.002

server: added `yum_updates` (Linux only)

### 17-Mar-2013 version 0.1.003

server: tweaked `yum_updates` to use `subprocess.call`

### 29-Aug-2014 version 0.1.004

server: added `mon_version()`, `has_process()`

### 15-May-2015 version 0.1.005

server: added `apt_updates2` (Linux only - Debian specifically)

### 22-Sep-2015 version 0.1.005

client: added `apt_updates2a()` (for Debian and Zabbix)

### 23-Oct-2015 version 0.1.006

server: added `swap_backup_drive()` (Bacula-director server only)

### 18-Mar-2016 version 0.1.007

server: added `mount` (Linux only)

### 14-Oct-2016 version 0.1.008

server: added `mdstat2` (returns number instead of string for Zabbix)

### 15-Sep-2017 version 0.1.009

server: added `executable` (Linux only) returns 1 if specified file is executable

### 14-Dec-2018 version 0.1.010

client: added `get_temp` (for XenServer)

### 25-Dec-2019 version 0.1.010

server: added `rpi_temp` (RPionly)

### 20-Apr-2020 version 0.1.011

server: due to psutil changes, replaced `get_process_list` with `process_iter`

### 22-Nov-2020 version 0.1.012

server: added `rpi_room_temp` (RPi only)
client: added `rpi_room_temp` (RPi only)
        import `xmlrpclib` (Python 2) or `xmlrpc.client` (Python 3)
        replace `print` with `Writeln()` for Python 2/3 compatibility

### 08-Dec-2020 version 0.1.013

client: adjust room temperature readings for selected nodes (RPi)

