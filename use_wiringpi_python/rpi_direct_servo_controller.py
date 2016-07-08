#! /usr/bin/env python
# coding: utf-8
# coding=utf-8
# -*- coding: utf-8 -*-
# vim: fileencoding=utf-8

import wiringpi
from sg90_direct import SG90Direct


# サーボの制御方法を実装
# SG90Directと一緒に使う
# Paspberry PiのハードウェアPWMを使った実装(ただしちゃんと動かず)
class RPiDirectServoController:
	PWM_COUNTUP_FREQUENCY = 400  # Hz
	PWM_CYCLE_RANGE = 1024  # PWMの1サイクルの解像度0〜1023

	# ServoをPWM制御するピン番号
	# hardware pwm pin, see: http://abyz.co.uk/rpi/pigpio/python.html#hardware_PWM
	# $ gpio readall
	# してBCMの列の数値を使う(wiringPiSetupGpio()しているので)
	#
	# #####################################################################
	# ###GPIO12と13は同じ出力、GPIO18と19は同じ出力となるのでうまく動かない!! ###
	# #####################################################################
	#
	WAIST_SERVO_PIN = 12
	BOOM_SERVO_PIN = 13
	ARM_SERVO_PIN = 18
	CRAW_SERVO_PIN = 19

	# 操作対象とピン番号のマップ
	PIN_MAP = {
		0: WAIST_SERVO_PIN,
		1: BOOM_SERVO_PIN,
		2: ARM_SERVO_PIN,
		3: CRAW_SERVO_PIN,
	}

	def __init__(self):
		# GPIO番号でピンを指定
		wiringpi.wiringPiSetupGpio()

		self.servos = []
		for index in RPiDirectServoController.PIN_MAP.iterkeys():
			pin = RPiDirectServoController.PIN_MAP[index]
			# サーボを作る
			self.servos.append(SG90Direct(pin, RPiDirectServoController.PWM_COUNTUP_FREQUENCY, RPiDirectServoController.PWM_CYCLE_RANGE))

		wiringpi.pwmSetMode(wiringpi.PWM_MODE_MS)
		wiringpi.pwmSetClock(RPiDirectServoController.PWM_COUNTUP_FREQUENCY)
		wiringpi.pwmSetRange(RPiDirectServoController.PWM_CYCLE_RANGE)

	def shutdown(self):
		# スレッドは使ってないので何もしない
		return

	def getIndexes(self):
		return RPiDirectServoController.PIN_MAP.keys()

	def apply(self, positions):
		print '-------------'
		for index in RPiDirectServoController.PIN_MAP.iterkeys():
			degree = positions[index]
			print self.getPartName(index) + ': ' + str(degree)
			self.servos[index].rotateTo(degree)

	def getPartName(self, index):
		if(0 == index):
			return 'WAIST'
		elif(1 == index):
			return 'ARM'
		elif(2 == index):
			return 'BOOM'
		elif(3 == index):
			return 'CRAW'
		else:
			return 'unknown'
