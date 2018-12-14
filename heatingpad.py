#!/usr/bin/env python3

import sys
import datetime
import time
import requests
import pywemo


class heatingpad(object):
    def __init__(self, TILT_COLOR, TILTPI_HOST, TILTPI_PORT, WEMO_NAME, SETPOINT):
        self.tilt_color = TILT_COLOR
        self.tiltpi_host = TILTPI_HOST
        self.tiltpi_port = TILTPI_PORT
        self.wemo_name = WEMO_NAME
        self.setpoint = SETPOINT

        self.wemo = None

        wemo_devices = pywemo.discover_devices()

        for device in wemo_devices:
            if device.name == WEMO_NAME:
                self.wemo = device

        if not self.wemo:
            print("Wemo \"%s\" not found on network" % self.wemo_name)
            sys.exit(1)

        print("Found Wemo: %s | mac: %s | serial: %s | ipaddress: %s".format(
            self.wemo.name,
            self.wemo.mac,
            self.wemo.serialnumber,
            self.wemo.host
        ))

    def main_loop(
            self,
            LOOP_DELAY_SECONDS=60,
            MAX_TIMESTAMP_MINTUES=10,
            MAX_CONSECUTIVE_TILTPI_FAILURES=5,
            MAX_SETPOINT_DEVIATION=1
    ):

        skip_count = 0
        LOW_POINT = self.setpoint - MAX_SETPOINT_DEVIATION
        HIGH_POINT = self.setpoint + MAX_SETPOINT_DEVIATION

        while True:

            try:
                tiltpi_request = requests.get("http://%s:%s/data/%s.json".format(
                    self.tiltpi_host,
                    self.tiltpi_port,
                    self.tilt_color
                ), timeout=10)
                tiltpi_request.raise_for_status()

            except Exception as e:
                skip_count = skip_count + 1
                print("Exception calling tiltpi: %s, skip_count: %d" % (str(e), skip_count))

            else:
                skip_count = 0
                temperature = tiltpi_request.json()["Temp"]
                timestamp = datetime.datetime.strptime(tiltpi_request.json()["formatteddate"], "%Y-%m-%d %H:%M:%S")

                timestamp_age = datetime.datetime.now() - timestamp

                if self.wemo.get_state():
                    switch_state_message = "Heat is on"
                else:
                    switch_state_message = "Heat is off"

                temp_age_message = "Timestamp is %s old" % str(timestamp_age)
                temp_val_message = "Temperature is %d degrees" % temperature

                switch_action_message = "No action taken at this time"
                if timestamp_age < datetime.timedelta(minutes=MAX_TIMESTAMP_MINTUES):
                    if temperature < LOW_POINT and not self.wemo.get_state():
                        switch_action_message = "Too cold, turning heat on"
                        self.wemo.on()

                    elif temperature > HIGH_POINT and self.wemo.get_state():
                        switch_action_message = "Too hot, turning heat off"
                        self.wemo.off()
                else:
                    # If we got to here, then the timestamp on tilt reading is too old
                    # I'm going to say that too cold is better than too hot, so kill the heat
                    try:
                        switch_action_message = "Timestamp too old, turning heat off"
                        self.wemo.off()
                    except:
                        # Asking to turn the switch off when it already is
                        # will throw an exception.  I don't care right now.
                        pass

            if skip_count > MAX_CONSECUTIVE_TILTPI_FAILURES:
                try:
                    switch_action_message = "skip_count is %d, turning heat off" % skip_count
                    self.wemo.off()
                except:
                    pass

            print("%s | %s | %s | %s".format(
                temp_age_message,
                temp_val_message,
                switch_state_message,
                switch_action_message
            ))
            time.sleep(LOOP_DELAY_SECONDS)


if __name__ == "__main__":
    import argparse
    import configparser

    argparser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config-file", default="/dev/null", help="Path to the config file")
    args = parser.parse_args()

    configfile = configparser.ConfigParser()
    configfile["DEFAULT"] = {"Tilt_Color": "RED",
                             "TiltPi_Host": "localhost",
                             "TiltPi_Port": "1880",
                             "WeMo_Switch_Name": "Fermentation Heat",
                             "Setpoint_Temperature": 78}
    configfile.read(args.config_file)

    if "heatingpad" not in configfile:
        configfile["heatingpad"] = {}

    heatingpadconfig = configfile["heatingpad"]

    tilt_color = heatingpadconfig["Tilt_Color"]
    tiltpi_host = heatingpadconfig["TiltPi_Host"]
    tiltpi_port = heatingpadconfig["TiltPi_Port"]
    wemo_name = heatingpadconfig["WeMo_Switch_Name"]
    setpoint = heatingpadconfig["Setpoint_Temperature"]

    heatingpad = heatingpad(
        TILT_COLOR=tilt_color,
        TILTPI_HOST=tiltpi_host,
        TILTPI_PORT=tiltpi_port,
        WEMO_NAME=wemo_name,
        SETPOINT=setpoint
    )

    heatingpad.main_loop()



# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
