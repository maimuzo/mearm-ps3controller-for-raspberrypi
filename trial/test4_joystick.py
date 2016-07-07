#! /usr/bin/env python
# coding: utf-8
# coding=utf-8
# -*- coding: utf-8 -*-
# vim: fileencoding=utf-8

from evdev import InputDevice, categorize, ecodes
from select import select
dev = InputDevice('/dev/input/event0')
# dev = InputDevice('/dev/input/js0')

print(dev)

def main():
	while True:
	  r,w,x = select([dev], [], [])
	  for event in dev.read():
	  	print('event: ' + str(event.type))
	  	if event.type == ecodes.EV_KEY:
	  		print(categorize(event))
	
if __name__ == '__main__':
  main()
  
	