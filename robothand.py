#! /usr/bin/env python
# coding: utf-8
# coding=utf-8
# -*- coding: utf-8 -*-
# vim: fileencoding=utf-8

import pygame
import time
from pygame.locals import *
import wiringpi

class HandServo:
	# pin mode
	INPUT_MODE = 0
	OUTPUT_MODE = 1
	PWM_MODE = 2

	MIN_VALUE = 0
	MAX_VALUE = 1

	INITIAL_SET = 0

	# ServoをPWM制御するピン番号
	# hardware pwm pin, see: http://abyz.co.uk/rpi/pigpio/python.html#hardware_PWM
	# でも、software pwmならどのGPIOピンでも使える(?)
	# $ gpio readall
	# してBCMの列の数値を使う(wiringPiSetupGpio()しているので)
	WAIST_SERVO_PIN = 2
	BOOM_SERVO_PIN = 3
	ARM_SERVO_PIN = 4
	CRAW_SERVO_PIN = 14

	# 操作対象用インデックス
	WAIST = 0 # 左右に回転する部分
	BOOM = 1 # 台座から伸びる部分。left servo
	ARM = 2 # boomからcrawまでの部分。right servo
	CRAW = 3 # バケットに相当する部分。先端の爪

	# 操作対象とピン番号のマップ
	PIN_DIC = {
		0: WAIST_SERVO_PIN,
		1: BOOM_SERVO_PIN,
		2: ARM_SERVO_PIN,
		3: CRAW_SERVO_PIN,
	}

	# 物理的な可動範囲[min, max] 0〜100の範囲内であること
	# サンプルを参考に0〜180度を、0〜100に変換
	# see: https://www.mearm.com/blogs/news/74739717-mearm-on-the-raspberry-pi-work-in-progress
	RANGE = (
		(0, 100), # waist
		(33, 92), # boom
		(22, 100), # arm
		(33, 100), # craw
	)

	# コントローラーの感度係数
	SENSITIVITY = (
		50, # waist
		50, # boom
		50, # arm
		50, # craw
	)

	# 定義済み位置(WAIST, BOOM, ARM, CRAW)
	PRESET = (
		(50, 85, 50, 33), # initial position
		(20, 30, 40, 50), # topキー用
	)

	def __init__(self):
		# initial servo position
		self.position = list(HandServo.PRESET[HandServo.INITIAL_SET]);

		# GPIO番号でピンを指定
		wiringpi.wiringPiSetupGpio()

		for index in HandServo.PIN_DIC.iterkeys():
			pin = HandServo.PIN_DIC[index]
			# ピンモード設定
			wiringpi.pinMode(pin, HandServo.OUTPUT_MODE)
			# 可動範囲設定 0〜100で指定
			wiringpi.softPwmCreate(pin, 0, 100)

			# wiringpi.pinMode(pin, wiringpi)

		# 初期位置設定
		self._apply()


	def update(self, powerList, delay):
		for index in HandServo.PIN_DIC.iterkeys():
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
		for index in HandServo.PIN_DIC.iterkeys():
			pin = HandServo.PIN_DIC[index]
			# 端数を落として使う
			value = int(self.position[index])
			wiringpi.softPwmWrite(pin, value)
			print self.getPartName(index) + ': ' + str(value)

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


class PS3Pad:
	# digital 0 to 18
	SELECT = 0
	L3 = 1
	R3 = 2
	START = 3
	TOP = 4
	RIGHT = 5
	BOTTOM = 6
	LEFT = 7
	L2 = 8
	R2 = 9
	L1 = 10
	R1 = 11
	TRIANGLE = 12
	CIRCLE = 13
	CROSS = 14
	BOX = 15
	PS = 16
	
	# analog 0 to 26
	L3_AX = 0
	L3_AY = 1
	R3_AX = 2
	R3_AY = 3
	TOP_A = 8
	RIGHT_A = 9
	BOTTOM_A = 10
	LEFT_A  = 11
	L2_A = 12
	R2_A = 13
	L1_A = 14
	R1_A = 15
	TRIANGLE_A = 16
	CIRCLE = 17
	CROSS_A = 18
	BOX_A = 19

	# なんでもいいので適当
	SCREEN_WIDTH = 10
	SCREEN_HEIGHT = 10

	def __init__(self):
		
		pygame.joystick.init()
		try:
			self.joystick = pygame.joystick.Joystick(0)
			self.joystick.init()
			if 'Sony PLAYSTATION(R)3 Controller' in self.joystick.get_name() \
					and 27 == self.joystick.get_numaxes() \
					and 19 == self.joystick.get_numbuttons():
				pygame.init()
				# 初期化しないとエラーになる
				screen = pygame.display.set_mode( (PS3Pad.SCREEN_WIDTH, PS3Pad.SCREEN_HEIGHT) )
			else:
				raise Exception('this joystick is no PS3 controller')
		except pygame.error:
			print 'Joystickが見つかりませんでした。'
	
	def getEvents(self):
		return pygame.event.get()
		
	def getAnalog(self, number):
		return self.joystick.get_axis(number)
		
	def isPressed(self, number):
		return 1 == self.joystick.get_button(number)

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

