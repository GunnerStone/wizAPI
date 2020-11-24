import keyboard
import pythoncom 
import time

HISTORY = {} 

def key_recording(e):
    if e.name not in HISTORY and e.event_type == keyboard.KEY_DOWN:
        HISTORY[e.name] = time.time()
    elif e.name in HISTORY and e.event_type == keyboard.KEY_UP:
        # print(f"The key {e.name} is pressed for {round(e.time - HISTORY.pop(e.name), 3)} seconds")
        if (e.name != 'w'):
            print(f"t = Thread(target=tester.hold_key, args=('{e.name}', {round(time.time() - HISTORY.pop(e.name), 1)}, {round(time.time() - HISTORY['w'], 1)}))\nthreads.append(t)\n")
        else:
            print(f"t = Thread(target=tester.hold_key, args=('{e.name}', {round(time.time() - HISTORY.pop(e.name), 1)}, 0))\nthreads.append(t)\n")
keyboard.hook(key_recording)

pythoncom.PumpMessages() 