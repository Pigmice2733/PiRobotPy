import time
from threading import Thread
from hal_impl.data import hal_data


def talon_outputs():
    pwm_values = {}
    for chan in range(20):
        if hal_data['pwm'][chan]['type'] == 'talon':
            pwm_values[chan] = hal_data['pwm'][chan]['value']
        else:
            pwm_values[chan] = None
    return pwm_values


class PwmWatch(Thread):
    def __init__(self, pwm_output=None):
        Thread.__init__(self)
        self.pwm_output = pwm_output
        self.daemon = True
        self.start()

    def run(self):
        while True:
            time.sleep(0.05)
            pwm_values = talon_outputs()
            if self.pwm_output:
                for channel, value in pwm_values.items():
                    if value is not None:
                        self.pwm_output.set_pwm_output(channel, value)
                pass
            else:
                # For printing we don't need as fast an update cycle
                time.sleep(0.45)
                for channel, value in pwm_values.items():
                    if value is not None:
                        print("Channel: {}  Value: {}".format(channel, value))
