import struct
import time
import serial


class MicroMaestro(object):
    """
    Sender class that formats and sends motor commands
    to the Pololu board over serial USB
    """
    def __init__(self, path):
        self.ser = serial.Serial(path, 9600)
    
    def _minissc(self, channel, pwm):
        """
        packs the motor channel and value into bytes readable by a pololu board
        channel is the maestro output (0-5), pwm is 0-254 corresponding to 1000-2000us
        """
        if channel > 5 or channel < 0:
            raise Exception("Invalid Channel {}".format(channel))
        if pwm > 254 or pwm < 0:
            raise Exception("Invalid Value {}".format(pwm))
        print("Channel {} pwm {}".format(channel, pwm))
        # MiniSSC protocol is 3 bytes starting with ff
        packet = struct.pack("BBB", 0xff, channel, pwm)
        self.ser.write(packet)

    def set_pwm_output(self, channel, output):
        if output > 1.0 or output < -1.0:
            raise Exception("Invalid Control Level {}".format(output))
        if channel > 5 or channel < 0:
            raise Exception("Invalid Channel {}".format(channel))
        pwm = output*(254/2.0) + (254/2.0)

        self._minissc(channel, int(pwm))

class MotorControl(object):
    def __init__(self, maestro_controller):
        self.maestro_controller = maestro_controller

    def output(self, channel, out):
        if out > 1.0 or out < -1.0:
            raise Exception("Invalid Control Level {}".format(output))
        if out == 0:
            self.maestro_controller.set_pwm_output(channel, 0)
        elif out < 0:
            deadzone = 0.08 # determined by experiment for RC 20A Chinese Brushed Controllers
            # The deadzone is the values of the output for which the pwm value doesn't move the motor
            self.maestro_controller.set_pwm_output(channel, out*(1-deadzone) - deadzone)
        elif out > 0:
            deadzone = 0.19 # deadzone is different for each motor direction
            self.maestro_controller.set_pwm_output(channel, out*(1-deadzone) + deadzone)
        
if __name__ == "__main__":
    maestro = MicroMaestro('/dev/ttyACM0')
    motor = MotorControl(maestro)
    
    
    while True:
        s = input("Motor Percentage: ")
        try:
            percent = int(s)
            if percent >= -100 and percent <= 100:
                motor.output(0, percent/100.0)
                motor.output(1, percent/100.0)
            else:
                raise Exception("Invalid Percentage {}".format(percent))
        except Exception as e:
            print(e)
        
                
