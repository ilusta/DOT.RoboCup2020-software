import serial.tools.list_ports as serial_list

def getSerialDevices():
    return serial_list.comports(True)

def extractName(device):
    return device.device

def extractNames(devices):
    return [extractName(el) for el in devices]

def getSerialNames():
    return [extractName(el) for el in getDevices()]

def getSerialIds():
    return [el.pid for el in getDevices()]
