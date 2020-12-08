from wizAPI import *
import time
from threading import Thread
import os
import sys
import psutil
import logging

tester = wizAPI().register_window(nth=1)
wx, wy = tester.get_window_rect()[:2]

#tester.use_potion_if_needed(health_percent=80)
 #108, 551
# tester.screenshot('test.png', (350, 415, 100, 20))
# tester.bazaar_sell("feinter.png")
tester.click(350, 350)
tester.wait(2)
tester.click(350, 405)

restart_program()