#! /usr/bin/env python
# coding: utf-8
# coding=utf-8
# -*- coding: utf-8 -*-
# vim: fileencoding=utf-8

import pygame
import time
from pygame.locals import *
import wiringpi


class SG90:
	# pin mode
	INPUT_MODE = 0
	OUTPUT_MODE = 1
	PWM_MODE = 2

	# Raspberry Pi setting
	PRI_PWM_BASE_CLOCK_FREQUENCY = 19200000 # 19.2MHz

	# reference to: http://akizukidenshi.com/download/ds/towerpro/SG90_a.pdf
	REFERENCE_PWM_1CYCLE_SEC = 0.02
	MIN_ANGLE_SEC = 0.0005
	MAX_ANGLE_SEC = 0.0024
	MIN_ANGLE = -90
	MAX_ANGLE = 90
	MIN_PWM_VALUE = 0

	def __init__(self, pin, pwmCountUpFrequency, pwmCycleRange):
		# このservoが接続されるGPIO番号
		self.pin = pin
		self.pwmCountUpFrequency = pwmCountUpFrequency
		self.pwmCycleRange = pwmCycleRange

		# ピン設定
		wiringpi.pinMode(pin, SG90.PWM_MODE)

		# see: http://qiita.com/locatw/items/f15fd9df40153bbb4d27
		# PWMのカウンタ周期：19.2[MHz]/clock=19.2∗10^6/400=48[KHz]≒0.0208[ms]
		self.pwmFrequency = float(SG90.PRI_PWM_BASE_CLOCK_FREQUENCY / self.pwmCountUpFrequency)
		# PWM周波数：19.2[MHz]/clock/range=19.2∗106/400/1024=46.875[Hz]≒21.3[ms]
		self.pwmCycleSec = 1.0 / self.pwmFrequency * self.pwmCycleRange
		# 48[KHz]∗0.5[ms]=48000[Hz]∗0.0005[s]=24
		self.minPmwValue = int(self.pwmFrequency * SG90.MIN_ANGLE_SEC)
		# 48[KHz]∗2.4[ms]=48000[Hz]∗0.0024[s]=115.2≒115
		self.maxPmwValue = int(self.pwmFrequency * SG90.MAX_ANGLE_SEC)
		self.deltaPmwValue = self.maxPmwValue - self.minPmwValue

		print 'pin: ' + str(self.pin) + ', pwmCountUpFrequency: ' + str(self.pwmCountUpFrequency) + 'Hz, pwmCycleRange: ' + str(self.pwmCycleRange)
		print 'pwmFrequency: ' + ('%.3f' % self.pwmFrequency) + ' Hz(' + ('%.6f' % (1.0 / self.pwmFrequency)) + ' sec), pwmCycleSec: ' + ('%.6f' % self.pwmCycleSec)
		print 'reference pwmCycleSec: ' + str(SG90.REFERENCE_PWM_1CYCLE_SEC)
		print 'minPmwValue: ' + str(self.minPmwValue) + ', maxPmwValue: ' + str(self.maxPmwValue) + ', deltaPmwValue: ' + str(self.deltaPmwValue)

	# 操作は角度(degree)で行う。中間地点を0度とし、MIN=-90度、MAX=90度とする
	# PWMの操作は0〜pwmCycleRangeで行うので、このマッピングを行う
	def _getPWMValue(self, degree):
		if SG90.MIN_ANGLE > degree:
			return SG90.MIN_PWM_VALUE
		elif SG90.MAX_ANGLE < degree:
			return self.pwmCycleRange - 1
		else:
			# マッピングする
			# 0〜180度換算して%算出
			percent = float(degree + 90) / 180
			return int(self.minPmwValue + percent * self.deltaPmwValue)

	def rotateTo(self, degree):
		value = self._getPWMValue(degree)
		wiringpi.pwmWrite(self.pin, value)
		print 'pin: ' + str(self.pin) + ', degree: ' + ('%.6f' % degree) + ', pwmValue: ' + str(value)


wiringpi.wiringPiSetupGpio()
servoWaist = SG90(12, 400, 1024)
servoBoom = SG90(13, 400, 1024)
servoArm = SG90(18, 400, 1024)
servoCraw = SG90(19, 400, 1024)
wiringpi.pwmSetMode(wiringpi.PWM_MODE_MS)
wiringpi.pwmSetClock(400)
wiringpi.pwmSetRange(1024)



def rotate(delay, enableList):
	if enableList[0]:
		servoWaist.rotateTo(90)
	if enableList[1]:
		servoBoom.rotateTo(90)
	if enableList[2]:
		servoArm.rotateTo(90)
	if enableList[3]:
		servoCraw.rotateTo(90)
	time.sleep(delay)
	if enableList[0]:
		servoWaist.rotateTo(-90)
	if enableList[1]:
		servoBoom.rotateTo(-90)
	if enableList[2]:
		servoArm.rotateTo(-90)
	if enableList[3]:
		servoCraw.rotateTo(-90)
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
	servoWaist.rotateTo(0)
	servoBoom.rotateTo(62)
	servoArm.rotateTo(0)
	servoCraw.rotateTo(-30)
	time.sleep(1)


def main():
	testSet((True, False, False, False))
	testSet((False, True, False, False))
	testSet((False, False, True, False))
	testSet((False, False, False, True))

if __name__ == '__main__' :
	main()
# end of file