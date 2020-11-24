import keyboard
import pythoncom 
import time

HISTORY = {} 

hold_times = []
keys = []
wait_times = []

"""def key_recording(e):
    if e.name not in HISTORY and e.event_type == keyboard.KEY_DOWN:
        HISTORY[e.name] = time.time()
    elif e.name in HISTORY and e.event_type == keyboard.KEY_UP:
        # print(f"The key {e.name} is pressed for {round(e.time - HISTORY.pop(e.name), 3)} seconds")
        if (e.name != 'w'):
            print(f"t = Thread(target=tester.hold_key, args=('{e.name}', {round(time.time() - HISTORY.pop(e.name), 3)}, {round(time.time() - HISTORY['w'], 3)}))\nthreads.append(t)\n")
        else:
            print(f"t = Thread(target=tester.hold_key, args=('{e.name}', {round(time.time() - HISTORY.pop(e.name), 3)}, 0))\nthreads.append(t)\n")
"""
def key_recording(e):
    if e.name == "o" and e.event_type == keyboard.KEY_DOWN:
        print("[", end='')
        for i in range(len(keys)):
            print(keys[i], end='')
            if(i < len(keys) - 1):
                print(",", end='')
        print("],", end='')
        print("[", end='')
        for i in range(len(hold_times)):
            print(hold_times[i], end='')
            if(i < len(hold_times) - 1):
                print(",", end='')
        print("],", end='')
        print("[", end='')
        for i in range(len(wait_times)):
            print(wait_times[i], end='')
            if(i < len(wait_times) - 1):
                print(",", end='')
        print("]")
    if e.name not in HISTORY and e.event_type == keyboard.KEY_DOWN:
        HISTORY[e.name] = time.time()
    elif e.name in HISTORY and e.event_type == keyboard.KEY_UP:
        # print(f"The key {e.name} is pressed for {round(e.time - HISTORY.pop(e.name), 3)} seconds")
        if (e.name != 'w'):
            hold_times.append(round(time.time() - HISTORY.pop(e.name), 3))
            keys.append(e.name)
            wait_times.append(round(time.time() - HISTORY['w'], 3))
        else:
            print(f"t = Thread(target=tester.hold_key, args=('{e.name}', {round(time.time() - HISTORY.pop(e.name), 3)}, 0))\nthreads.append(t)\n")

keyboard.hook(key_recording)



pythoncom.PumpMessages() 
