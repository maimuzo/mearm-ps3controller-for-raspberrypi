#! /usr/bin/env python
# coding: utf-8
# coding=utf-8
# -*- coding: utf-8 -*-
# vim: fileencoding=utf-8

import sys,os
import pygame
import time
from pygame.locals import *
from ps3pad_pygame import PS3PadPygame
from repeated_timer import RepeatedTimer


from rpi_direct_servo_controller import RPiDirectServoController
from rpi_servoblaster_controller import RPiServoblasterController
from rpi_pca9685_controller import RPiPCA9685Controller



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
		(0, 180), # waist
		(60, 165), # boom
		(40, 180), # arm
		(60, 180), # craw
	)

	# コントローラーの感度係数
	SENSITIVITY = (
		-50.0, # waist
		-50.0, # boom
		-50.0, # arm
		50.0, # craw
	)

	# 定義済み位置(WAIST, BOOM, ARM, CRAW) 0〜180の範囲
	PRESET = (
		(90, 112, 90, 60), # initial position
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
		self.isEnabledDebugPad = True

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
		pygame.event.set_blocked(pygame.JOYAXISMOTION)
		self.axisScanThread = RepeatedTimer(HandCockpit.SCAN_INTERVAL_SEC, self.scanAxis)
		self.axisScanThread.start()
		self.isStartedAxisScanThread = True

	def stopAxisScanThread(self):
		if True == self.isStartedAxisScanThread:
			self.isStartedAxisScanThread = False
			self.axisScanThread.cancel()
			pygame.event.set_blocked(None)

	def scanAxis(self):
		now = time.time()
		delay = now - self.lastUpdateAt
		self.lastUpdateAt = now

		x1 = self.pad.getAnalog(PS3PadPygame.L3_AX)
		y1 = self.pad.getAnalog(PS3PadPygame.L3_AY)
		x2 = self.pad.getAnalog(PS3PadPygame.R3_AX)
		y2 = self.pad.getAnalog(PS3PadPygame.R3_AY)
		if self.isEnabledDebugPad:
			log = ('delay: %.3f, x1: %.3f, y1: %.3f, x2: %.3f, y2: %.3f' % (delay, x1, y1, x2, y2))
			print log

		# バックホーの操作レバー割当はJIS方式だと以下のようになっている
		# 	（左レバー）			(右レバー)
		#	アーム伸ばし			ブーム下げ
		# 左旋回	○ 右旋回	 バケット掘削 ○ バケット開放
		#	アーム曲げ			ブーム上げ
		# よってバケットをクローに置き換えて
		# (WAIST, BOOM, ARM, CRAW)の順に整理する
		self.update((x1, y1, y2, x2), delay)

	def consumeEvents(self):
		events = self.pad.getEvents()
		# print 'events: ' + str(len(events))
		for e in events:
			if e.type == pygame.locals.JOYBUTTONDOWN:
				if self.pad.isPressed(PS3PadPygame.START):
					print 'start button pressed. exit.'
					return False
				elif self.pad.isPressed(PS3PadPygame.TOP):
					# pre-set 1
					print 'top button pressed.'
					self.usePreset(1)
				elif self.pad.isPressed(PS3PadPygame.CIRCLE):
					self.switchDebugPad()
				elif self.pad.isPressed(PS3PadPygame.BOX):
					self.controller.switchDebugPosition()

			elif False == self.isStartedAxisScanThread and e.type == pygame.locals.JOYAXISMOTION:
				self.scanAxis()
		return True


	def switchDebugPad(self):
		self.isEnabledDebugPad = not self.isEnabledDebugPad




def main():
	pad = PS3PadPygame()
	# controller = RPiDirectServoController()
	# controller = RPiServoblasterController()
	controller = RPiPCA9685Controller()
	hand = HandCockpit(controller, pad)
	hand.startAxisScanThread()
	running = True
	while running:
		running = hand.consumeEvents()
	hand.stopAxisScanThread()
	controller.shutdown()
	pad.shutdown()


if __name__ == '__main__' : 
	main()
# end of file

