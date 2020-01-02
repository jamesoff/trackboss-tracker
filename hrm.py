import datetime
import bluepy.btle as btle
import paho.mqtt.client as mqtt
import argparse
import json

packets = 0

class MyDelegate(btle.DefaultDelegate):
    def __init__(self):
        btle.DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        global packets 
        packets += 1

        global hr
        hr = str(data[1])

        global time
        time = datetime.datetime.now().time()
        print("time: {} packet: {} Handle: {} HR (bpm): {}".format(time, packets, cHandle, data[1]))

parser = argparse.ArgumentParser(description="Connect to Polar H10 HRM")
parser.add_argument('device', type=str, help='HRM strap device ID')

args = parser.parse_args()
print('args: {}'.format(args.device))

p = btle.Peripheral(args.device, addrType="random")
p.setDelegate(MyDelegate())

#start hr notification
service_uuid = 0x180D
svc = p.getServiceByUUID(service_uuid)
ch = svc.getCharacteristics()[0]
desc = ch.getDescriptors()[0]
desc.write(b"\x01\x00", True)

# MQTT
broker_url = "10.10.10.71"
broker_port = 1883

client = mqtt.Client()
client.connect(broker_url, broker_port)

# listen for notifications
while True:
    if p.waitForNotifications(1.0):
        payload = json.dumps({'time': str(time), 'heart_rate': hr})
        client.publish(topic="TrackBossHRM", payload=str(payload), qos=0, retain=False)
        continue