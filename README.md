# mearm-ps3controller-for-raspberrypi
MeArm controllable python 2.x script by PS3 controller on Raspberry pi 3


Install ServoBlaster
$ sudo apt-get install git
$ git clone git://github.com/richardghirst/PiBits.git
$ cd PiBits/ServoBlaster/user
$ make servod
$ sudo ./servod --idle-timeout=2000

Board model:                     1
GPIO configuration:            P1 (26 pins), P5 (8 pins)
Using hardware:                PWM
Using DMA channel:              14
Idle timeout:                 2000ms
Number of servos:                8
Servo cycle time:            20000us
Pulse increment step size:      10us
Minimum width value:            50 (500us)
Maximum width value:           250 (2500us)
Output levels:              Normal

Using P1 pins:               7,11,12,13,15,16,18,22
Using P5 pins:

Servo mapping:
     0 on P1-7           GPIO-4
     1 on P1-11          GPIO-17
     2 on P1-12          GPIO-18
     3 on P1-13          GPIO-27
     4 on P1-15          GPIO-22
     5 on P1-16          GPIO-23
     6 on P1-18          GPIO-24
     7 on P1-22          GPIO-25



Install WiringPi-Python
$ sudo apt-get install git python-dev python-setuptools swig
$ git clone --recursive https://github.com/WiringPi/WiringPi-Python.git
$ cd WiringPi-Python/
$ sudo ./build.sh
$ sudo swig2.0 -python wiringpi.i
$ sudo python setup.py install


Install pygame
$ sudo apt-get install python-pygame pip

