from wizAPI import *
import time
from threading import Thread

tester = wizAPI().register_window(nth=0)
wx, wy = tester.get_window_rect()[:2]

#tester.use_potion_if_needed(health_percent=80)
 #108, 551
# tester.screenshot('test.png', (740, 390, 60, 60))
# while(tester.match_image(tester.screenshotRAM(region=(740, 390, 60, 60)), 'buttons/quest_dialog.png', threshold=.2)):
#     tester.click(770, 430, button='right', delay=.2)
#     tester.move_mouse(730, 430).wait(2)

# x, y = (717,40)#563,394
# tester.set_active()
# # # self.move_mouse(x, y)
# tester.screenshot('test.png',(x,y,15,15))
# large = tester.screenshotRAM((x,y,15,15))
tester.join_teamup(world=4,school="Fire")
