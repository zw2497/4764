import machine
from machine import *
import ssd1306
import time
import socket
import urequests as requests
import json

labels = ['c', 'o', 'l', 'u', 'm', 'b', 'i', 'a']
urllocation = "https://0hzikyemyj.execute-api.us-east-2.amazonaws.com/4764/4764"
flag = 0
data = {}
xdata = []
ydata = []
label = "null"
n = 0
counter = 0


def dp(d):
    if (d > 128):
        return d - 255
    return d

def do_connect():
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(b'sun', "12345678")
        # wlan.connect(b'Columbia University')
        while not wlan.isconnected():
            pass
            print('network config:', wlan.ifconfig())
do_connect()

def http_post(url, d):
    r = requests.post(url, data=json.dumps(d))
    return r.json()

def switchCcallback(p):
    time.sleep(0.1)
    global label
    global counter
    global n
    if p.value() == 1:
        if counter < len(labels):
            label = labels[counter]
            n = 0
            counter += 1
        else:
            counter = 0
            n = 0
            label = labels[counter]

def sendData():
    global label
    global xdata
    global ydata
    global n
    n = n + 1
    l = {
        "label": label,
        "n": n,
        "number": len(xdata),
        "content": {
            "data": {
                "x": xdata,
                "y": ydata
            }
        }

    }
    http_post(urllocation, l)
    xdata, ydata = [], []

def switchAcallback(p):
    global flag
    time.sleep(0.1)
    if p.value() == 1:
        flag = 1




switchA = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)
switchC = machine.Pin(2, machine.Pin.IN, machine.Pin.PULL_UP)
switchA.irq(trigger=machine.Pin.IRQ_RISING, handler=switchAcallback)
switchC.irq(trigger=machine.Pin.IRQ_RISING, handler=switchCcallback)

spi = machine.SPI(1, baudrate=2000000, polarity=1, phase=1)
cs = machine.Pin(15, machine.Pin.OUT)
cs.value(0)
spi.write(b'\x2d')
spi.write(b'\x2b')
cs.value(1)
cs.value(0)
spi.write(b'\x31')
spi.write(b'\x0f')
cs.value(1)

i2c = machine.I2C(-1, machine.Pin(5), machine.Pin(4))
oled = ssd1306.SSD1306_I2C(128, 32, i2c)



while True:
    x = 0
    y = 0
    sendstatus = "null"
    if (flag):
        cs.value(0)
        test1 = spi.read(5, 0xf2)
        cs.value(1)

        cs.value(0)
        test2 = spi.read(5, 0xf3)
        cs.value(1)

        cs.value(0)
        test3 = spi.read(5, 0xf4)
        cs.value(1)

        cs.value(0)
        test4 = spi.read(5, 0xf5)
        cs.value(1)

        x = dp(test2[1])
        y = dp(test4[1])

        xdata.append(x)
        ydata.append(y)
        sendstatus = "collect" + str(len(xdata)) + ' '+ ' ' + str(x) + ' ' + str(y)
        if (len(xdata) > 49):
            sendData()
            sendstatus = "send success"
            flag = 0
    oled.fill(0)
    oled.text(label, 0, 0)
    oled.text(sendstatus, 0, 20)
    oled.show()


