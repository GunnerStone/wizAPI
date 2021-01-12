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
        SCHOOL = "Storm"
        PROGRAM_START_TIME = time.time()
        ROUND_COUNT = 0


    
    def main():
        world = 0
        school = "Storm"
        tester.logout(isDungeon=True)
        tester.wait_pet_loading()
        tester.LOGOUT_FLAG=False
        while True:
            drive(world, school)
            tester.LOGOUT_FLAG=False
            global ROUND_COUNT
            global START_TIME
            START_TIME = time.time()
            ROUND_COUNT += 1
    
    def drive(world, school):
        tester.successful_teamups +=1
    
        #quicksell after N rounds
        if(tester.successful_teamups % 10 == 0):
            tester.quick_sell(False, False)
            tester.wait(1)
        #Wait for kiosk to prompt user to press x
        # tester.reset_teamup_kiosk()
        while not tester.is_on_kiosk():
            tester.wait(.1)
        #boot-up teamup kiosk
        tester.press_key('x').wait(1)

        # Navigate and load up desired world for teamup
        tester.select_world_teamup(pos=0,page=0)
        #move mouse out of the way of CV
        tester.move_mouse(535,492,speed=.1)
        #load the list of displayed dungeons
        teamup_availability = tester.give_teamup_available()

        #refresh page until team availability contains at least 1 true
        while ((not any(teamup_availability)) and (tester.LOGOUT_FLAG==False)):
            tester.wait(1)
            tester.teamup_refresh()
            teamup_availability = tester.give_teamup_available()

        while (tester.LOGOUT_FLAG==True):
            #stall this program until the logout resets the program
            tester.wait(1)
            

        #try to join first available non-long team
        # finding first True value 
        # using next() and enumerate() 
        teamup_index = next((i for i, j in enumerate(teamup_availability) if j), None) 
        tester.select_teamup_at(teamup_index)
        #checks if teamup icon is showing (in queue) or pet icon is missing (already loading in)
        if(tester.is_teamup_icon_showing() or (tester.is_pet_icon_visible() is not False)):
            #Great we are in
            #wait for a lag in displaying the icon
            tester.wait(.5)
            #wait until icon disappears (indicating loading screen into dungeon)
            tester.wait_for_teamup_queue()
            tester.wait(.1)
            #print("Loading...")
            if (tester.is_teamup_canceled()):
                #print("Teamup was canceled, restarting")
                tester.remove_queue_error_teamup().wait(1)
                # tester.reset_teamup_kiosk()
                return
            if (tester.is_refresh_showing()):
                #refresh btn is showing so something errored out, restart program
                #logout to reset kiosk 'x' prompt
                # tester.reset_teamup_kiosk()
                return
            tester.wait_pet_loading()
            #print("In Dungeon")
            tester.clear_dialog()
            tester.move_mouse(717,40)
            #wait for slow computer noobs to get in fight/load
            #otherwise no credit
            tester.wait(.25)

            #Walk forward until fight starts
            while not tester.is_turn_to_play():
                tester.hold_key('w', 1)
            #print("In Fight")

            #print("Next turn found")
            inFight = True
            battle_round = 0

            while inFight:
                tester.mass_feint_attack_teamup(wizard_type = "hitter",boss_pos=0,hitter=school)
            
                tester.wait_for_end_of_round_dialog()
                
                if tester.is_idle():
                    inFight = False
                if tester.find_button('done'):
                    inFight = False
                if tester.find_button('more'):
                    inFight = False
            #print("Battle 1 has ended")
            tester.wait(.5)
            #remove any post-battle dialog (happens in few instances)
            tester.clear_dialog()

            #potion managemant & use before teleporting home
            tester.logout(isDungeon=True)
            tester.wait_pet_loading()

            return
        else:
            #Teamup no longer available, remove error & try again
            #print("Team no longer joinable, restarting")
            tester.remove_queue_error_teamup().wait(1)
            # tester.reset_teamup_kiosk()
            #tester.join_teamup(world=world,page=0)
            return

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
            # w.teleport_home()

    afk_thread = Thread(target=afk_timeout_failsafe, args=())
    metric_thread = Thread(target=display_metrics,args=())
    try:
        sp.start()
        START_TIME = time.time()
        # metric_thread.start()
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