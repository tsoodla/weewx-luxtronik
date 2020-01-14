import socket
import logging 
import struct
import sys

import weewx
from weewx.engine import StdService
import weewx.units
weewx.units.obs_group_dict['soilTemp3'] = 'group_energy'

try:
    # Test for new-style weewx logging by trying to import weeutil.logger
    import weeutil.logger
    import logging
    log = logging.getLogger(__name__)

    def logdbg(msg):
        log.debug(msg)

    def loginf(msg):
        log.info(msg)

    def logerr(msg):
        log.error(msg)

except ImportError:
    # Old-style weewx logging
    import syslog

    def logmsg(level, msg):
        syslog.syslog(level, 'luxtronik: %s:' % msg)

    def logdbg(msg):
        logmsg(syslog.LOG_DEBUG, msg)

    def loginf(msg):
        logmsg(syslog.LOG_INFO, msg)

    def logerr(msg):
        logmsg(syslog.LOG_ERR, msg)

class Luxtronik(StdService):
    def __init__(self, engine, config_dict):

        super(Luxtronik, self).__init__(engine, config_dict)
        self.bind(weewx.NEW_ARCHIVE_RECORD, self.new_archive_record)

        self.last_total_energy = None

        try:
            self.host = config_dict['Luxtronik'].get('host')
            self.port = config_dict['Luxtronik'].get('port')

            loginf("host %s:%s" % self.host, self.port)

        except KeyError as e:
            logerr("Missing parameter {}".format(e))

    def connect(self):
        try:
            self.hp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.hp.settimeout(2)
            self.hp.connect((self.host, int(self.port)))
        except socket.error as e:
            logerr("Error: connection failed {}".format(e))
            self.hp.close()

    def get_calculated(self):
        self.calculated = []

        request = struct.pack('!ii', 3004, 0)
        self.hp.send(request)
        data = self.hp.recv(4)
        response = struct.unpack('!i', data)
        if response[0] != 3004:
            logerr("Error in 3004, invalid response")
            return
        data = self.hp.recv(4)
        struct.unpack('!i', data)[0]
        data = self.hp.recv(4)
        length = struct.unpack('!i', data)[0]
        for i in range(0, length):
            data = self.hp.recv(4)
            self.calculated.append(struct.unpack('!i',data)[0])
        self.hp.close()
    
    def new_archive_record(self, event):
        self.connect()
        self.get_calculated()

        net_energy_consumed = None

        # Available variables: https://www.loxwiki.eu/display/LOX/Java+Webinterface
        energy_heating   = float(self.calculated[151]) / 10
        energy_hot_water = float(self.calculated[152]) / 10

        total_energy = energy_heating + energy_hot_water

        logdbg("total_energy %s" % total_energy)

        if self.last_total_energy:
            net_energy_consumed = total_energy - self.last_total_energy
            event.record['soilTemp3'] = net_energy_consumed

        self.last_total_energy = total_energy


