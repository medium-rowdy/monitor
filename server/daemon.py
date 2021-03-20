#!/usr/bin/env python

import sys, os
import datetime

###########################################################################
# configure these paths:
MON_DIR = '/opt/monitor'
LOGFILE = '/var/log/monitor.log'
PIDFILE = os.path.join(MON_DIR, 'monitor.pid'

# let USERPROG be the main function of your project
import server
USERPROG = server.server
# ADDRESS and PORT are, well, the address and port to listen on
ADDRESS = '192.168.2.64'
PORT = 8002
###########################################################################

# based on J\uffffrgen Hermanns http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/66012

class Log:
    '''file like for writes with auto flush after each write
    to ensure that everything is logged, even during an
    unexpected exit.'''
    def __init__(self, f):
        self.f = f
    def write(self, s):
        self.f.write(s)
        self.f.flush()

def main():
    # change to data directory if needed
    os.chdir(MON_DIR)
    # redirect outputs to a logfile
    sys.stdout = sys.stderr = Log(open(LOGFILE, 'a+'))
    #print '%s - daemon.py main()' % str(datetime.datetime.now())[:19]
    # ensure that the daemon runs a normal user (unless we need to run as root, or as the user in the systemd script)
    #os.setegid(103)     #set group first 'pydaemon'
    #os.seteuid(103)     #set user 'pydaemon'
    # start the user program here:
    USERPROG(ADDRESS, PORT)

if __name__ == '__main__':
    # Possibly this is not required when running as a systemd service ...
    if 0 == 1:
        # do the UNIX double-fork magic, see Stevens' 'Advanced
        # Programming in the UNIX Environment' for details (ISBN 0201563177)
        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError, e:
            print >>sys.stderr, 'fork #1 failed: %d (%s)' % (e.errno, e.strerror)
            sys.exit(1)

        # decouple from parent environment
        os.chdir('/')   #don't prevent unmounting....
        os.setsid()
        os.umask(0)

        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent, print eventual PID before
                print 'Daemon PID %d' % pid
                open(PIDFILE,'w').write('%d'%pid)
                sys.exit(0)
        except OSError, e:
            print >>sys.stderr, 'fork #2 failed: %d (%s)' % (e.errno, e.strerror)
            sys.exit(1)

    # start the daemon main loop
    main()

