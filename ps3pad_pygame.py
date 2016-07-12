#! /usr/bin/env python
# coding: utf-8
# coding=utf-8
# -*- coding: utf-8 -*-
# vim: fileencoding=utf-8

import pygame


class PS3PadPygame:
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
    CIRCLE_A = 17
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
                print 'init display...'
                screen = pygame.display.set_mode((PS3PadPygame.SCREEN_WIDTH, PS3PadPygame.SCREEN_HEIGHT))
                print 'done.'
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

    def shutdown(self):
        pygame.quit()
