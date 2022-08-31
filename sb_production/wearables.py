#!/usr/bin/env python

import os
import socket
import sys
import time
import struct
import fcntl
import errno

class wearables_server_t(object):
    def __init__(self,debug=False,mcaddr='239.255.223.01',port=0xDF0D,demo=False):
        self.debug = debug
        self.mcaddr = mcaddr
        self.port = port
        self.demo = demo
        self.cnt_send = 0

        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((self.mcaddr, self.port))
        mreq = struct.pack("4sl", socket.inet_aton(self.mcaddr), socket.INADDR_ANY)
        self.s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        
    def send_msg(self,msg):
        MESSAGE = 0xDF0002
        elapsed = beat = hue_med = hue_dev = 0
        if type(msg) is tuple:
            msg_effect = msg[0]
            if msg[1] in ['fast']:
                elapsed = 2
            elif msg[1] in ['slow']:
                elapsed = 1
            else:
                pass
        elif type(msg) is list:
            raise
        else:
            msg_effect = msg
        print "TX   %-16s elapsed: %04d beat: %04d hue_med:%03d hue_dev:%03d" % (msg_effect, elapsed, beat, hue_med, hue_dev)
        frame = struct.pack("!I12s16sIIBB", MESSAGE, '', msg_effect, elapsed, beat, hue_med, hue_dev)
        self.s.sendto(frame, (self.mcaddr, self.port))
        self.cnt_send += 1
        
        
class wearables_client_t(object):
    def __init__(self,debug=False,mcaddr='239.255.223.01',port=0xDF0D,demo=False):
        self.debug = debug
        self.mcaddr = mcaddr
        self.port = port
        self.demo = demo
        self.cnt_recv = 0
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((self.mcaddr, self.port))
        mreq = struct.pack("4sl", socket.inet_aton(self.mcaddr), socket.INADDR_ANY)
        self.s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        if not self.demo:
            fcntl.fcntl(self.s,fcntl.F_SETFL, os.O_NONBLOCK)

    def get_msgs_nonblocking(self):
        msgs = None
        while True:
            try:
                data, addr = self.s.recvfrom(1024)
    	        (msgcode,
                 reserved,
                 effect,
                 elapsed,
                 beat,
                 hue_med,
                 hue_dev) = \
                     struct.unpack("!I12s16sIIBB", data)

                effect = effect.rstrip('\x00')
                if elapsed in [2]:
                    effect = (effect,'fast')
                elif elapsed in [1]:
                    effect = (effect,'slow')
                elif elapsed in [0]:
                    pass
                else:
                    print ('** Unexpected elapsed: {}'.format(elapsed))

                msg_rec = {
    	            'msgcode' : msgcode,
                    'reserved' : reserved,
                    'effect' : effect,
                    'elapsed' : elapsed,
                    'beat' : beat,
                    'hue_med' : hue_med,
                    'hue_dev' : hue_dev
                }
                if msgs is None:
                    msgs = []

                msgs.append(msg_rec)
                self.cnt_recv += 1
                
#    	        print "RX %s:%s   %-16s elapsed: %04d beat: %04d hue_med: %03d hue_dev: %03d" % (addr[0], addr[1], effect.rstrip('\0'), elapsed, beat, hue_med, hue_dev)
    	        print "RX %s:%s   %-16s elapsed: %04d beat: %04d hue_med: %03d hue_dev: %03d" % (addr[0], addr[1], effect, elapsed, beat, hue_med, hue_dev)
            except socket.error, e:
                if e.args[0] == errno.EWOULDBLOCK:
                    break
                elif e.args[0] == errno.EGAIN:
                    break
                else:
                    raise
            except Exception as err:
                print ('Error: {}'.format(err))
    	        #print "RX %d bytes, %s" % (len(data), err)
                break
            
        return msgs
    
if __name__ == "__main__":
    wearables_client = wearables_client_t(debug=False,demo=False)
    while True:
        msg = wearables_client.get_msg_nonblocking()
        if msg is not None:
            print ('msg: {}'.format(msg))
    
