#! /usr/bin/env python
# coding: utf-8
# coding=utf-8
# -*- coding: utf-8 -*-
# vim: fileencoding=utf-8
import pygame
from pygame.locals import *

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

pygame.joystick.init()
try:
    j = pygame.joystick.Joystick(0) # create a joystick instance
    j.init() # init instance
    print 'Joystickの名称: ' + j.get_name()
    print 'ボタン数 : ' + str(j.get_numbuttons())
except pygame.error:
    print 'Joystickが見つかりませんでした。'

def main():
    pygame.init()
    screen = pygame.display.set_mode( (SCREEN_WIDTH, SCREEN_HEIGHT) ) # 画面を作る
    pygame.display.set_caption('Joystick') # タイトル
    pygame.display.flip() # 画面を反映

    while 1:
        for e in pygame.event.get(): # イベントチェック
            if e.type == QUIT: # 終了が押された？
                return
            if (e.type == KEYDOWN and
                e.key  == K_ESCAPE): # ESCが押された？
                return
            # Joystick関連のイベントチェック
            if e.type == pygame.locals.JOYAXISMOTION: # 7
                x , y = j.get_axis(0), j.get_axis(1)
                print 'x and y : ' + str(x) +' , '+ str(y)
            elif e.type == pygame.locals.JOYBALLMOTION: # 8
                print 'ball motion'
            elif e.type == pygame.locals.JOYHATMOTION: # 9
                print 'hat motion'
            elif e.type == pygame.locals.JOYBUTTONDOWN: # 10
                print str(e.button)+'番目のボタンが押された'
            elif e.type == pygame.locals.JOYBUTTONUP: # 11
                print str(e.button)+'番目のボタンが離された'

if __name__ == '__main__': main()
# end of file