
import time
import hal
from threading import Thread
from hal_impl.data import hal_data


def talon_outputs():
    o = {}
    for chan in range(20):
        if hal_data['pwm'][chan]['type'] == 'talon':
            o[chan] = hal_data['pwm'][chan]['value']
        else:
            o[chan] = None
    return o

class PwmWatch(Thread):
    def __init__(self, output=None):
        Thread.__init__(self)
        self.output = output
        self.daemon = True
        self.start()

    def run(self):
        while True:
            time.sleep(0.05)
            outputs = talon_outputs()
            if self.output:
                # TODO: hook to micro maestro here
                pass
            else:
                for k, v in outputs.items():
                    if v != None:
                        print("chan {} output {}".format(k, v))
