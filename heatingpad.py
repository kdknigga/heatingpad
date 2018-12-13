#!/usr/bin/env python3

import sys
import datetime
import time
import requests
import pywemo


TILT_COLOR = "RED"
TILTPI = "localhost:1880"

WEMO_NAME = "Fermentation Heat"

LOW_POINT = 77
HIGH_POINT = 78


my_wemo = None
wemo_devices = pywemo.discover_devices()


for device in wemo_devices:
    if device.name == WEMO_NAME:
        my_wemo = device


if not my_wemo:
    print("Wemo \"%s\" not found on network" % WEMO_NAME)
    sys.exit(1)


print("Found Wemo:")
print(" - name: %s" % my_wemo.name)
print(" - mac: %s" % my_wemo.mac)
print(" - serial: %s" % my_wemo.serialnumber)
print(" - ipaddress: %s" % my_wemo.host)


skip_count = 0

while True:

    try:
        tiltpi_request = requests.get("http://%s/data/%s.json" % (TILTPI, TILT_COLOR), timeout=10)
        tiltpi_request.raise_for_status()

    except Exception as e:
        skip_count = skip_count + 1
        print("Exception calling tiltpi: %s, skip_count: %d" % (str(e), skip_count))

    else:
        skip_count = 0
        temperature = tiltpi_request.json()["Temp"]
        timestamp = datetime.datetime.strptime(tiltpi_request.json()["formatteddate"], "%Y-%m-%d %H:%M:%S")
        
        timestamp_age = datetime.datetime.now() - timestamp

        print("Timestamp is %s old" % str(timestamp_age))
        print("Temperature is %d degrees" % temperature)
        
        if timestamp_age < datetime.timedelta(minutes=10):
            if temperature < LOW_POINT and not my_wemo.get_state():
                print("Too cold, turning heat on")
                my_wemo.on()
        
            elif temperature > HIGH_POINT and my_wemo.get_state():
                print("Too hot, turning heat off")
                my_wemo.off()
        else:
            # If we got to here, then the timestamp on tilt reading is too old
            # I'm going to say that too cold is better than too hot, so kill the heat
            try:
                print("Timestamp too old, turning heat off")
                my_wemo.off()
            except:
        	    # Asking to turn the switch off when it already is
        	    # will throw an exception.  I don't care right now.
                pass

    if skip_count > 5:
        try:
            print("skip_count is %d, turning heat off" % skip_count)
            my_wemo.off()
        except:
            pass
    
    time.sleep(60)


# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
