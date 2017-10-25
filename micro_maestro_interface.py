import struct
import serial


class MicroMaestro(object):
    """
    Sender class that formats and sends motor commands
    to the Pololu board over serial USB
    """

    def __init__(self, path, channel):
        """
        raises: `RuntimeError` if no micro maestro is present on `path`
        """
        try:
            self.ser = serial.Serial(port=path, baudrate=9600)
        # If no micro maestro is present on the specfied port,
        #  raise a RuntimeError
        except serial.SerialException:
            raise RuntimeError("No micro maestro on port: " + str(path))

        self.channel = channel

    def _minissc(self, channel: int, pwm: float):
        # Is pwm 0-254 correct? Should it be 0-255?
        """Packs the motor channel and value into bytes readable by a
        pololu board channel is the maestro output (0-5), pwm is 0-254
        corresponding to 1000-2000us
        """
        if channel > 5 or channel < 0:
            raise ValueError("Invalid channel: {}".format(channel))
        if pwm > 254.0 or pwm < 0.0:
            raise ValueError("Invalid value: {}".format(pwm))
        # MiniSSC protocol is 3 bytes starting with ff
        packet = struct.pack("BBB", 0xff, channel, pwm)
        self.ser.write(packet)

    def set_pwm_output(self, channel: int, output: float):
        if output > 1.0 or output < -1.0:
            raise ValueError("Invalid pwm value: {}".format(output))
        if channel > 5 or channel < 0:
            raise ValueError("Invalid channel: {}".format(channel))
        pwm = output * (254.0 / 2.0) + (254.0 / 2.0)

        self._minissc(channel, int(pwm))
