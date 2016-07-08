#! /usr/bin/env python
# coding: utf-8
# coding=utf-8
# -*- coding: utf-8 -*-
# vim: fileencoding=utf-8

import pygame
import time
from pygame.locals import *
import wiringpi
from ps3pad import PS3Pad


import sys,os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/use_wiringpi_python')

from sg90_direct import SG90Direct


class HandServo:

	MIN_VALUE = 0
	MAX_VALUE = 1
	INITIAL_SET = 0

	PWM_COUNTUP_FREQUENCY = 400 # Hz
	PWM_CYCLE_RANGE = 1024 # PWMの1サイクルの解像度0〜1023

	# ServoをPWM制御するピン番号
	# hardware pwm pin, see: http://abyz.co.uk/rpi/pigpio/python.html#hardware_PWM
	# $ gpio readall
	# してBCMの列の数値を使う(wiringPiSetupGpio()しているので)
	WAIST_SERVO_PIN = 12
	BOOM_SERVO_PIN = 13
	ARM_SERVO_PIN = 18
	CRAW_SERVO_PIN = 19

	# 操作対象用インデックス
	WAIST = 0 # 左右に回転する部分
	BOOM = 1 # 台座から伸びる部分。left servo
	ARM = 2 # boomからcrawまでの部分。right servo
	CRAW = 3 # バケットに相当する部分。先端の爪

	# 操作対象とピン番号のマップ
	PIN_MAP = {
		0: WAIST_SERVO_PIN,
		1: BOOM_SERVO_PIN,
		2: ARM_SERVO_PIN,
		3: CRAW_SERVO_PIN,
	}

	# 物理的な可動範囲[min, max] 0〜180の範囲内であること
	# サンプルを参考にする
	# see: https://www.mearm.com/blogs/news/74739717-mearm-on-the-raspberry-pi-work-in-progress
	RANGE = (
		(0, 90), # waist
		(60, 165), # boom
		(40, 180), # arm
		(60, 180), # craw
	)

	# コントローラーの感度係数
	SENSITIVITY = (
		50.0, # waist
		50.0, # boom
		-50.0, # arm
		50.0, # craw
	)

	# 定義済み位置(WAIST, BOOM, ARM, CRAW) -90〜90の範囲
	PRESET = (
		(90, 152, 90, 60), # initial position
		(20, 30, 40, 50), # topキー用
	)

	def __init__(self):
		# initial servo position
		self.position = list(HandServo.PRESET[HandServo.INITIAL_SET])

		# GPIO番号でピンを指定
		wiringpi.wiringPiSetupGpio()

		self.servos = []
		for index in HandServo.PIN_MAP.iterkeys():
			pin = HandServo.PIN_MAP[index]
			# サーボを作る
			self.servos.append(SG90Direct(pin, HandServo.PWM_COUNTUP_FREQUENCY, HandServo.PWM_CYCLE_RANGE))

		wiringpi.pwmSetMode(wiringpi.PWM_MODE_MS)
		wiringpi.pwmSetClock(HandServo.PWM_COUNTUP_FREQUENCY)
		wiringpi.pwmSetRange(HandServo.PWM_CYCLE_RANGE)

		# 初期位置設定
		self._apply()


	def update(self, powerList, delay):
		for index in HandServo.PIN_MAP.iterkeys():
			self.position[index] += powerList[index] * delay * HandServo.SENSITIVITY[index]
			if self.position[index] < HandServo.RANGE[index][HandServo.MIN_VALUE]:
				self.position[index] = HandServo.RANGE[index][HandServo.MIN_VALUE]
			elif self.position[index] > HandServo.RANGE[index][HandServo.MAX_VALUE]:
				self.position[index] = HandServo.RANGE[index][HandServo.MAX_VALUE]
		self._apply()

	def usePreset(self, number):
		self.position = list(HandServo.PRESET[number]);
		self._apply()

	def _apply(self):
		print '-------------'
		for index in HandServo.PIN_MAP.iterkeys():
			pin = HandServo.PIN_MAP[index]
			degree = self.position[index]
			print 'pin: ' + str(pin) + ' (' + self.getPartName(index) + '): ' + str(degree)
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



def main():
	pad = PS3Pad()
	hand = HandServo()
	lastUpdateAt = time.time()
	while True:
		events = pad.getEvents()
		# print 'events: ' + str(len(events))
		for e in events:
			if e.type == pygame.locals.JOYAXISMOTION:
				now = time.time()
				delay = now - lastUpdateAt
				lastUpdateAt = now

				x1 = pad.getAnalog(PS3Pad.L3_AX)
				y1 = pad.getAnalog(PS3Pad.L3_AY)
				x2 = pad.getAnalog(PS3Pad.R3_AX)
				y2 = pad.getAnalog(PS3Pad.R3_AY) 
				print 'delay: ' + str(delay) + 'x1 and y1 : ' + str(x1) +', '+ str(y1) + ', x2 and y2 : ' + str(x2) +' , '+ str(y2)

				# バックホーの操作レバー割当はJIS方式だと以下のようになっている
				# 	（左レバー）			(右レバー)
				#	アーム伸ばし			ブーム下げ
				# 左旋回	○ 右旋回	 バケット掘削 ○ バケット開放
				#	アーム曲げ			ブーム上げ
				# よってバケットをクローに置き換えて
				# (WAIST, ARM, BOOM, CRAW)の順に整理する
				hand.update((x1, y1, y2, x2), delay)


			elif e.type == pygame.locals.JOYBUTTONDOWN:
				if pad.isPressed(PS3Pad.START):
					print 'start button pressed. exit.'
					pygame.quit()
					return
				elif pad.isPressed(PS3Pad.TOP):
					# pre-set 1
					print 'top button pressed.'
					hand.usePreset(1)

if __name__ == '__main__' : 
	main()
# end of file

