#! /usr/bin/env python
# coding: utf-8
# coding=utf-8
# -*- coding: utf-8 -*-
# vim: fileencoding=utf-8

import threading

# see: http://ja.stackoverflow.com/questions/24508/python%E3%81%AEthreading-timer%E3%81%A7%E5%AE%9A%E6%9C%9F%E7%9A%84%E3%81%AB%E5%87%A6%E7%90%86%E3%82%92%E5%91%BC%E3%81%B3%E5%87%BA%E3%81%99%E3%82%B5%E3%83%B3%E3%83%97%E3%83%AB
class RepeatedTimer(threading._Timer):
	def __init__(self, interval, function, args=[], kwargs={}):
		threading._Timer.__init__(self, interval, self.run, args, kwargs)
		self.thread = None
		self.function = function

	def run(self):
		self.thread = threading.Timer(self.interval, self.run)
		self.thread.start()
		self.function(*self.args, **self.kwargs)

	def cancel(self):
		if self.thread is not None:
			self.thread.cancel()
			self.thread.join()
			del self.thread