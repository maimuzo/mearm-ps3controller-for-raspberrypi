#! /usr/bin/env python
# coding: utf-8
# coding=utf-8
# -*- coding: utf-8 -*-
# vim: fileencoding=utf-8

import os, sys
from sg90_servoblaster import SG90Servoblaster
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')
from repeated_timer import RepeatedTimer
import time

# サーボの制御方法を実装
# SG90Servoblasterと一緒に使う
# Servoblasterで実現されるソフトウェアPWMを使った実装
# Servoblasterであれば、複数のGPIOでPWMが使える
class RPiServoblasterController:

	# ServoBlasterへの反映間隔
	COMMIT_INTERVAL_SEC = 0.1

	# ./servodを実行した時のピン番号を使う(GPIOの番号でも、物理位置番号でもない)
	WAIST_SERVO_PIN = 7
	BOOM_SERVO_PIN = 6
	ARM_SERVO_PIN = 5
	CRAW_SERVO_PIN = 4

	# 操作対象とピン番号のマップ
	PIN_MAP = {
		0: WAIST_SERVO_PIN,
		1: BOOM_SERVO_PIN,
		2: ARM_SERVO_PIN,
		3: CRAW_SERVO_PIN,
	}

	def __init__(self):
		# GPIO番号でピンを指定
		# ServoBlasterの起動(rootで実行する必要あり)
		# 50%指定時の中間位置を--maxで調整する。--max=200がちょうどよかった
		os.system('sudo /home/pi/PiBits/ServoBlaster/user/servod --idle-timeout=2000 --max=200')

		# # タイマースレッド内で使うので、HandCockpit.lastUpdateAtとは別に持つ
		# self.lastUpdateAt = time.time()

		self.servos = []
		for index in RPiServoblasterController.PIN_MAP.iterkeys():
			pin = RPiServoblasterController.PIN_MAP[index]
			# サーボを作る
			self.servos.append(SG90Servoblaster(pin))

		# self.positionの内容を定期的にcommit()を使ってservoblasterで反映する
		self.positions = []
		self.timer = RepeatedTimer(RPiServoblasterController.COMMIT_INTERVAL_SEC, self.commit)
		self.timer.start()

	def shutdown(self):
		# if self.timer is not None:
		self.timer.cancel()

	def getIndexes(self):
		return RPiServoblasterController.PIN_MAP.keys()


	# 直接同期的にservoblasterを呼ぶのではなく、
	# 一度内容をインスタンス変数に格納しておき、定期的にservoblasterで反映させる
	def apply(self, positions):
		self.positions = positions


	def commit(self):
		if 0 == len(self.positions):
			return
		print '-------------'
		for index in RPiServoblasterController.PIN_MAP.iterkeys():
			degree = self.positions[index]
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

