#! /usr/bin/env python
# coding: utf-8
# coding=utf-8
# -*- coding: utf-8 -*-
# vim: fileencoding=utf-8

import time
import wiringpi


class SG90Direct:
	# Raspberry Pi setting
	PRI_PWM_BASE_CLOCK_FREQUENCY = 19200000 # 19.2MHz

	# reference to: http://akizukidenshi.com/download/ds/towerpro/SG90_a.pdf
	REFERENCE_PWM_1CYCLE_SEC = 0.02
	MIN_ANGLE_SEC = 0.0005
	MAX_ANGLE_SEC = 0.0024
	MIN_ANGLE = 0
	MAX_ANGLE = 180
	MIN_PWM_VALUE = 0

	def __init__(self, pin, pwmCountUpFrequency, pwmCycleRange):
		# このservoが接続されるGPIO番号
		# GPIO12またはGPIO18のみサポートされる(GPIO12と13は同じ内容、GPIO18と19は同じ内容となる)
		self.pin = pin
		self.pwmCountUpFrequency = pwmCountUpFrequency
		self.pwmCycleRange = pwmCycleRange

		# ピン設定
		wiringpi.pinMode(pin, wiringpi.PWM_OUTPUT)

		# see: http://qiita.com/locatw/items/f15fd9df40153bbb4d27
		# PWMのカウンタ周期：19.2[MHz]/clock=19.2∗10^6/400=48[KHz]≒0.0208[ms]
		self.pwmFrequency = float(SG90Direct.PRI_PWM_BASE_CLOCK_FREQUENCY / self.pwmCountUpFrequency)
		# PWM周波数：19.2[MHz]/clock/range=19.2∗106/400/1024=46.875[Hz]≒21.3[ms]
		self.pwmCycleSec = 1.0 / self.pwmFrequency * self.pwmCycleRange
		# 48[KHz]∗0.5[ms]=48000[Hz]∗0.0005[s]=24
		self.minPmwValue = int(self.pwmFrequency * SG90Direct.MIN_ANGLE_SEC)
		# 48[KHz]∗2.4[ms]=48000[Hz]∗0.0024[s]=115.2≒115
		self.maxPmwValue = int(self.pwmFrequency * SG90Direct.MAX_ANGLE_SEC)
		self.deltaPmwValue = self.maxPmwValue - self.minPmwValue

		print 'pin: ' + str(self.pin) + ', pwmCountUpFrequency: ' + str(self.pwmCountUpFrequency) + 'Hz, pwmCycleRange: ' + str(self.pwmCycleRange)
		print 'pwmFrequency: ' + ('%.3f' % self.pwmFrequency) + ' Hz(' + ('%.6f' % (1.0 / self.pwmFrequency)) + ' sec), pwmCycleSec: ' + ('%.6f' % self.pwmCycleSec)
		print 'reference pwmCycleSec: ' + str(SG90Direct.REFERENCE_PWM_1CYCLE_SEC)
		print 'minPmwValue: ' + str(self.minPmwValue) + ', maxPmwValue: ' + str(self.maxPmwValue) + ', deltaPmwValue: ' + str(self.deltaPmwValue)

	# 操作は角度(degree)で行う。中間地点を0度とし、MIN=0度、MAX=180度とする
	# PWMの操作は0〜pwmCycleRangeで行うので、このマッピングを行う
	def _getPWMValue(self, degree):
		if SG90Direct.MIN_ANGLE > degree:
			return self.minPmwValue
		elif SG90Direct.MAX_ANGLE < degree:
			return self.maxPmwValue
		else:
			# マッピングする
			percent = float(degree) / 180
			return int(self.minPmwValue + percent * self.deltaPmwValue)

	def rotateTo(self, degree):
		value = self._getPWMValue(degree)
		wiringpi.pwmWrite(self.pin, value)
		print 'pin: ' + str(self.pin) + ', degree: ' + ('%.6f' % degree) + ', pwmValue: ' + str(value)
		time.sleep(0.3)
