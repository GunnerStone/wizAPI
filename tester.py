from wizAPI import *
import time
from threading import Thread

tester = wizAPI().register_window(nth=2)
wx, wy = tester.get_window_rect()[:2]

#tester.use_potion_if_needed(health_percent=80)
 #108, 551
# tester.screenshot('test.png', (740, 390, 60, 60))
# while(tester.match_image(tester.screenshotRAM(region=(740, 390, 60, 60)), 'buttons/quest_dialog.png', threshold=.2)):
#     tester.click(770, 430, button='right', delay=.2)
#     tester.move_mouse(730, 430).wait(2)
THRESHOLD = 15
POSITION = (26,541)            
COLOR = (220, 43, 60)
tester.screenshot(name="test.png",region=(26,541,20,20))
print(pyautogui.pixel(26+wx,541+wy))
print(tester.pixel_matches_color(POSITION, COLOR, threshold=THRESHOLD))