#! /usr/bin/env python
# coding: utf-8
# coding=utf-8
# -*- coding: utf-8 -*-
# vim: fileencoding=utf-8

import os
from repeated_timer import RepeatedTimer
import time
import Adafruit_PCA9685

# サーボの制御方法を実装
# SG90Servoblasterと一緒に使う
# Servoblasterで実現されるソフトウェアPWMを使った実装
# Servoblasterであれば、複数のGPIOでPWMが使える
class RPiPCA9685Controller:



	# 反映間隔
	COMMIT_INTERVAL_SEC = 0.1

	# ./servodを実行した時のピン番号を使う(GPIOの番号でも、物理位置番号でもない)
	WAIST_SERVO_PIN = 0
	BOOM_SERVO_PIN = 1
	ARM_SERVO_PIN = 2
	CRAW_SERVO_PIN = 3

	# 操作対象とピン番号のマップ
	PIN_MAP = {
		0: WAIST_SERVO_PIN,
		1: BOOM_SERVO_PIN,
		2: ARM_SERVO_PIN,
		3: CRAW_SERVO_PIN,
	}

	def __init__(self, address=0x40):
		# I2C経由でのコントロール用ライブラリ
		# https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code.git
		self.pwm = Adafruit_PCA9685.PCA9685(address, busnum=1)

		self.pwm.set_pwm_freq(SG90PCA9685.PWM_FREQ)

		self.servos = []
		for index in RPiPCA9685Controller.PIN_MAP.iterkeys():
			pin = RPiPCA9685Controller.PIN_MAP[index]
			# サーボを作る
			self.servos.append(SG90PCA9685(pin, self.getPartName(index), self.pwm))

		# self.positionの内容を定期的にcommit()を使ってservoblasterで反映する
		self.positions = []
		self.timer = RepeatedTimer(RPiPCA9685Controller.COMMIT_INTERVAL_SEC, self.commit)
		self.timer.start()

	# 直接同期的にservoblasterを呼ぶのではなく、
	# 一度内容をインスタンス変数に格納しておき、定期的にservoblasterで反映させる
	def apply(self, positions):
		self.positions = positions

	def shutdown(self):
		# if self.timer is not None:
		self.timer.cancel()

	def getIndexes(self):
		return RPiPCA9685Controller.PIN_MAP.keys()

	def switchDebugPosition(self):
		for index in RPiPCA9685Controller.PIN_MAP.iterkeys():
			self.servos[index].switchDebugPosition()

	# マルチスレッド下でタイマーから実行される
	def commit(self):
		if 0 == len(self.positions):
			return
		for index in RPiPCA9685Controller.PIN_MAP.iterkeys():
			degree = self.positions[index]
			self.servos[index].rotateTo(degree)

	def getPartName(self, index):
		if(0 == index):
			return 'WAIST'
		elif(1 == index):
			return 'BOOM'
		elif(2 == index):
			return 'ARM'
		elif(3 == index):
			return 'CRAW'
		else:
			return 'unknown'


class SG90PCA9685:
	# reference to: http://akizukidenshi.com/download/ds/towerpro/SG90_a.pdf
	# PWM1サイクルの時間(秒)
	PWM_FREQ = 50
	PWM_1CYCLE_SEC = 0.02
	# PWM1サイクルの解像度
	PWM_RESOLUTION = 4096
	MIN_ANGLE_SEC = 0.0005
	MAX_ANGLE_SEC = 0.0024
	MIN_ANGLE = 0
	MAX_ANGLE = 180
	MIN_PWM_VALUE = 0

	def __init__(self, pin, name, pwm):
		self.pwm = pwm
		self.pin = pin
		self.name = name
		self.isEnabledDebugPosition = True
		self.lastValue = -1

		# MIN_ANGLEの時にカウントすべき数
		self.minPmwValue = int(float(SG90PCA9685.MIN_ANGLE_SEC) / SG90PCA9685.PWM_1CYCLE_SEC * SG90PCA9685.PWM_RESOLUTION)
		# MAX_ANGLEの時にカウントすべき数
		self.maxPmwValue = int(float(SG90PCA9685.MAX_ANGLE_SEC) / SG90PCA9685.PWM_1CYCLE_SEC * SG90PCA9685.PWM_RESOLUTION)
		self.deltaPmwValue = self.maxPmwValue - self.minPmwValue

		print ('pin: %d(%s), PWM_1CYCLE_SEC: %.5f Hz, pwmCycleRange: %d' % (self.pin, self.name, SG90PCA9685.PWM_1CYCLE_SEC, SG90PCA9685.PWM_RESOLUTION))
		print ('minPmwValue: %d, maxPmwValue: %d, deltaPmwValue: %d' % (self.minPmwValue, self.maxPmwValue,self.deltaPmwValue))

	# 操作は角度(degree)で行う。MIN=0度、MAX=180度とする
	# PWMの操作はminPmwValue〜maxPmwValueで行うので、このマッピングを行う
	def _getPWMValue(self, degree):
		if SG90PCA9685.MIN_ANGLE > degree:
			return self.minPmwValue
		elif SG90PCA9685.MAX_ANGLE < degree:
			return self.maxPmwValue
		else:
			# マッピングする
			percent = float(degree) / 180
			return int(self.minPmwValue + percent * self.deltaPmwValue)

	def switchDebugPosition(self):
		self.isEnabledDebugPosition = not self.isEnabledDebugPosition

	def rotateTo(self, degree):
		value = self._getPWMValue(degree)
		if self.lastValue == value:
			# 同じ値ならスキップ
			return
		# 0〜valueまでONにする
		self.pwm.set_pwm(self.pin, 0, value)
		if self.isEnabledDebugPosition:
			log =  ('pin: %1d(%s), degree: %.6f, pwmValue: %s' % (self.pin, self.name, degree, value))
			print log

