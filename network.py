#!/usr/bin/env python3
from inky import InkyPHAT
import socket


host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)

font = ImageFont.truetype("./inkyphat/fonts/MesloLGS_NF_Regular.ttf", 10)
fontsm = ImageFont.truetype("./inkyphat/fonts/MesloLGS_NF_Regular.ttf", 6)
fontlg = ImageFont.truetype("./inkyphat/fonts/MesloLGS_NF_Regular.ttf", 16)

inkyphat = InkyPHAT("red")

inkyphat.set_rotation(180)
inkyphat.set_colour("red")
inkyphat.set_border(inkyphat.BLACK)

inkyphat.text((6, 77), host_name, inkyphat.WHITE, font=font)
inkyphat.text((6, 87), host_ip, inkyphat.WHITE, font=font)

inkyphat.show()
