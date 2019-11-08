# -*- coding: utf-8 -*-

import sys
import vxi11
from pylink import TCPLink
import serial
from .prologix import Prologix


class Device(object):
    com = None
    trm = '\r\n'
    connection_type = None
    host = None
    port = None

    def __init__(self, connection_type, host, port):
        self.connection_type = connection_type
        self.host = host
        self.port = port

        if (connection_type == 'serial'):
            self.com = TCPLink(host, port)
        elif (connection_type == 'lan'):
            self.com = TCPLink(host, port)
        elif (connection_type == 'gpib'):
            sPort = 'gpib0,%i' % port
            self.com = vxi11.Instrument(host, sPort)
        elif (connection_type == 'gpibSerial'):
            sPort = 'COM1,488'
            self.com = vxi11.Instrument(host,sPort)
            #This probably will solely work with Keysight E5810B
        elif (connection_type == 'usb'):
            self.com = serial.Serial(host, 9600)
        elif (connection_type == 'prologix'):
            self.com = Prologix(host, port)
            self.com.open()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def open(self):
        self.com.open()

    def close(self):
        self.com.close()

    def reconnect(self):
        self.close()
        self.open()

    def read(self):
        try:
            if self.connection_type == 'usb':
                s = self.com.readline()
                s = s.decode()
            else:
                s = self.com.read()
        except:
            print('First reading attempt failed on "{}", trying again...'.format(type(self).__name__))
            try:
                if self.connection_type == 'usb':
                    s = self.com.readline()
                    s = s.decode()
                else:
                    s = self.com.read()
            except:
                print('Timeout while reading from "{}"!'.format(type(self).__name__))
                raise
        s = s.replace('\r', '')
        s = s.replace('\n', '')
        return s

    def write(self, cmd):
        cmd = cmd + self.trm
        if self.connection_type == 'usb':
            cmd = cmd.encode()
        try:
            self.com.write(cmd)
        except:
            self.reconnect()
            try:
                self.com.write(cmd)
            except:
                print('Timeout while writing to "{}"!'.format(type(self).__name__))
                raise

    def ask(self, cmd):
        self.write(cmd)
        return self.read()

    def printOutput(self, string):
        sys.stdout.write(string+'\r\n')
