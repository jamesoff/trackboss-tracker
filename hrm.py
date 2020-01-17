#!/usr/bin/env python3
import argparse
import json
import logging
import re
import subprocess
import sys
import time

import bluepy.btle as btle
import paho.mqtt.client as mqtt


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
        logging.debug(
            "epoch_time: %f packet: %d Handle: %d HR (bpm): %s",
            self.epoch_time,
            self.packets,
            cHandle,
            self.hr,
        )


logger = logging.Logger("hrm")
parser = argparse.ArgumentParser(description="Connect to Polar H10 HRM")
parser.add_argument("device", type=str, help="HRM strap device ID")
parser.add_argument(
    "debug", action="store_true", default=False, help="enable debug logging"
)

args = parser.parse_args()
if args.debug:
    logger.setLevel(logging.DEBUG)

logger.debug("args: %s", args.device)

p = btle.Peripheral(args.device, addrType="random")
delegate = MyDelegate()
p.setDelegate(delegate)

# start hr notification
service_uuid = 0x180D
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
        logging.debug("payload: %s", payload)

        try:
            client.publish(topic="TrackBossHRM", payload=payload, qos=0, retain=False)
        except Exception:
            logging.exception("Failed to publish message to MQTT")

        if not connection_flag:
            # Get the connection handle
            try:
                output = subprocess.run(["hcitool", "con"], capture_output=True)
            except Exception:
                logging.exception("Failed to run hcitool con")
                #  Bail since we can't continnue
                sys.exit(1)
            connection_output = re.compile(r"(handle\s)(\d\d)").split(
                str(output.stdout)
            )
            try:
                connection_handle = connection_output[2]
            except IndexError:
                logging.critical("Failed to parse hcitool con output")
                sys.exit(1)

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
                logging.critical("Error with amending the connection settings.")
                sys.exit(1)
            else:
                connection_flag = True
