import socket
import logging 
import struct
import sys

import weewx
from weewx.engine import StdService
import weewx.units
from weeutil.weeutil import to_int
weewx.units.obs_group_dict['soilTemp3'] = 'group_energy'

VERSION = "0.2"

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
        syslog.syslog(level, 'Luxtronik: %s' % msg)

    def logdbg(msg):
        logmsg(syslog.LOG_DEBUG, msg)

    def loginf(msg):
        logmsg(syslog.LOG_INFO, msg)

    def logerr(msg):
        logmsg(syslog.LOG_ERR, msg)

class Luxtronik(StdService):
    def __init__(self, engine, config_dict):
        super(Luxtronik, self).__init__(engine, config_dict)
        loginf("service version is %s" % VERSION)

        self.bind(weewx.NEW_ARCHIVE_RECORD, self.new_archive_record)

        self.last_total_energy = None

        # Extract our stanza from the configuration dictionary
        l_dict = config_dict.get('Luxtronik', {})

        # Extract stuff out of the resultant dictionary
        self.port = to_int(l_dict.get('port', 8889))
        self.host = l_dict.get('host', '192.168.201.40')

        loginf("heatpump %s:%s" % (self.host, self.port))

    def connect(self):
        self.connection_alive = True

        try:
            self.hp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.hp.settimeout(2)
            self.hp.connect((self.host, self.port))
        except socket.error as e:
            logerr("Error: connection failed {}".format(e))
            self.hp.close()
            self.connection_alive = False

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
        
        if self.connection_alive:
            self.get_calculated()

            net_energy_consumed = None

            energy_heating   = float(self.calculated[151]) / 10  # Energy output for heating
            energy_hot_water = float(self.calculated[152]) / 10  # Energy output for domestic hot water

            total_energy = energy_heating + energy_hot_water

            logdbg("total_energy %s" % total_energy)

            if self.last_total_energy:
                net_energy_consumed = total_energy - self.last_total_energy
                event.record['soilTemp3'] = net_energy_consumed
                loginf("Calculated energy consumed %.2f kW/h" % net_energy_consumed)

            self.last_total_energy = total_energy
        else:
            logerr("No connection to heatpump")
