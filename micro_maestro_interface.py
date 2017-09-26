import struct
import time
import serial


class MicroMaestro(object):
    """
    Sender class that formats and sends motor commands
    to the Pololu board over serial USB
    """
    def __init__(self, path):
        # Serial opened at 9600 baud
        self.ser = serial.Serial(path, 9600)

    def _minissc(self, channel, pwm):
        """
        packs the motor channel and value into bytes readable by a pololu board
        channel is the maestro output (0-5), pwm is 0-254 corresponding to 1000-2000us
        """
        if channel > 5 or channel < 0:
            raise ValueError("Invalid Channel {}".format(channel))
        if pwm > 254 or pwm < 0:
            raise ValueError("Invalid Value {}".format(pwm))
        print("Channel {} pwm {}".format(channel, pwm))
        # MiniSSC protocol is 3 bytes starting with ff
        packet = struct.pack("BBB", 0xff, channel, pwm)
        self.ser.write(packet)

    def set_pwm_output(self, channel, output):
        if output > 1.0 or output < -1.0:
            raise ValueError("Invalid Control Level {}".format(output))
        if channel > 5 or channel < 0:
            raise ValueError("Invalid Channel {}".format(channel))
        pwm = output*(254/2.0) + (254/2.0)

        self._minissc(channel, int(pwm))

class MotorControl(object):
    def __init__(self, maestro_controller, channel):
        self.maestro_controller = maestro_controller
        self.channel = channel

    def set_bounds(self, bmax, bmin, mid, fmin, fmax):
        """
        Sets the max backward, forward, and resting values of the motors
        as well as the deadzones for the motors (min values).
        """
        self.bmax = bmax #tbd
        self.bmin = bmin #0.08
        self.mid = mid #0.0
        self.fmin = fmin #0.19
        self.fmax = fmax #tbd
    
    def output(self, out):
        if out > fmax or out < -bmax:
            raise ValueError("Invalid Control Level {}".format(output))
        if out == 0:
            self.maestro_controller.set_pwm_output(self.channel, mid)
        elif out < 0:
            # the max and min values of the motor are used to scale the input from the joysticks and convert them
            # into values that the robot can use (without breaking).
            self.maestro_controller.set_pwm_output(self.channel, out*(bmax-bmin) - bmin)
        elif out > 0:
            self.maestro_controller.set_pwm_output(self.channel, out*(fmax-fmin) + fmin)
 
