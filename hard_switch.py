#! /usr/bin/env python
# coding: utf-8
# coding=utf-8
# -*- coding: utf-8 -*-
# vim: fileencoding=utf-8

import time
import RPi.GPIO as GPIO
import os

watch_pin = 17
wait_sec = 5
internal_green_led_pin = 16

GPIO.setmode(GPIO.BCM)

# LEDコントロール用に16pinを出力モードに
GPIO.setup(16, GPIO.OUT)

# GPIO18pinを入力モードとし、pull up設定とします
GPIO.setup(watch_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

while True:
    # ボタンが押されるまで待つ
    GPIO.wait_for_edge(watch_pin, GPIO.FALLING)
    sw_counter = 0
    led_is_on = False

    while True:
        sw_status = GPIO.input(watch_pin)
        if sw_status == 0:
            sw_counter = sw_counter + 1
            if led_is_on:
                # LED On
                GPIO.output(16, GPIO.LOW)
            else:
                # LED Off
                GPIO.output(16, GPIO.HIGH)
            led_is_on = not led_is_on
            if sw_counter >= wait_sec:
                print("長押し検知-shutdown")
                os.system("sudo shutdown -h now")
                break
        else:
            print("短押し検知-reboot")
            os.system("sudo reboot")
            break

        time.sleep(1)

    print(sw_counter)
    # LED Off
    GPIO.output(16, GPIO.HIGH)