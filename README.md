# heatingpad
This is a python script to control an electric heating pad (via a [WeMo Switched Smart Plug](https://belkin.com/us/support-product?pid=01t80000002xFCbAAM)) based on the temperature reported by a [Tilt hydrometer](https://tilthydrometer.com/) (via a [TiltPi](https://tilthydrometer.com/blogs/news/introducing-tilt-pi-an-sd-card-image-download-for-your-raspberry-pi-3-or-zero-w)).  The idea is to keep a fermentation vessel at a steadyish, warmer-than-room temperature.

The script is intended to run on the TiltPi, but could run on another device.  Also, this script requires **no** internet access (after the initial repo cloning and requirements installation) and interacts with both the Tilt/TiltPi and the WeMo plug directly without any intermediary cloud service.


## Getting Started
Parts required:
* WeMo plug
* Simple heating pad that turns on with power application ([perhaps like this](https://www.prairie-essentials.com/collections/home-and-garden/products/prairie-essentials-3-x-20-strip-wrap-around-heating-pad-warming-heat-mat-thermometer-for-kombucha-tea-beer-brewing-plant-fermentation-seedlings-plant-germination))
* A Raspberry Pi (or similar) running TiltPi
* A Tilt hydrometer
* Some liquid/yeast mixture that you want to ferment in a container

First, plug your WeMo plug into an outlet and get it joined to your wireless LAN.  You'll either need to name it, or note the default name.

Second, configure your TiltPi installation so it's on your LAN and can read values from your Tilt.

Next, clone this repo onto the device that will be running the script (probably the TiltPi device), `pip install` the requirements, and adjust the config file to match your setup.  At a minimum you'll probably need to set the correct Tilt color, WeMo name, and target temperature.

Now, arrange your heating pad so that it will effectively heat your fermentation vessel.  I wrap my pad around my fermenter, but how you do it probably depends on your pad and your fermenter.  Also, plug the pad into the WeMo plug.

Drop your sterilized Tilt into your fermenter and verify TiltPi can get readings from it.

Finally, start the script, either via the soon-to-be included systemd unit file or via a detachable terminal multiplexer such as tmux or screen.  The script will try to maintain the desired temperature by cycling the power to the heating pad on and off.

## Thoughts
This script assumes that too cool is better than too hot.  Too cool can mean slow fermentation, but too hot can mean cooked yeast!  If it goes more than 10 minutes (by default) without getting an updated temperature it will turn the heat off.  If the TiltPi software stops responding it will turn the heat off.  Basically, if anything goes wrong it turns the heat off.

When run as a systemd service, log messages get sent to syslog.

I've only tested this with an old-style WeMo Switched Smart Plug, as that's what I have.  I think it should work with the newer plugs, though.

