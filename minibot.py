"""Contains modifications and extensions to RobotPy
 needed for the minibot project"""

import wpilib
import hal
import networktables

import pwmoutput
import micro_maestro_interface


class Minibot(wpilib.SampleRobot):
    """Subclass of wpilib.SampleRobot, handles Pololu board, etc."""

    def __init__(self, *args, **kwargs):
        super(Minibot, self).__init__(*args, **kwargs)

        self.ds = DriverStation()

        try:
            micro_maestro = micro_maestro_interface.MicroMaestro("test", 0)
        except RuntimeError:
            # No micro maestro on correct port
            micro_maestro = None

        pwmoutput.PwmWatch(micro_maestro)

    def startCompetition(self):
        """Start a competition.
        This code tracks the order of the field starting to ensure that
        everything happens in the right order. Repeatedly run the correct
        method, either Autonomous or OperatorControl when the robot is
        enabled. After running the correct method, wait for some state to
        change, either the other mode starts or the robot is disabled. Then
        go back and wait for the robot to be enabled again.

        This code is nearly identical to `SampleRobot.startCompetition`, with
         minor modifications to make it work with `minibot.DriverStation`. Once
         the client-side driver station is compatible with
         `wpilib.DriverStation` this will be unnecessary.
        """
        self.robotInit()

        self.robotMain()

        if hasattr(self, '_no_robot_main'):
            # first and one-time initialization
            while True:
                if self.isDisabled():
                    self.disabled()
                    while self.isDisabled():
                        wpilib.Timer.delay(0.01)
                elif self.isAutonomous():
                    self.autonomous()
                    while self.isAutonomous() and not self.isDisabled():
                        wpilib.Timer.delay(0.01)
                elif self.isTest():
                    self.test()
                    while self.isTest() and self.isEnabled():
                        wpilib.Timer.delay(0.01)
                else:
                    self.operatorControl()
                    while self.isOperatorControl() and not self.isDisabled():
                        wpilib.Timer.delay(0.01)


class DriverStation:
    """DriverStation for Rpi

    Provide access to the network communication data
     to / from the remote driverstation.
    """

    def __init__(self):
        """DriverStation constructor."""
        self.table = networktables.NetworkTables.getTable('driver_station')

    def getStickAxis(self, stick, axis):
        """Get the value of the axis on a joystick.
        This depends on the mapping of the joystick connected to the specified
        port.

        :param stick: The joystick port number
        :type stick: int
        :param axis: The analog axis value to read from the joystick.
        :type axis: int

        :returns: The value of the axis on the joystick.
        """

        if axis < 0 or axis >= 3:
            raise IndexError("Joystick axis is out of range")
        if stick < 0 or stick >= 2:
            raise IndexError(
                "Joystick index is out of range, should be 0-%s" % 2)

        key = "/joystick-" + str(stick) + "/axis-" + str(axis)

        try:
            return self.table.getNumber(
                key) if networktables.NetworkTables.isConnected() else 0.0
        except KeyError:
            # Joystick is unavailable, user should be notified?
            return 0.0

    def getStickButton(self, stick, button):
        """The state of a button on the joystick. Button indexes begin at 1.
        :param stick: The joystick port number
        :type stick: int
        :param button: The button index, beginning at 1.
        :type button: int

        :returns: The state of the button.
        """
        if stick < 0 or stick >= 2:
            raise IndexError(
                "Joystick index is out of range, should be 0-%s" % 2)

        key = "/joystick-" + str(stick) + "/button-" + str(button)

        try:
            return self.table.getNumber(
                key) != 0.0 if networktables.NetworkTables.isConnected(
                ) else 0.0
        except KeyError:
            # Joystick is unavailable, user should be notified?
            return 0.0

    def isEnabled(self):
        try:
            return self.table.getBoolean("/enabled")
        except KeyError:
            # DS is not sending enabled/disabled
            return False

    def isDisabled(self):
        try:
            return not self.table.getBoolean("/enabled")
        except KeyError:
            # DS is not sending enabled/disabled
            return True

    def isAutonomous(self):
        try:
            return self.table.getString("/mode") == "autonomous"
        except KeyError:
            # DS is not sending mode
            return False

    def isOperatorControl(self):
        try:
            return self.table.getString("/mode") == "teleop"
        except KeyError:
            # DS is not sending mode
            return False

    def isTest(self):
        try:
            return self.table.getString("/mode") == "test"
        except KeyError:
            # DS is not sending mode
            return False


class Joystick:
    """Joystick for Rpi

    Handle input from standard Joysticks connected to the driverstation.

    This class handles standard input that comes from the driverstation. Each
    time a value is requested the most recent value is returned. There is a
    single class instance for each joystick and the mapping of ports to
    hardware buttons depends on the code in the drivestation.
    """

    def __init__(self, port):
        """Construct an instance of a joystick.
        The joystick index is the USB port on the Driver Station.

        :param port: The port on the Driver Station that the joystick is
            plugged into.
        :type  port: int
        """
        self.port = port

        self.ds = DriverStation()

    def getX(self, hand=None):
        """Get the X value of the joystick.

        This depends on the mapping of the joystick connected to the current
        port.

        :param hand: Unused
        :returns: The X value of the joystick.
        :rtype: float
        """
        return self.getRawAxis(0)

    def getY(self, hand=None):
        """Get the Y value of the joystick.

        This depends on the mapping of the joystick connected to the current
        port.

        :param hand: Unused
        :returns: The Y value of the joystick.
        :rtype: float
        """
        return self.getRawAxis(1)

    def getZ(self, hand=None):
        return self.getRawAxis(3)

    def getTwist(self):
        """Get the twist value of the current joystick.

        This depends on the mapping of the joystick connected to the current
        port.

        :returns: The Twist value of the joystick.
        :rtype: float
        """
        return self.getRawAxis(2)

    def getRawAxis(self, axis):
        """Get the value of the axis.

        :param axis: The axis to read, starting at 0.
        :type  axis: int
        :returns: The value of the axis.
        :rtype: float
        """
        return self.ds.getStickAxis(self.port, axis)


class MinibotMotorController(wpilib.PWMSpeedController):
    """Minibot Speed Controller via PWM"""

    def __init__(self, channel):
        """Constructor for a minibot electronic speed controller (ESC)

        :param channel: The PWM channel that the ESC is attached to. Channels
        0-5 are valid channels on the micro maestro.
        :type  channel: int

        .. note ::
            These values for the ESC deadbands are untested and likely to need
             additional calibration

            - 1.800ms = full "forward" - this is a WAG, needs to be found
             experimentally
            - 1.595ms = the "high end" of the deadband range
            - 1.500ms = center of the deadband range (off) - should be roughly
             correct but could use some fine tuning
            - 1.460ms = the "low end" of the deadband range
            - 1.200ms = full "reverse" - also a WAG, pretty much
             totally random number
        """
        super().__init__(channel)
        self.setBounds(1.800, 1.595, 1.500, 1.460, 1.200)
        # The period multiplier might also need calibration, we might
        #  even need to completely override it.
        self.setPeriodMultiplier(self.PeriodMultiplier.k4X)
        self.setSpeed(0.0)
        # What does this line do? I think it might be zeroing a
        #  hardware latch in the speed controller, but I don't
        #  know if we need it with the minibot motor controllers
        self.setZeroLatch()

        wpilib.LiveWindow.addActuatorChannel("Minibot ESC",
                                             self.getChannel(), self)
        # We can just pretend we are a Talon to the hal, as I don't
        #  see any clean way to add a new hal resource type
        hal.report(hal.UsageReporting.kResourceType_Talon, self.getChannel())
