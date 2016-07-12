#! /usr/bin/env python
# coding: utf-8
# coding=utf-8
# -*- coding: utf-8 -*-
# vim: fileencoding=utf-8

import time
import wiringpi
import os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')
from rpi_direct_servo_controller import SG90Direct

PWM_COUNTUP_FREQUENCY = 400 # Hz
PWM_CYCLE_RANGE = 1024 # PWMの1サイクルの解像度0〜1023

# GPIO12またはGPIO18のみサポートされる(GPIO12と13は同じ内容、GPIO18と19は同じ内容となる)
wiringpi.wiringPiSetupGpio()
servoWaist = SG90Direct(12, PWM_COUNTUP_FREQUENCY, PWM_CYCLE_RANGE)
servoBoom = SG90Direct(13, PWM_COUNTUP_FREQUENCY, PWM_CYCLE_RANGE)
servoArm = SG90Direct(18, PWM_COUNTUP_FREQUENCY, PWM_CYCLE_RANGE)
servoCraw = SG90Direct(19, PWM_COUNTUP_FREQUENCY, PWM_CYCLE_RANGE)
wiringpi.pwmSetMode(wiringpi.PWM_MODE_MS)
wiringpi.pwmSetClock(PWM_COUNTUP_FREQUENCY)
wiringpi.pwmSetRange(PWM_CYCLE_RANGE)



def rotate(delay, enableList):
	if enableList[0]:
		servoWaist.rotateTo(180)
	if enableList[1]:
		servoBoom.rotateTo(180)
	if enableList[2]:
		servoArm.rotateTo(180)
	if enableList[3]:
		servoCraw.rotateTo(180)
	time.sleep(delay)
	if enableList[0]:
		servoWaist.rotateTo(0)
	if enableList[1]:
		servoBoom.rotateTo(0)
	if enableList[2]:
		servoArm.rotateTo(0)
	if enableList[3]:
		servoCraw.rotateTo(0)
	time.sleep(delay)


def testSet(testTarget):
	initPosition()
	rotate(2, testTarget)
	rotate(1, testTarget)
	rotate(0.5, testTarget)
	rotate(0.3, testTarget)
	for c in range(1, 5):
		rotate(0.1, testTarget)


def initPosition():
	time.sleep(0.5)
	servoWaist.rotateTo(90)
	servoBoom.rotateTo(152)
	servoArm.rotateTo(90)
	servoCraw.rotateTo(60)
	time.sleep(1)


def main():
	testSet((True, False, False, False))
	testSet((False, True, False, False))
	testSet((False, False, True, False))
	testSet((False, False, False, True))

if __name__ == '__main__' :
	main()
# end of file