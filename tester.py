from wizAPI import *
import time
import keyboard

tester = wizAPI().register_window(nth=0)

print(tester.find_button('done'))
# tester.logout(isDungeon=True)