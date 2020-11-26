from wizAPI import *
import time
from threading import Thread

tester = wizAPI().register_window(nth=0)

while True:

    threads = []

    t = Thread(target=tester.hold_key, args=('w', 8.109-.3))
    threads.append(t)

    arr1 , arr2, arr3 = ['a','d'],[0.651,0.471],[2.41,5.698]

    t = Thread(target=tester.navigate_keys, args=(arr1,arr2,arr3))
    threads.append(t)

    

    # Start all threads
    for x in threads:
        x.start()

    # Wait for all of them to finish
    for x in threads:
        x.join()

    tester.teleport_to_friend('feinter.png')

    tester.wait(4)