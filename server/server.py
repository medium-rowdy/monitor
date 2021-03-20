#!/usr/bin/python
# -*- coding: latin-1 -*-
#
# server.py - XML-RPC server for server monitoring

from SimpleXMLRPCServer import *
import socket, os, sys, psutil, subprocess, datetime, stat

# 22-Nov-2020 Imports for room temperature (RPi only).
sysname, nodename, release, version, machine = os.uname()
if machine.startswith('arm'):
    try:
        from bmp280 import BMP280
    except ImportError:
        pass
    try:
        from smbus2 import SMBus
    except ImportError:
        from smbus import SMBus
    # Initialise the BMP280.
    bus = SMBus(1)
    bmp280 = BMP280(i2c_dev = bus)

########################################################################################################
# IMPORTANT: Version number changes must be reflected in: /usr/lib/nagios/plugins/check_r_mon_version.py
########################################################################################################
VERSION = '0.1.013'

ONE_KB  = 1024
ONE_MB  = ONE_KB * ONE_KB
ONE_GB  = ONE_MB * ONE_KB

# ----------------------------------------------------------------------------

class XMLRPCServer_r(SimpleXMLRPCServer):

    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)

# ----------------------------------------------------------------------------

class MyServer(XMLRPCServer_r):

    def serve_forever(self):
        self.quit = 0
        while not self.quit:
            self.handle_request()

####################################################################################################

def kill():
    global server
    server.quit = 1
    return 1

def disk_space(what):
    result = psutil.disk_usage(what)
    total = result.total / ONE_GB
    used = result.used / ONE_GB
    free = result.free / ONE_GB
    return total, used, free

def disk_space_mb(what):
    result = psutil.disk_usage(what)
    total = result.total / ONE_MB
    used = result.used / ONE_MB
    free = result.free / ONE_MB
    return total, used, free

def cpu_usage():
    return psutil.cpu_percent(interval = 1)

def cpu_times():
    user = 0
    system = 0
    idle = 0
    nice = 0
    iowait = 0
    irq = 0
    softirq = 0
    result = psutil.cpu_times()
    if sys.platform == 'linux2':
        user = int(result.user)
        system = int(result.system)
        idle = int(result.idle)
        nice = int(result.nice)
        iowait = int(result.iowait)
        irq = int(result.irq)
        softirq = int(result.softirq)
    elif sys.platform == 'win32':
        user = int(result.user)
        system = int(result.system)
        idle = int(result.idle)
    return user, system, idle, nice, iowait, irq, softirq

def memory():
    result = psutil.phymem_usage()
    total = result.total / ONE_MB
    used = result.used / ONE_MB
    free = result.free / ONE_MB
    return total, used, free

def swap():
    result = psutil.virtmem_usage()
    total = result.total / ONE_MB
    used = result.used / ONE_MB
    free = result.free / ONE_MB
    return total, used, free

def processes():
    kount = 0
    for p in psutil.process_iter(['name']):
        kount += 1
    return kount

def users():
    result = 0
    if sys.platform == 'linux2':
        #  11:20:06 up 34 days, 17:39,  1 user,  load average: 0.16, 0.27, 0.26
        # USER     TTY      FROM              LOGIN@   IDLE   JCPU   PCPU WHAT
        # rowdy    pts/1    f106_r           08:25    0.00s 10.81s  0.10s sshd: rowdy [pr

        i = os.popen('/usr/bin/w')
        s = i.readline() # uptime/load
        s = i.readline() # headings
        while 1:
            s = i.readline()
            if s == '':
                break
            result += 1
        i.close()
    return result

def load():
    load1 = 0.0
    load5 = 0.0
    load15 = 0.0
    if sys.platform == 'linux2':
        # 0.68 0.34 0.29 2/266 32439

        i = open('/proc/loadavg')
        s = i.readline()
        i.close()
        c = s.split(' ')
        load1 = float(c[0])
        load5 = float(c[1])
        load15 = float(c[2])
    return load1, load5, load15

def proc_mem(what):
    what = what.lower()
    rss = 0
    vms = 0
    for p in psutil.process_iter():
        try:
            if p.name.lower().find(what) != -1:
                m = p.get_memory_info()
                rss += m.rss
                vms += m.vms
        except psutil.AccessDenied:
            pass # for some reason some processes cannot be queried on Microsfot, even as Administrator
    rss = rss / ONE_MB
    vms = vms / ONE_MB
    return rss, vms

def network():
    kbytesIn = 0
    kbytesOut = 0

    if sys.platform == 'win32':
        # Interface Statistics
        #
        #                            Received            Sent
        #
        # Bytes                    4268697340      3633365601
        # Unicast packets           204561365       216948742
        # Non-unicast packets         5962365          113644
        # Discards                          0               0
        # Errors                            0               0
        # Unknown protocols                 0

        i = os.popen('netstat -e')
        while 1:
            s = i.readline()
            if s == '':
                break
            if s.startswith('Bytes '):
                s = ' '.join(s.split())
                c = s.split(' ')
                kbytesIn = int(c[1]) / 1024
                kbytesOut = int(c[2]) / 1024
                break
        i.close()

    return kbytesIn, kbytesOut

def apt_updates():
    # Note that this works on Ubuntu.
    available = 0
    security = 0

    if sys.platform == 'linux2':
        i = os.popen('/usr/lib/update-notifier/apt-check --human-readable')
        s = i.readline()
        c = s.split(' ')
        available = int(c[0])
        s = i.readline()
        c = s.split(' ')
        security =  int(c[0])
        i.close()

    return available, security

def apt_updates2():
    # Note that this works on Debian, and probably other Debian derivatives.
    available = -1 # error

    if sys.platform == 'linux2':
        os.system('/usr/bin/apt-get -qq update')
        i = os.popen('/usr/bin/apt-get -qs upgrade')
        while 1:
            s = i.readline()
            if s == '':
                break
            s = s.replace('\r', '').replace('\n', '').strip()
            if s.find('upgraded,') != -1:
                if s == '0 upgraded, 0 newly installed, 0 to remove and 0 not upgraded.':
                    available = 0 # nothing to upgrade
                else:
                    c = s.split(' ')
                    available = int(c[0]) # something to upgrade
        i.close()

    return available

def yum_updates():
    available = 0

    if sys.platform == 'linux2':
        q = subprocess.call(['/usr/bin/yum', 'check-update'], stdout = subprocess.PIPE)
        if q == 100: # updates are available
            available = 1
        elif q == 1: # an error occurred
            available = 2

    return available

def mdstat(what):
    # what = something like md0 or md1 (NOT /dev/md0)
    # return:
    #   ok           = the array is operational and not resyncing
    #   resync_50%   = the array is resyncing at 50% progress
    #   broken       = the array is broken (this is bad)
    #   not_found    = the specified array was not found
    #   recovery_50% = the array is recovering at 50% progress
    #   broken       = any other status is probably broken

    # from Ubuntu:

    # Personalities : [linear] [multipath] [raid0] [raid1] [raid6] [raid5] [raid4] [raid10]
    # md0 : active raid1 sdb1[1] sda1[0]
    #       308592576 blocks [2/2] [UU]
    #
    # md1 : active raid1 sdb2[1] sda2[0]
    #       3977152 blocks [2/2] [UU]
    #
    # unused devices: <none>

    # Personalities : [linear] [multipath] [raid0] [raid1] [raid6] [raid5] [raid4] [raid10]
    # md1 : active raid1 sda2[0] sdb2[1]
    #       3977152 blocks [2/2] [UU]
    #
    # md0 : active raid1 sdb1[1] sda1[0]
    #       308592576 blocks [2/2] [UU]
    #       [=>...................]  resync =  9.5% (29481472/308592576) finish=172.0min speed=27039K/sec
    #
    # unused devices: <none>

    # from CentOS:

    # Personalities : [raid1]
    # md0 : active raid1 sda1[0] sdb1[1]
    #       1023936 blocks super 1.0 [2/2] [UU]
    #
    # md1 : active raid1 sda3[0] sdb3[1]
    #       1948163904 blocks super 1.1 [2/2] [UU]
    #       bitmap: 3/15 pages [12KB], 65536KB chunk
    #
    # unused devices: <none>

    found = 0
    status = 0
    foundResync = 0
    resyncProgress = 'unknown'
    foundRecovery = 0
    recoveryProgress = 'unknown'
    i = open('/proc/mdstat')
    while 1:
        s = i.readline()
        if s == '':
            break
        s = s.strip()
        if s.startswith('Personalities'):
            continue
        if s.find(' : ') != -1:
            # found a header line, see if it is for the array we are looking for
            if s.startswith(what):
                # yes!
                found = 1
                s = i.readline()
                s = s.strip()
                if s.endswith('[UU]'):
                    status = 1
                s = i.readline()
                s = s.strip()
                if s.find('resync') != -1:
                    foundResync = 1
                    #       [=>...................]  resync =  9.5% (29481472/308592576) finish=172.0min speed=27039K/sec
                    s = ' '.join(s.split())
                    c = s.split(' ')
                    for cc in c:
                        if cc.find('%') != -1:
                            resyncProgress = cc
                if s.find('recovery') != -1:
                    foundRecovery = 1
                    #       [===>.................]  recovery = 19.4% (93223104/478514112) finish=157.9min speed=40640K/sec
                    s = ' '.join(s.split())
                    c = s.split(' ')
                    for cc in c:
                        if cc.find('%') != -1:
                            recoveryProgress = cc
                break
    i.close()

    if found == 0:
        return 'not_found'
    elif foundResync != 0:
        return 'resync_%s' % resyncProgress
    elif foundRecovery != 0:
        return 'recovery_%s' % recoveryProgress
    elif status == 1:
        return 'ok'
    else:
        return 'broken'

def mdstat2(what):
    # return:
    #   0 = ok           = the array is operational and not resyncing
    #   1 = resync_50%   = the array is resyncing at 50% progress
    #   2 = broken       = the array is broken (this is bad)
    #   3 = not_found    = the specified array was not found
    #   4 = recovery_50% = the array is recovering at 50% progress
    #   5 = unknown status, probably broken
    s = mdstat(what)
    if s == 'not_found':
        return 3
    elif s.startswith('resync_'):
        return 1
    elif s.startswith('recovery_'):
        return 4
    elif s == 'ok':
        return 0
    else:
        return 5

def mailq_size():
    size = 0
    if sys.platform == 'linux2':
        # -Queue ID- --Size-- ----Arrival Time---- -Sender/Recipient-------
        # 8287DE811EB     2223 Wed Oct 30 19:00:07  sender@bad_domain.com.au
        # (host filter1.somewhere.com.au[1.2.3.4] said: 450 4.1.8 <sender@bad_domain.com.au>: Sender address rejected: Domain not found (in reply to RCPT TO command))
        #                                          recipient@example.com.au
        #
        # ...
        # 4ABFEE81952     1177 Thu Oct 31 20:46:03  sender@example.com.au
        # (host mail-abs.somewhere.com.au[1.2.3.5] said: 421 4.3.2 System not accepting network messages (in reply to end of DATA command))
        #                                          recipient@example.com.au
        #
        # -- 23 Kbytes in 10 Requests.

        i = os.popen('/usr/bin/mailq')
        while 1:
            s = i.readline()
            if s == '':
                break
            if (s.find('Kbytes') != -1) and (s.find('Requests') != -1):
                c = s.split(' ')
                size = int(c[4])
                break
        i.close()

    return size

def mon_version():
    return VERSION

def has_process(what):
    found = 0
    for p in psutil.process_iter(['cmdline']):
        cmdline = p.cmdline()
        if what in cmdline:
            found = 1
    return found

def swap_backup_drive():
    # Really only applicable for a Bacula server, return 1 if the backup drive needs to be swapped.
    # According to the current schedule, that is on Friday after 6am if there are backup files from
    # earlier in the week still in the root directory on the backup file system.
    # This does not cater exactly for holidays (long weekends).
    # This also does not cater for the drive being unmounted at the time of checking.
    result = 0
    noww = datetime.datetime.now()
    if (noww.weekday() == 4) and (noww.hour > 6): # Friday
        names = os.listdir('/usb')
        for name in names:
            # skip the .tmp file to keep the drive awake
            if (name.find('_201') != -1) and not(name.endswith('.tmp')):
                result = 1
    return result

def mount(what):
    found = 0
    if sys.platform == 'linux2':
        # /dev/md0 on / type ext4 (rw,errors=remount-ro)
        # proc on /proc type proc (rw,noexec,nosuid,nodev)
        # none on /sys type sysfs (rw,noexec,nosuid,nodev)
        # none on /sys/fs/fuse/connections type fusectl (rw)
        # none on /sys/kernel/debug type debugfs (rw)
        # none on /sys/kernel/security type securityfs (rw)
        # none on /dev type devtmpfs (rw,mode=0755)
        # none on /dev/pts type devpts (rw,noexec,nosuid,gid=5,mode=0620)
        # none on /dev/shm type tmpfs (rw,nosuid,nodev)
        # none on /var/run type tmpfs (rw,nosuid,mode=0755)
        # none on /var/lock type tmpfs (rw,noexec,nosuid,nodev)
        # none on /lib/init/rw type tmpfs (rw,nosuid,mode=0755)
        # //xylon/files on /fms/xylon type cifs (rw,mand)
        # /dev/sdc1 on /usb type ext4 (rw)

        # note: searching for /usb - we will actually look for ' on /usb '
        #       so that searching for mount / will work correctly
        mounted = ' on %s ' % what

        i = os.popen('/bin/mount')
        while 1:
            s = i.readline()
            if s == '':
                break
            if s.find(mounted) != -1:
                found = 1
                break
        i.close()

    return found

def executable(what):
    executable = 0
    if sys.platform == 'linux2':
        # Only if it exists, otherwise return 0 (not executable).
        if os.path.exists(what):
            q = os.stat(what)
            w = q.st_mode
            if (w & stat.S_IXUSR) or (w & stat.S_IXGRP) or (w & stat.S_IXOTH):
                executable = 1

    return executable

def rpi_temp():
    result = 0.0
    # Only for RPi (arm)
    sysname, nodename, release, version, machine = os.uname()
    if machine.startswith('arm'):
        i = os.popen('/opt/vc/bin/vcgencmd measure_temp')
        s = i.readline()
        i.close()
        # temp=46.5'C
        s = s.replace("'", '=')
        # temp=46.5=C
        c = s.split('=')
        # 0: temp
        # 1: 46.5
        # 2: C
        result = float(c[1])
    return result

def rpi_room_temp():
    result = 0.0
    # Only for RPi (arm)
    sysname, nodename, release, version, machine = os.uname()
    if machine.startswith('arm'):
        result = bmp280.get_temperature()
    return result

####################################################################################################

def server(theAddress, thePort):
    global server
    print 'initialising ...'

    server = MyServer((theAddress, thePort))
    server.register_function(kill)
    server.register_function(disk_space)
    server.register_function(disk_space_mb)
    server.register_function(cpu_usage)
    server.register_function(cpu_times)
    server.register_function(memory)
    server.register_function(swap)
    server.register_function(processes)
    server.register_function(users)
    server.register_function(load)
    server.register_function(proc_mem)
    server.register_function(network)
    server.register_function(apt_updates)
    server.register_function(mdstat)
    server.register_function(mdstat2)
    server.register_function(mailq_size)
    server.register_function(yum_updates)
    server.register_function(mon_version)
    server.register_function(has_process)
    server.register_function(apt_updates2)
    server.register_function(swap_backup_drive)
    server.register_function(mount)
    server.register_function(executable)
    server.register_function(rpi_temp)
    server.register_function(rpi_room_temp)

    print '... initialised'

    print 'running ...'
    server.serve_forever()
    print '... ran'

    server.server_close()

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print 'server.py: usage: server.py address port'
        sys.exit(1)

    anAddress = sys.argv[1]
    anPort = int(sys.argv[2])

    server(anAddress, anPort)

