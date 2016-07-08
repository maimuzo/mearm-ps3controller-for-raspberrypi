#! /usr/bin/env python
# coding: utf-8
# coding=utf-8
# -*- coding: utf-8 -*-
# vim: fileencoding=utf-8

import sys,os
import pygame
import time
from pygame.locals import *
from ps3pad import PS3Pad
from repeated_timer import RepeatedTimer


sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/use_wiringpi_python')
from rpi_direct_servo_controller import RPiDirectServoController

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/use_servoblaster')
from rpi_servoblaster_controller import RPiServoblasterController



# PS3コントローラーを操作して各サーボの角度を計算し、可動範囲内に収まるようにする
# サーボには角度のみ伝え、具体的なコントロール方法はcontrollerに任せる
class HandCockpit:

	MIN_VALUE = 0
	MAX_VALUE = 1
	INITIAL_SET = 0

	SCAN_INTERVAL_SEC = 0.1

	# 操作対象用インデックス
	WAIST = 0 # 左右に回転する部分
	BOOM = 1 # 台座から伸びる部分。left servo
	ARM = 2 # boomからcrawまでの部分。right servo
	CRAW = 3 # バケットに相当する部分。先端の爪


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

	# 定義済み位置(WAIST, BOOM, ARM, CRAW) 0〜180の範囲
	PRESET = (
		(90, 152, 90, 60), # initial position
		(20, 30, 40, 50), # topキー用
	)

	def __init__(self, controller, pad):
		# initial servo position
		self.position = list(HandCockpit.PRESET[HandCockpit.INITIAL_SET])
		# controllerはapplyメソッドを持っている必要がある
		self.controller = controller
		self.pad = pad

		self.lastUpdateAt = time.time()
		self.isStartedAxisScanThread = False

		# 初期位置設定
		self._apply()


	def update(self, powerList, delay):
		for index in self.controller.getIndexes():
			self.position[index] += powerList[index] * delay * HandCockpit.SENSITIVITY[index]
			if self.position[index] < HandCockpit.RANGE[index][HandCockpit.MIN_VALUE]:
				self.position[index] = HandCockpit.RANGE[index][HandCockpit.MIN_VALUE]
			elif self.position[index] > HandCockpit.RANGE[index][HandCockpit.MAX_VALUE]:
				self.position[index] = HandCockpit.RANGE[index][HandCockpit.MAX_VALUE]
		self._apply()

	def usePreset(self, number):
		self.position = list(HandCockpit.PRESET[number])
		self._apply()

	def _apply(self):
		self.controller.apply(self.position)

	def startAxisScanThread(self):
		self.axisScanThread = RepeatedTimer(HandCockpit.SCAN_INTERVAL_SEC, self.scanAxis)
		self.axisScanThread.start()
		self.isStartedAxisScanThread = True

	def stopAxisScanThread(self):
		if True == self.isStartedAxisScanThread:
			self.isStartedAxisScanThread = False
			self.axisScanThread.cancel()

	def scanAxis(self):
		now = time.time()
		delay = now - self.lastUpdateAt
		self.lastUpdateAt = now

		x1 = self.pad.getAnalog(PS3Pad.L3_AX)
		y1 = self.pad.getAnalog(PS3Pad.L3_AY)
		x2 = self.pad.getAnalog(PS3Pad.R3_AX)
		y2 = self.pad.getAnalog(PS3Pad.R3_AY)
		print 'delay: ' + str(delay) + 'x1 and y1 : ' + str(x1) + ', ' + str(y1) + ', x2 and y2 : ' + str(
			x2) + ' , ' + str(y2)

		# バックホーの操作レバー割当はJIS方式だと以下のようになっている
		# 	（左レバー）			(右レバー)
		#	アーム伸ばし			ブーム下げ
		# 左旋回	○ 右旋回	 バケット掘削 ○ バケット開放
		#	アーム曲げ			ブーム上げ
		# よってバケットをクローに置き換えて
		# (WAIST, ARM, BOOM, CRAW)の順に整理する
		self.update((x1, y1, y2, x2), delay)

	def consumeEvents(self):
		events = self.pad.getEvents()
		# print 'events: ' + str(len(events))
		for e in events:
			if e.type == pygame.locals.JOYBUTTONDOWN:
				if self.pad.isPressed(PS3Pad.START):
					print 'start button pressed. exit.'
					self.stopAxisScanThread()
					self.controller.shutdown()
					self.pad.shutdown()
					sys.exit()
				elif self.pad.isPressed(PS3Pad.TOP):
					# pre-set 1
					print 'top button pressed.'
					self.usePreset(1)
			elif False == self.isStartedAxisScanThread and e.type == pygame.locals.JOYAXISMOTION:
				self.scanAxis()



def main():
	pad = PS3Pad()
	# controller = RPiDirectServoController()
	controller = RPiServoblasterController()
	hand = HandCockpit(controller, pad)
	hand.startAxisScanThread()
	while True:
		hand.consumeEvents()

if __name__ == '__main__' : 
	main()
# end of file

