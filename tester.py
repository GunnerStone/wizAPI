from wizAPI import *

tester = wizAPI().register_window(nth=0)

test_pos = tester.get_friendly_pos('star.png')
print('Friend at pos', test_pos)