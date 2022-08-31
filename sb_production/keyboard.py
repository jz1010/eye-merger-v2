#!/usr/bin/python

from evdev import InputDevice, ecodes
from select import select

class keyboard_t(object):
    def __init__(self,keyboard_dev='/dev/input/event0',debug=False):
        self.keyboard_dev = keyboard_dev
        self.debug = debug
        try:
            print('Called init_keyboard for device: {}'.format(self.keyboard_dev))
            self.keyboard = InputDevice(self.keyboard_dev)
            self.devices = [self.keyboard]
            self.devices = {dev.fd: dev for dev in self.devices}
        except:
            self.keyboard = None
            print ('keyboard init failed')


    def info(self):
        print ('keyboard: {}'.format(self.keyboard))

    def get_status(self):
        return (self.keyboard is not None)
        
    def sample(self):
        events = []
        if self.keyboard is not None:
            r,w,x = select(self.devices,[],[], 0)

            for fd in r:
                try:
                    for event in self.devices[fd].read():
                        if event.type == ecodes.EV_KEY:
                            print ('event: {}'.format(event))
                            events.append(event)
                except:
                    self.keyboard = None
                    
        return events

    def shutdown(self):
        pass
        
if __name__ in "__main__":
    keyboard = keyboard_t(debug=True)
    keyboard.info()
    while True:
        events = keyboard.sample()
        for event in events:
            print ('event: {}'.format(event))
            
            
