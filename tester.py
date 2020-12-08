from wizAPI import *
import time
from threading import Thread

tester = wizAPI().register_window(nth=0)
wx, wy = tester.get_window_rect()[:2]

#tester.use_potion_if_needed(health_percent=80)
 #108, 551
# tester.screenshot('test.png', (350, 415, 100, 20))
# tester.bazaar_sell("feinter.png")
tester.quick_sell(sell_crown_items=False, sell_jewels=False)