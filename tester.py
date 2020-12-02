from wizAPI import *
import time
from threading import Thread

tester = wizAPI().register_window(nth=1)
wx, wy = tester.get_window_rect()[:2]

#tester.use_potion_if_needed(health_percent=80)
 #108, 551
tester.quick_sell(False,False)