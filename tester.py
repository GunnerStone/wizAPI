from wizAPI import *
import time
from threading import Thread

tester = wizAPI().register_window(nth=2)
wx, wy = tester.get_window_rect()[:2]

#tester.use_potion_if_needed(health_percent=80)
 #108, 551
# tester.screenshot('test.png', (665, 325, 40, 70))
tester.bazaar_sell("feinter.png")