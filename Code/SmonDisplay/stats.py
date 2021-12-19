from threading import Thread
import time
import socket

import psutil
from uptime import uptime


class SmonStats:
    """Funkcja wyciąga parametry systemu, zapisuje je i zwraca pojedynczo"""

    smonStats = {}

    def disp_uptime(self):
        """Gets host uptime and return it in formated way"""
        try:
            uptime_now = uptime()
            # print (uptimeNow//60)
            disp_uptime = ""
            if uptime_now // 60 < 60:  # mins
                disp_uptime = str(round(uptime_now // 60)) + "m"
            elif uptime_now // 60 // 60 < 24:  # hours
                disp_uptime = (
                    str(round(uptime_now // 60 // 60))
                    + "h "
                    + str(round(uptime_now // 60 % 60))
                    + "m"
                )
            elif uptime_now // 60 // 60 // 24 < 365:  # days
                disp_uptime = (
                    str(round(uptime_now // 60 // 60 // 24))
                    + "d "
                    + str(round(uptime_now // 60 // 60 % 24))
                    + "h"
                )
            else:
                disp_uptime = str(round(uptime_now // 60 // 60 // 24)) + "d "
            return disp_uptime
        except Exception as ex:
            # logging.exception(str(ex))
            print("SmonStats.disp_uptime error:", str(ex))

    def update_stats(self, startOnce=True, refresh_rate=5):
        try:
            while True:

                self.smonStats["hostname"] = socket.gethostname()
                self.smonStats["uptime"] = self.disp_uptime()

                self.smonStats["ip"] = psutil.net_if_addrs()["eth0"][0][1]
                self.smonStats["netmask"] = psutil.net_if_addrs()["eth0"][0][2]
                self.smonStats["mac"] = psutil.net_if_addrs()["eth0"][2][1]

                self.smonStats["cpuTotal"] = str(psutil.cpu_percent()) + "%"
                self.smonStats["cpuUser"] = str(psutil.cpu_times_percent()[0]) + " %"
                self.smonStats["cpuSystem"] = str(psutil.cpu_times_percent()[2]) + " %"

                self.smonStats["diskTotal"] = (
                    str(round(psutil.disk_usage("/")[0] / 1024 / 1024 / 1024)) + " GB"
                )
                self.smonStats["diskUsed"] = (
                    str(round(psutil.disk_usage("/")[1] / 1024 / 1024 / 1024)) + " GB"
                )
                self.smonStats["diskAvailable"] = (
                    str(round(psutil.disk_usage("/")[2] / 1024 / 1024 / 1024)) + " GB"
                )

                self.smonStats["totalMemory"] = (
                    str(round(psutil.virtual_memory()[0] / 1024 / 1024)) + " MB"
                )
                self.smonStats["usedMemory"] = (
                    str(round(psutil.virtual_memory()[3] / 1024 / 1024)) + " MB"
                )
                self.smonStats["availableMemory"] = (
                    str(round(psutil.virtual_memory()[1] / 1024 / 1024)) + " MB"
                )

                self.smonStats["totalSwap"] = (
                    str(round(psutil.swap_memory()[0] / 1024 / 1024)) + " MB"
                )
                self.smonStats["usedSwap"] = (
                    str(round(psutil.swap_memory()[1] / 1024 / 1024)) + " MB"
                )
                self.smonStats["availableSwap"] = (
                    str(round(psutil.swap_memory()[2] / 1024 / 1024)) + " MB"
                )

                time.sleep(refresh_rate)
                if startOnce:
                    break
        except Exception as ex:
            # logging.exception(str(ex))
            print("SmonStats.update_stats error:", str(ex))

    def __init__(self):
        self.update_stats(True, 0)

    def get_stat(self, stat):
        try:
            return self.smonStats[stat]
        except Exception as ex:
            # logging.exception(str(ex))
            print("SmonStats.get_stat error:", str(ex))

    def auto_refresh_stats(self, refresh_rate=5):
        try:
            statThread = Thread(target=self.update_stats, args=(False, refresh_rate))
            statThread.start()

        except Exception as ex:
            # logging.exception(str(ex))
            print("SmonStats.auto_refresh_stats error:", str(ex))


"""



smon = SmonStats()
# smon.update_stats()
smon.auto_refresh_stats(3)
print('tutaj')
while True:

	print(smon.get_stat('uptime'))
	print(smon.get_stat('ip'))
	time.sleep(1)

"""
