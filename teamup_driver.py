from wizAPI import *
import time
from threading import Thread
import logging
import os
import psutil
from sys import argv
import subprocess
import sys
from sys import exit
from yaspin import yaspin
from yaspin.spinners import Spinners
from prompt_toolkit import HTML, print_formatted_text
from prompt_toolkit.styles import Style

try:
    tester = wizAPI().register_window(nth=0)


    str_buffer = "Teamup Kiosk bot running"
    sp = yaspin(text = str_buffer,spinner=Spinners.circleHalves)
    print = print_formatted_text
    style = Style.from_dict({
        'msg': '#71f076 bold',
        'sub-msg': '#616161 italic'
    })

    # Global vars
    if len(sys.argv) > 1:
        SCHOOL = sys.argv[1]
        PROGRAM_START_TIME = int(float(sys.argv[2]))
        ROUND_COUNT = int(sys.argv[3])
    else:
        SCHOOL = "Fire"
        PROGRAM_START_TIME = time.time()
        ROUND_COUNT = 0


    def main():
        tester.teleport_home()
        print("Teleporting home")
        tester.wait_pet_loading()
        print("FInished loading")
        while True:
            tester.join_teamup(world=0,school=SCHOOL)
            global ROUND_COUNT
            global START_TIME
            START_TIME = time.time()
            ROUND_COUNT += 1

    def afk_timeout_failsafe():
        global START_TIME
        global SCHOOL
        global PROGRAM_START_TIME
        global ROUND_COUNT
        while True:
            curr_time = int((time.time() - START_TIME) / 60)
            #print(str(curr_time))
            if(curr_time >= 8):
                # timeout_fails += 1
                logout_failsafe([tester])
                tester.wait(1)
                spawn_program_and_die(['python', 'teamup_driver.py',str(SCHOOL),str(PROGRAM_START_TIME),str(ROUND_COUNT)])
            time.sleep(5)

    def spawn_program_and_die(program, exit_code=0):
        """
        Start an external program and exit the script 
        with the specified return code.

        Takes the parameter program, which is a list 
        that corresponds to the argv of your command.
        """
        # Start the external program
        subprocess.Popen(program)
        # We have started the program, and can suspend this interpreter
        #Kills all active threads & main program
        os._exit(1)

    def display_metrics():
        global START_TIME #time when lap started
        global PROGRAM_START_TIME #time when python script was run
        global ROUND_COUNT
        global sp
        global style
        while(True):
            tester.clear_console()
            #Total Program Runtime
            str_buffer = str('{:0>2}'.format(int((time.time()-PROGRAM_START_TIME)/60))) + ":" + str('{:0>2}'.format(int((time.time()-PROGRAM_START_TIME)%60)))
            #sp.write(str_buffer)
            with sp.hidden():
                print(HTML(
                    u'<ansigreen><u>Total Runtime</u></ansigreen>'+"<b> : </b>"+'<i><ansigrey>'+str_buffer+'</ansigrey></i>'
                ), style=style)

            #Current Lap RunTime
            str_buffer = str('{:0>2}'.format(int((time.time()-START_TIME)/60)))+ ":" + str('{:0>2}'.format(int((time.time()-START_TIME)%60)))
            #formatting for laptime being longer
            curr_minutes = int((time.time()-START_TIME)/60)
            lap_color = "ansigreen"
            if curr_minutes >= 7:
                lap_color = "ansired"
            elif curr_minutes >= 6:
                lap_color = "ansiyellow"

            #sp.write(str_buffer)
            with sp.hidden():
                print(HTML(
                    u'<'+lap_color+'><u>Current Lap Time</u></'+lap_color+'>'+"<b> : </b>"+'<i><ansigrey>'+str_buffer+'</ansigrey></i>'
                ), style=style)

            #Current dungeon run number
            str_buffer = str(ROUND_COUNT)
            #sp.write(str_buffer)
            with sp.hidden():
                print(HTML(
                    u'<b>></b> <ansicyan><u>Current Dungeon Run</u></ansicyan>'+"<b> : </b>"+'<i><ansigrey>'+str_buffer+'</ansigrey></i>'
                ), style=style)

            time.sleep(1)

    def logout_failsafe(windows):
        for w in windows:
            w.logout(isDungeon=True)
            w.teleport_home()

    afk_thread = Thread(target=afk_timeout_failsafe, args=())
    metric_thread = Thread(target=display_metrics,args=())
    try:
        #sp.start()
        START_TIME = time.time()
        #metric_thread.start()
        afk_thread.start()
        time.sleep(2)
        main()
    except KeyboardInterrupt:
        
        sp.write('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
except Exception as e:
    logf = open("logfileErrors.log", "w")
    logging.exception("message")
    str_buffer = str('{:0>2}'.format(int((time.time()-PROGRAM_START_TIME)/60))) + ":" + str('{:0>2}'.format(int((time.time()-PROGRAM_START_TIME)%60)))
    logf.write(str_buffer+str(e))
    logf.close()
    logout_failsafe([tester])
    tester.wait(1)
    spawn_program_and_die(['python', 'teamup_driver.py',str(SCHOOL),str(PROGRAM_START_TIME),str(ROUND_COUNT)])