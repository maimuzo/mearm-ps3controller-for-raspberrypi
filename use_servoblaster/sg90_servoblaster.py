#! /usr/bin/env python
# coding: utf-8
# coding=utf-8
# -*- coding: utf-8 -*-
# vim: fileencoding=utf-8

import time
import sys,os


class SG90Servoblaster:
	MIN_ANGLE = 0
	MAX_ANGLE = 180

	def __init__(self, pin):
		# このservoが接続される番号
		# servodを起動した時のServoBlaster用番号を使う
		self.pin = pin

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

	def rotateTo(self, degree):
		persent = self._getValue(degree)
		command = ("echo %d=%d%% > /dev/servoblaster" % (self.pin, persent))
		print 'pin: ' + str(self.pin) + ', degree: ' + ('%.6f' % degree) + ', persent: ' + str(persent) + '%, command: ' + command
		os.system(command)
		# time.sleep(0.3)
