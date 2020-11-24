from wizAPI import *
import time
import keyboard
from threading import Thread

tester = wizAPI().register_window(nth=1)

while True:

    threads = []

    t = Thread(target=tester.hold_key, args=('w', 8.847, 0))
    threads.append(t)
    
    t = Thread(target=tester.hold_key, args=('d', 0.248, 3.185))
    threads.append(t)

    t = Thread(target=tester.hold_key, args=('d', 0.162, 4.656))
    threads.append(t)

    t = Thread(target=tester.hold_key, args=('d', 0.099, 6.891))
    threads.append(t)

    # Start all threads
    for x in threads:
        x.start()

    # Wait for all of them to finish
    for x in threads:
        x.join()

    tester.teleport_to_friend('blader.png')

    tester.wait(4)
