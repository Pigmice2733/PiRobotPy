"""
    This is the generic robotpy skeleton. We are going to work to make this run
    on platforms besides the RoboRIO.
"""

import wpilib

import minibot


class Robot(minibot.Minibot):
    def robotInit(self):
        """
        This function is called upon program startup and
        should be used for any initialization code.
        """
        self.robot_drive = wpilib.RobotDrive(
            0, 1, motorController=minibot.MinibotMotorController)
        self.stick = minibot.Joystick(0)

    def autonomous(self):
        """This function is run once each time the robot enters
         autonomous mode."""
        auto_loop_counter = 0

        # Repeat 100 times - approx 2 seconds
        while (auto_loop_counter < 100):
            # Drive forward at half speed
            self.robot_drive.drive(-0.5, 0)
            auto_loop_counter += 1
            wpilib.Timer.delay(0.02)
        # Stop robot once driving is completed
        self.robot_drive.drive(0, 0)  # Stop robot

    def operatorControl(self):
        """This function is called once at the start of operator control."""
        # Drive forward at half speed while in teleop
        while (self.isEnabled() and self.isOperatorControl()):
            self.robot_drive.drive(-0.5, 0)

    def test(self):
        """This function is called once at the start of test mode."""
        wpilib.LiveWindow.run()

    def disabled(self):
        """This is called once every time robot is disabled."""
        self.robot_drive.drive(0, 0)


if __name__ == "__main__":
    wpilib.run(Robot)
