from wizAPI import *
import time
from threading import Thread

tester = wizAPI().register_window(nth=0)
wx, wy = tester.get_window_rect()[:2]

tester.use_potion_if_needed(health_percent=80)

# print(pyautogui.pixel(26 + wx,531 + wy))