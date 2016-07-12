#! /usr/bin/env python
# coding: utf-8
# coding=utf-8
# -*- coding: utf-8 -*-
# vim: fileencoding=utf-8

import os
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

		self.servos = []
		for index in RPiServoblasterController.PIN_MAP.iterkeys():
			pin = RPiServoblasterController.PIN_MAP[index]
			# サーボを作る
			self.servos.append(SG90Servoblaster(pin, self.getPartName(index)))

		# self.positionの内容を定期的にcommit()を使ってservoblasterで反映する
		self.positions = []
		self.timer = RepeatedTimer(RPiServoblasterController.COMMIT_INTERVAL_SEC, self.commit)
		self.timer.start()

	# 直接同期的にservoblasterを呼ぶのではなく、
	# 一度内容をインスタンス変数に格納しておき、定期的にservoblasterで反映させる
	def apply(self, positions):
		self.positions = positions

	def shutdown(self):
		# if self.timer is not None:
		self.timer.cancel()

	def getIndexes(self):
		return RPiServoblasterController.PIN_MAP.keys()

	def switchDebugPosition(self):
		for index in RPiServoblasterController.PIN_MAP.iterkeys():
			self.servos[index].switchDebugPosition()


	# マルチスレッド下でタイマーから実行される
	def commit(self):
		if 0 == len(self.positions):
			return
		for index in RPiServoblasterController.PIN_MAP.iterkeys():
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


class SG90Servoblaster:
	MIN_ANGLE = 0
	MAX_ANGLE = 180

	def __init__(self, pin, name):
		# このservoが接続される番号
		# servodを起動した時のServoBlaster用番号を使う
		self.pin = pin
		self.name = name

		# 最後の値(%) 最初は必ず違う値にする
		self.lastPersent = -1

		# デバッグ用
		self.isEnabledDebugPosition = True

	# 操作は角度(degree)で行う。MIN=0度、MAX=180度とする
	# ServoBlasterの操作は0〜100の整数で行うので、このマッピングを行う
	def _getValue(self, degree):
		if SG90Servoblaster.MIN_ANGLE > degree:
			return 0
		elif SG90Servoblaster.MAX_ANGLE < degree:
			return 100
		else:
			# マッピングする
			percent = float(degree) / 180
			return round(percent * 100)

	def switchDebugPosition(self):
		self.isEnabledDebugPosition = not self.isEnabledDebugPosition

	def rotateTo(self, degree):
		persent = self._getValue(degree)
		if self.lastPersent == persent:
			# 同じ値ならスキップ
			return
		self.lastPersent = persent
		command = ("echo %d=%d%% > /dev/servoblaster" % (self.pin, persent))
		if self.isEnabledDebugPosition:
			log =  ('pin: %1d(%s), degree: %.6f, persent: %3d, command: %s' % (self.pin, self.name, degree, persent, command))
			print log
		os.system(command)


