
# Pigmice RobotPy for Raspberry Pi

This project is for running the RobotPy framework on our "minibots" based on
the Raspberry Pi.

Currently we support using the Pololu Micro Maestro to output PWM signals over
a USB port. This functionality should work on any PC, and the Raspberry Pi.

## Requirements

Start with an installation of `python3` and `pip3`. Get these from your OS's
package manager.

You can install `pipenv` with `pip3 install pipenv`.

Then, run
```sh
$ pipenv install
```
in this directory. This will fetch all of the project's dependencies from the
internet and install them.

To change your shell to use the packages installed for this project, run
```sh
$ pipenv shell
```

Now you are ready to develop for this project. When you run `python` it will
know about all the installed dependencies.

## Using this code

### `run` mode

There is sufficient scaffolding to make the robotpy run command work, you invoke this with `python robot.py run`. Right now this will launch a thread that monitors PWM and prints debug output. Someone needs to change this to open a micro maestro, if one is present, and send the PWM values to the micro maestro.

### `sim` mode

There is an incorrect physics model for a tank drive robot in `physics.py`. Someone should get this implemented correctly so that the robotpy sim, run by `python robot.py sim`, drives the robot around in a sensible way. (The bug may also be related to the robot implementation itself).

