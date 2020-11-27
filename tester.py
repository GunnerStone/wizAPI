from wizAPI import *
import time
from threading import Thread

tester = wizAPI().register_window(nth=2)

while True:

    threads = []

    # t = Thread(target=tester.hold_key, kwargs=dict(key='w', holdtime=2.646))
    # threads.append(t)

    # arr1 , arr2, arr3 = ['d','a'],[0.707,0.391],[0.06,1.609]

    # t = Thread(target=tester.navigate_keys, args=(arr1,arr2,arr3))
    # threads.append(t)

    
    tester.hold_key('d',0.7)

    tester.hold_key('w',1.5)

    # Start all threads
    for x in threads:
        x.start()

    # Wait for all of them to finish
    for x in threads:
        x.join()

    tester.teleport_to_friend('feinter.png')

    tester.wait(4)