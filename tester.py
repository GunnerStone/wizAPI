from wizAPI import *
import time
import keyboard

tester = wizAPI().register_window(nth=0)

print(tester.is_turn_to_play_pass())
# tester.logout(isDungeon=True)