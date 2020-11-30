from wizAPI import *
import time
from threading import Thread

tester = wizAPI().register_window(nth=0)


tester.click(555, 300)
tester.click(261, 491)
tester.click(515, 470)
tester.click(410, 390)
tester.click(555, 300)
tester.click(261, 491)
tester.click(685, 540)