from wizAPI import *
import time
from threading import Thread

tester = wizAPI().register_window(nth=0)

while True:

    threads = []

    t = Thread(target=tester.hold_key, args=('w', 30.498, 0))
    threads.append(t)

    t = Thread(target=tester.hold_key, args=('d', 0.451, 3.619))
    threads.append(t)

    t = Thread(target=tester.hold_key, args=('d', 0.376, 8.204))
    threads.append(t)

    t = Thread(target=tester.hold_key, args=('d', 0.395, 11.282))
    threads.append(t)

    t = Thread(target=tester.hold_key, args=('d', 0.127, 12.997))
    threads.append(t)

    t = Thread(target=tester.hold_key, args=('d', 0.035, 18.203))
    threads.append(t)

    t = Thread(target=tester.hold_key, args=('d', 0.032, 18.32))
    threads.append(t)

    t = Thread(target=tester.hold_key, args=('d', 0.592, 22.078))
    threads.append(t)

    t = Thread(target=tester.hold_key, args=('d', 0.427, 24.991))
    threads.append(t)

    t = Thread(target=tester.hold_key, args=('a', 0.147, 28.8))
    threads.append(t)

    t = Thread(target=tester.hold_key, args=('d', 0.211, 30.072))
    threads.append(t)

    

    

    

    # Start all threads
    for x in threads:
        x.start()

    # Wait for all of them to finish
    for x in threads:
        x.join()

    tester.teleport_to_friend('feinter.png')

    tester.wait(4)