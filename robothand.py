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
		wiringpi.pinMode(pin, wiringpi.PWM_OUTPUT)

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
			return self.minPmwValue + int(percent * self.deltaPmwValue)

	def rotateTo(self, degree):
		value = self._getPWMValue(degree)
		wiringpi.pwmWrite(self.pin, value)
		print 'pin: ' + str(self.pin) + ', degree: ' + ('%.6f' % degree) + ', pwmValue: ' + str(value)
		time.sleep(0.3)


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

	# 物理的な可動範囲[min, max] -90〜90の範囲内であること
	# サンプルを参考に0〜180度を、-90〜90度に変換
	# see: https://www.mearm.com/blogs/news/74739717-mearm-on-the-raspberry-pi-work-in-progress
	RANGE = (
		(-90, 90), # waist
		(-30, 75), # boom
		(-50, 90), # arm
		(-30, 90), # craw
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
		(0, 62, 0, -30), # initial position
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
			self.servos.append(SG90(pin, HandServo.PWM_COUNTUP_FREQUENCY, HandServo.PWM_CYCLE_RANGE))

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

