
import time

from hal_impl.data import hal_data

class Reporter(object):
    def __init__(self):
        def notified_change(_k, _v):
            print("notified!")
            for chan in range(20):
                if hal_data['pwm'][chan]['type'] == 'talon':
                    print("chan {} value {}".format(
                            chan,
                            hal_data['pwm'][chan]['value']))

        for chan in range(20):
            hal_data['pwm'][chan].register('value', notified_change)

