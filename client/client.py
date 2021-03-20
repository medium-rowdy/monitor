#!/usr/bin/env python3
#
# client.py - get stats from a remote server using XML-RPC
#
# client.py server port what [how]
#
# e.g. client.py 192.168.1.8 8000 disk_space /
#
# note: Nagios-style output, either "0" if there is one return value, or "label:1 next:2"

import sys

VERSION = '0.1.013'

def Write(s):
    sys.stdout.write(str(s))
    sys.stdout.flush()

def Writeln(s):
    Write(str(s) + '\n')

def print0():
    Writeln('0')

if len(sys.argv) < 4:
    print0()
    sys.exit()

server = sys.argv[1]
port = sys.argv[2]
what = sys.argv[3]
how = ''
if len(sys.argv) > 4:
    how = sys.argv[4]

try:
    # Python 2
    import xmlrpclib
    xrServer = xmlrpclib.Server('http://' + server + ':' + port)
except ImportError:
    # Python 3
    import xmlrpc.client
    xrServer = xmlrpc.client.ServerProxy('http://' + server + ':' + port)

if 1 == 1: #try:
    if what == 'kill':
        xrServer.kill()
    elif what == 'disk_space':
        if how == '':
            total = 0
            used = 0
            free = 0
        else:
            total, used, free = xrServer.disk_space(how)
        Writeln('total:%d used:%d free:%d' % (total, used, free))
    elif what == 'disk_space_mb':
        if how == '':
            total = 0
            used = 0
            free = 0
        else:
            total, used, free = xrServer.disk_space_mb(how)
        Writeln('total:%d used:%d free:%d' % (total, used, free))
    elif what == 'cpu_usage':
        Writeln(xrServer.cpu_usage())
    elif what == 'cpu_times':
        user, system, idle, nice, iowait, irq, softirq = xrServer.cpu_times()
        Writeln('user:%d system:%d idle:%d nice:%d iowait:%d irq:%d softirq:%d' % (user, system, idle, nice, iowait, irq, softirq))
    elif what == 'memory':
        total, used, free = xrServer.memory()
        Writeln('total:%d used:%d free:%d' % (total, used, free))
    elif what == 'swap':
        total, used, free = xrServer.swap()
        Writeln('total:%d used:%d free:%d' % (total, used, free))
    elif what == 'processes':
        Writeln(xrServer.processes())
    elif what == 'users':
        Writeln(xrServer.users())
    elif what == 'load':
        load1, load5, load15 = xrServer.load()
        Writeln('1min:%f 5min:%f 15min:%f' % (load1, load5, load15))
    elif what == 'proc_mem':
        if how == '':
            rss = 0
            vms = 0
        else:
            rss, vms = xrServer.proc_mem(how)
        Writeln('rss:%d vms:%d' % (rss, vms))
    elif what == 'network':
        kbytesIn, kbytesOut = xrServer.network()
        Writeln('in:%d out:%d' % (kbytesIn, kbytesOut))
    elif what == 'apt_updates':
        available, security = xrServer.apt_updates()
        Writeln('available:%d security:%d' % (available, security))
    elif what == 'apt_updates2':
        available = xrServer.apt_updates2()
        # Leave security as 0 as we cannot determine that, and the existing Nagios script will still work
        Writeln('available:%d security:0' % available)
    elif what == 'apt_updates2a':
        available = xrServer.apt_updates2()
        Writeln(available)
    elif what == 'mdstat':
        # this is not intended to be processed by Cacti (mainly by Nagios)
        if how == '':
            Writeln('error')
        else:
            s = xrServer.mdstat(how)
            Writeln(s)
    elif what == 'mdstat2':
        # this is intended to be processed by Zabbi
        if how == '':
            Writeln('-2')
        else:
            s = xrServer.mdstat2(how)
            Writeln(s)
    elif what == 'mailq_size':
        Writeln(xrServer.mailq_size())
    elif what == 'yum_updates':
        available = xrServer.yum_updates()
        Writeln(available)
    elif what == 'mon_version':
        Writeln(xrServer.mon_version())
    elif what == 'has_process':
        if how == '':
            Writeln('0')
        else:
            s = xrServer.has_process(how)
            Writeln(s)
    elif what == 'swap_backup_drive':
        Writeln(xrServer.swap_backup_drive())
    elif what == 'mount':
        if how == '':
            Writeln('0')
        else:
            s = xrServer.mount(how)
            Writeln(s)
    elif what == 'executable':
        if how == '':
            Writeln('0')
        else:
            s = xrServer.executable(how)
            Writeln(s)
    elif what == 'get_temp':
        if how == '':
            Writeln('-1')
        else:
            s = xrServer.get_temp(how)
            Writeln(s)
    elif what == 'rpi_temp':
        Writeln(xrServer.rpi_temp())
    elif what == 'rpi_room_temp':
        q = xrServer.rpi_room_temp()
        # Some BMP280 sensors are known to have significant deviations.
        if server in ['europium', '192.168.2.63']:
            q -= 2
        elif server in ['terbium', '192.168.2.65']:
            q -= 4
        Writeln(q)
    else:
        print0()
#except:
#    print0()

