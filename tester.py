from wizAPI import *
import time
from threading import Thread

tester = wizAPI().register_window(nth=0)
wx, wy = tester.get_window_rect()[:2]

#tester.use_potion_if_needed(health_percent=80)
 #108, 551
tester.screenshot("loadingscreen2.png",(170,532,20,20))
while True:
    print(pyautogui.pixel(170 + wx,532 + wy))
    time.sleep(.2)