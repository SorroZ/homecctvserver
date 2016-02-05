#/usr/bin/python

import sys
import time
import syslog
import SocketServer
import json

from daemon import Daemon
from cameraHandler import CameraHandler

# ------------------------------------------------------------------------------


class SecurityDaemon (SocketServer.ThreadingTCPServer, Daemon):
    camera = None
    pinHandler = None
    motionAcitivated = False

    def __init__(self):
        Daemon.__init__(self, '/var/run/homesecurity.pid',
                        stderr='/var/log/homesecurity.log')

    def run(self):

        # Open port and define handlerclass
        try:
            SocketServer.ThreadingTCPServer.__init__(
                self, ("0.0.0.0", 1995), ConnectionHandler)
            syslog.syslog('Socket server initiated')
        except:
            syslog.syslog('Socket server could not be initiated')
            exit(1)

        self.camera = CameraHandler()

        # Wait for connections
        syslog.syslog('Waiting for connections...')
        self.serve_forever()
        return


class ConnectionHandler (SocketServer.BaseRequestHandler):
    timeout = 5

    def handle(self):
        syslog.syslog('Client connected from: ' + str(self.client_address[0]))
        recv = self.request.recv(4096)
        if(len(recv) < 1):
            return

        data = json.loads(recv)
        if(data[0] == 'command'):

            if(data[1] == 'snapshot'):
                if(data[2] == 'remote'):
                    syslog.syslog('Taking snapshot...')
                    self.server.camera.snap('remote')
                    syslog.syslog('snapshot taken')
                    self.request.send('snapshot_ok')
                if(data[2] == 'motion'):
                    if(self.server.motionAcitivated):
                        syslog.syslog('Taking snapshot...')
                        self.server.camera.snap('motion')
                        syslog.syslog('snapshot taken')
                        self.request.send('snapshot_ok')
                    else:
                        self.request.send('snapshot_blocked')

            if(data[1] == 'motion'):
                if(data[2] == 'off'):
                    self.server.motionAcitivated = False
                    syslog.syslog('Motion detector disabled')
                    self.request.send('motion_off')
                if(data[2] == 'on'):
                    self.server.motionAcitivated = True
                    syslog.syslog('Motion detector enabled')
                    self.request.send('motion_on')

                syslog.syslog(str(self.server.motionAcitivated))

            if(data[1] == 'debug'):
                syslog.syslog('debug')

        return


if __name__ == "__main__":
    daemon = SecurityDaemon()
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)
