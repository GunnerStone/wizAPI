from wizAPI import *
import time
from threading import Thread

tester = wizAPI().register_window(nth=0)

while True:

    threads = []

    t = Thread(target=tester.hold_key, args=('w', 13.752, 0))
    threads.append(t)

    t = Thread(target=tester.navigate_keys, args=(['a','a','a','d','a','a','a','a','a','a','a','d'],[0.273,0.454,0.26,0.164,0.304,0.319,0.185,0.374,0.292,0.184,0.1,0.094],[1.195,2.013,2.931,4.18,5.501,6.723,7.494,9.511,10.747,11.707,12.259,12.689]))
    threads.append(t)

    

    # Start all threads
    for x in threads:
        x.start()

    # Wait for all of them to finish
    for x in threads:
        x.join()

    tester.teleport_to_friend('feinter.png')

    tester.wait(4)