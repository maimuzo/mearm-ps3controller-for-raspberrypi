#! /usr/bin/env python
# coding: utf-8
# coding=utf-8
# -*- coding: utf-8 -*-
# vim: fileencoding=utf-8

import pygame
from pygame.locals import *
import time
 
def main() :
    pygame.init()
 
    while True:
 
        eventlist = pygame.event.get()
 
        eventlist = filter(lambda e : e.type == pygame.locals.JOYBUTTONDOWN , eventlist)
 
        print map(lambda x : x.button,eventlist)
 
        time.sleep(0.1)
 
if __name__ == '__main__':
    pygame.joystick.init()
    try:
        j = pygame.joystick.Joystick(0)
        j.init()
        print 'Joystickの名称: ' + j.get_name()
        print 'ボタン数 : ' + str(j.get_numbuttons())
        main()
    except pygame.error as e:
    	print e
    	print "error({0}): {1}".format(e.errno, e.strerror)
        print 'ジョイスティックを差し込め'
        