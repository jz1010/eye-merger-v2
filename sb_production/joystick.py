#!/usr/bin/python

from evdev import InputDevice, categorize, ecodes
import time
import random

class joystick_t(object):
    def __init__(self,joystick_dev='/dev/input/event1',debug=False):
        self.joystick_dev = joystick_dev
        self.debug = debug
        self.eye_direction_last = None
        self.last_joystick_event_time = 0
        try:
            print ('Called init joystick for device: {}'.format(self.joystick_dev))
            self.joystick = InputDevice(self.joystick_dev)
        except:
            self.joystick = None
            print ('joystick init failed')
            
        
        #self.name = self.joystick.get_name()
#       self.num_axes = self.joystick.get_numaxes()
#        self.num_buttons = self.joystick.get_numbuttons()
#        self.num_hats = self.joystick.get_numhats()
#        self.info()

        self.cnt_samples = 0
        self.buttons = {
            288: {'button': 'trigger'},
            289: {'button': '2'},
            290: {'button': '3'},
            291: {'button': '4'},            
            292: {'button': '5'},            
            293: {'button': '6'},            
            294: {'button': '7'},            
            295: {'button': '8'},            
            296: {'button': '9'},            
            297: {'button': '10'},            
            298: {'button': '11'},
            299: {'button': '12'}
        }
        
        total_range = 1024.0
        min_delta = total_range / 8.0
        self.range_hi = total_range
        self.range_lo = 0.0
        self.t_long_lo = total_range * 0.5 / 4.0
        self.t_long_hi = total_range * 3.5 / 4.0
        self.t_short_mid_lo = (total_range * 1.0 / 2.0) - min_delta
        self.t_short_mid_hi = (total_range * 1.0 / 2.0) + min_delta
        self.t_short_min = self.t_long_lo
        self.t_short_max = self.t_long_hi
        print ('t_long_lo: {} t_short_mid_lo: {} t_short_mid_hi: {} t_long_hi: {}'.format(
            self.t_long_lo,
            self.t_short_mid_lo,
            self.t_short_mid_hi,            
            self.t_long_hi))

        total_range = 255.0
        min_delta = total_range / 8.0        
        self.twist_range_hi = total_range
        self.twist_range_lo = 0.0
        self.twist_mid_lo = (total_range * 1.0 / 2.0) - min_delta
        self.twist_mid_hi = (total_range * 1.0 / 2.0) + min_delta
        print ('twist_range_lo: {} twist_mid_lo: {} twist_mid_hi: {} twist_range_hi: {}'.format(
            self.twist_range_lo,
            self.twist_mid_lo,
            self.twist_mid_hi,            
            self.twist_range_hi))
        self.twist_pattern = [('eye_southwest','fast'),
                              ('eye_down','fast'),
                              ('eye_southeast','fast'),
                              ('eye_right','fast'),                         
                              ('eye_northeast','fast'),
                              ('eye_up','fast'),                                                  
                              ('eye_northwest','fast'),
                              ('eye_left','fast'),
        ]

        self.center_pattern = [('eye_center','fast')]
        self.twist_pattern_cclockwise = [ \
            self.center_pattern + \
            self.twist_pattern + \
            self.center_pattern
        ]
        
        self.twist_pattern_clockwise = [ \
            self.center_pattern + \
            self.twist_pattern[::-1] + \
            self.center_pattern
        ]
        
        self.sample_interval = 2.00 # secs
        self.time_last_sample = 0

    def info(self):
        print ('joystick: {}'.format(self.joystick))
        print( "Number of axes: {}".format(self.num_axes) )
        print( "Number of buttons: {}".format(self.num_buttons) )
        print( "Number of hats: {}".format(self.num_hats) )

    def get_status(self):
        return (self.joystick is not None)

    def opt_eye_event_queue(self,events):
        
        return events

    def sample_nonblocking(self):
        gecko_events = []
        if self.joystick is None:
            return gecko_events

        sample = False
        events = []
        while True:
            try:
                event = self.joystick.read_one()
            except:
                self.joystick = None
                event = None
                
            if event is None:
                break
            events.append(event)
            
        for event in events:
            if event.type in [ecodes.EV_KEY]:
                if event.code not in self.buttons:
                    continue # unhandled event

                button_name = self.buttons[event.code]['button']
                button_val = event.value
                print ('button: {} state: {}'.format(button_name,button_val))
                if button_name in ['trigger']:
                    gecko_events.append('blink')
                elif button_name in ['2']:
                    #event = ('eye_center','fast')
                    event = ('eye_center','slow')                    
                    gecko_events.append(event)
                elif button_name in ['3']:
                    if button_val in [0]: # release
                        continue
                    crazy_pattern = self.twist_pattern
                    random.shuffle(crazy_pattern)                    
                    crazy_pattern += self.center_pattern
                    gecko_events += [crazy_pattern]
                elif button_name in ['9']:
                    gecko_events.append('eye_context_9')                    
                elif button_name in ['11']:
                    gecko_events.append('eye_context_11')                    
                elif button_name in ['12']:
                    gecko_events.append('eye_context_12')
                else:
                    pass
            elif event.type in [ecodes.EV_ABS]: # stick handle
                eye_direction = None
                eye_movement_rate = None
                if self.debug:
                    #print ('analog value: {}'.format(event.value))
                    pass
                if event.code in [0]: # stick left/right
                    if self.debug:
                        print ('Stick left/right, ABS_0: {}'.format(event))
                    if event.value < self.t_short_mid_lo and event.value > self.t_short_min:
                        # soft left
                        eye_direction = 'eye_left'
                        eye_movement_rate = 'slow'
                    elif event.value <= self.t_long_lo and event.value >= self.range_lo:
                        # hard left
                        eye_direction = 'eye_left'
                        eye_movement_rate = 'fast'
                    elif event.value >= self.t_short_mid_hi and event.value < self.t_short_max:
                        # soft right
                        eye_direction = 'eye_right'
                        eye_movement_rate = 'slow'                        
                    elif event.value >= self.t_long_hi and event.value <= self.range_hi:
                        # hard right
                        eye_direction = 'eye_right'
                        eye_movement_rate = 'fast'
                    else:
                        if self.debug:
                            print ('No decode left/right for val: {}'.format(event.value))
                            print ('t_long_lo: {} t_short_mid_lo: {} t_short_mid_hi: {} t_long_hi: {}'.format(
                                self.t_long_lo,
                                self.t_short_mid_lo,
                                self.t_short_mid_hi,            
                                self.t_long_hi))
                        
                        
                elif event.code in [1]: # stick forward/back
                    if self.debug:
                        print ('Stick forward/back ABS_1: {}'.format(event))
                    if event.value < self.t_short_mid_lo and event.value > self.t_short_min:
                        eye_direction = 'eye_up'
                        eye_movement_rate = 'slow'
                    elif event.value <= self.t_long_lo and event.value >= self.range_lo:
                        # hard forward
                        eye_direction = 'eye_up'
                        eye_movement_rate = 'fast'
                    elif event.value >= self.t_short_mid_hi and event.value < self.t_short_max:
                        # soft back
                        eye_direction = 'eye_down'
                        eye_movement_rate = 'slow'
                    elif event.value >= self.t_long_hi and event.value <= self.range_hi:
                        # hard back
                        eye_direction = 'eye_down'
                        eye_movement_rate = 'fast'
                    else:
                        if self.debug:
                            print ('No decode back/forward for val: {}'.format(event.value))
                            print ('t_long_lo: {} t_short_mid_lo: {} t_short_mid_hi: {} t_long_hi: {}'.format(
                                self.t_long_lo,
                                self.t_short_mid_lo,
                                self.t_short_mid_hi,            
                                self.t_long_hi))
                        
                elif event.code in [5]: # stick twist
                    #print ('ABS_5: {}'.format(event.value))
                    if event.value >= self.twist_range_lo and \
                       event.value <= self.twist_mid_lo:
                        #twist_pattern = self.twist_pattern_cclockwise
                        twist_pattern = None
                    elif event.value <= self.twist_range_hi and \
                         event.value >= self.twist_mid_hi:
                        #twist_pattern = self.twist_pattern_clockwise
                        twist_pattern = None
                    else: # Outside ranges
                        pass
                        twist_pattern = None

                    if twist_pattern is not None:
                        # Time-based sampling for twist control
                        time_now =  time.time()
                        if time_now < self.time_last_sample + self.sample_interval:
                            continue

                        self.time_last_sample = time_now
                        
                        print ('twist_pattern: {}'.format(twist_pattern))
                        gecko_events += twist_pattern
                    
                elif event.code in [17]: # Hat forward/back
                    if event.value in [-1]: # hat forward
                        gecko_events.append('pupil_widen')
                    elif event.value in [0]: # hat middle
                        pass
                    elif event.value in [1]: # hat back
                        gecko_events.append('pupil_narrow')                        
                    else:
                        raise
                elif event.code in [16]: # Hat left/right
                    if event.value in [-1]: # hat left
                        pass
                    elif event.value in [0]: # hat middle
                        pass
                    elif event.value in [1]: # hat right
                        pass
                    else:
                        raise
                else:
                    print ('Analog unhandled event: {}'.format(event))

                # Refine eye position
                if self.debug:
                    print ('last_position: {} eye_position: {}'.format(self.eye_direction_last,
                                                                       eye_direction))
                if eye_direction is not None:
                    if self.eye_direction_last in ['eye_up']:
                        if eye_direction in ['eye_right'] and \
                           eye_movement_rate in ['fast']:
                            eye_direction = 'eye_northeast'
                        elif eye_direction in ['eye_left'] and \
                           eye_movement_rate in ['fast']:
                            eye_direction = 'eye_northwest'
                    elif self.eye_direction_last in ['eye_down']:
                        if eye_direction in ['eye_right'] and \
                           eye_movement_rate in ['fast']:
                            eye_direction = 'eye_southeast'
                        elif eye_direction in ['eye_left']:
                            eye_direction = 'eye_southwest'
                    elif self.eye_direction_last in ['eye_left']:
                        if eye_direction in ['eye_up'] and \
                           eye_movement_rate in ['fast']:
                            eye_direction = 'eye_northwest'
                        elif eye_direction in ['eye_down']:
                            eye_direction = 'eye_southwest'
                    elif self.eye_direction_last in ['eye_right']:
                        if eye_direction in ['eye_up'] and \
                           eye_movement_rate in ['fast']:                           
                            eye_direction = 'eye_northeast'
                        elif eye_direction in ['eye_down'] and \
                             eye_movement_rate in ['fast']:                             
                            eye_direction = 'eye_southeast'
                    elif self.eye_direction_last in ['eye_northeast']:
                        if eye_direction in ['eye_up','eye_right']:
                            eye_direction = 'eye_northeast'
                    elif self.eye_direction_last in ['eye_northwest']:
                        if eye_direction in ['eye_up','eye_left']:
                            eye_direction = 'eye_northwest'
                    elif self.eye_direction_last in ['eye_southwest']:
                        if eye_direction in ['eye_down','eye_left']:
                            eye_direction = 'eye_southwest'
                    elif self.eye_direction_last in ['eye_southeast']:
                        if eye_direction in ['eye_down','eye_right']:
                            eye_direction = 'eye_southeast'
                    elif self.eye_direction_last is None:
                        pass
                    else:
                        pass

                    assert (eye_direction is not None)
                    if eye_direction in ['eye_southeast',
                                         'eye_southwest',
                                         'eye_northeast',
                                         'eye_northheast']:
                        pass
                        #continue

                    # Add event
                    event = (eye_direction,eye_movement_rate)
                    gecko_events.append(event)

                    # Prepare for next event
                    self.eye_direction_last = eye_direction
            elif event.type in [0]: # UNKNOWN
                pass
            elif event.type in [4]: # UNKNOWN - maybe relates to button press
                pass
            else:
                print ('Unhandled event type: {}'.format(event.type))

        gecko_events = self.opt_eye_event_queue(gecko_events)

        if len(gecko_events) > 0:
            self.last_joystick_event_time = time.time()
        
        return gecko_events

    def get_last_joystick_time(self):
        return self.last_joystick_event_time
    
    def shutdown(self):
        pass
        
if __name__ in "__main__":
    joystick = joystick_t(debug=True)
    while True:
        gecko_events = joystick.sample_nonblocking()
        for event in gecko_events:
            print ('event: {}'.format(event))
