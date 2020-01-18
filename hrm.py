#!/usr/bin/env python3
import sys
import time
import bluepy.btle as btle
import paho.mqtt.client as mqtt
import argparse
import json
import subprocess
import re


class MyDelegate(btle.DefaultDelegate):
    def __init__(self):
        btle.DefaultDelegate.__init__(self)
        self.hr = None
        self.epoch_time = None
        self.packets = 0

    def handleNotification(self, cHandle, data):
        self.packets += 1
        self.hr = str(data[1])
        self.epoch_time = time.time()
        # print("epoch_time: {} packet: {} Handle: {} HR (bpm): {}".format(epoch_time, packets, cHandle, data[1]))


parser = argparse.ArgumentParser(description="Connect to Polar H10 HRM or RUN device")
parser.add_argument("--device", "-d", type=str, help="Device ID", required=True)
parser.add_argument("--type", "-t", type=str, help="HRM or RUN", default="HRM")

args = parser.parse_args()
print("args.device: {}".format(args.device))
print("args.type: {}".format(args.type))

p = btle.Peripheral(args.device, addrType="random")
delegate = MyDelegate()
p.setDelegate(delegate)

# start hr notification
if args.type.lower() == "run":
    # TODO - Implement support for running data
    service_uuid = 0x1814   # Running speed and cadence
                            # https://www.bluetooth.com/wp-content/uploads/Sitecore-Media-Library/Gatt/Xml/Services/org.bluetooth.service.running_speed_and_cadence.xml
else:
    service_uuid = 0x180D   # Heart Rate
                            # https://www.bluetooth.com/wp-content/uploads/Sitecore-Media-Library/Gatt/Xml/Services/org.bluetooth.service.heart_rate.xml

svc = p.getServiceByUUID(service_uuid)
ch = svc.getCharacteristics()[0]
desc = ch.getDescriptors()[0]
desc.write(b"\x01\x00", True)

# MQTT
broker_url = "localhost"
broker_port = 1883

client = mqtt.Client()
client.connect(broker_url, broker_port)

# Bluetooth Connection hack flag
connection_flag = False

# listen for notifications
while True:
    if p.waitForNotifications(1.0):
        localtime = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime(delegate.epoch_time)
        )
        payload = json.dumps(
            {
                "time": str(localtime),
                "epoch": str(delegate.epoch_time),
                "heart_rate": delegate.hr,
            }
        )
        print("payload: {}".format(payload))

        client.publish(topic="TrackBossHRM", payload=str(payload), qos=0, retain=False)

        if connection_flag == False:
            # Get the connection handle
            output = subprocess.run(["hcitool", "con"], capture_output=True)
            connection_output = re.compile(r"(handle\s)(\d\d)").split(
                str(output.stdout)
            )
            connection_handle = connection_output[2]

            # Run command to prevent bluetooth barfing
            # sudo hcitool lecup --handle 64 --min 250 --max 400 --latency 0 --timeout 600
            output = subprocess.run(
                [
                    "sudo",
                    "hcitool",
                    "lecup",
                    "--handle",
                    connection_handle,
                    "--min",
                    "250",
                    "--max",
                    "400",
                    "--latency",
                    "0",
                    "--timeout",
                    "600",
                ],
                capture_output=True,
            )

            if output.returncode:
                #  Script will barf anyway
                print("Error with amending the connection settings.")
                sys.exit()
            else:
                connection_flag = True

        continue
