# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from wizAPI import *
import time
import math
import random
from threading import Thread
import os
import sys
import psutil
import logging
from sys import argv
import subprocess
import sys
from sys import exit
from yaspin import yaspin
from yaspin.spinners import Spinners
from prompt_toolkit import HTML, print_formatted_text
from prompt_toolkit.styles import Style

""" Register windows """
time.sleep(1) #wait for previoius process to finish

str_buffer = "Detritus 3p Bot Running"
sp = yaspin(text = str_buffer,spinner=Spinners.circleHalves)
print = print_formatted_text
# build a basic prompt_toolkit style for styling the HTML wrapped text
style = Style.from_dict({
    'msg': '#71f076 bold',
    'sub-msg': '#616161 italic'
})

try:
    blader = wizAPI().register_window(nth=2) # Middle
    hitter = wizAPI().register_window(nth=1) # Furthest Left
    feinter = wizAPI().register_window(nth=0) # Furthest Right 
except IndexError:
    print('You need 3 wizard101 accounts to run this particular bot. 2 or less accounts detected')
    exit()

""" compare x positions of windows to make sure 'hitter' is the farthest left, and 'feinter' is the farthest right, and 'blader' is middle """
if (hitter.get_window_rect()[0] > feinter.get_window_rect()[0]):
    # Switch them, if not
    hitter, feinter = feinter, hitter

if(hitter.get_window_rect()[0] > blader.get_window_rect()[0]):
    hitter, blader = blader, hitter

if(blader.get_window_rect()[0] > feinter.get_window_rect()[0]):
    blader, feinter = feinter, blader

# Time Func
START_TIME = time.time()
PROGRAM_START_TIME = time.time() #treat this like a constant

# Global vars
if len(sys.argv) > 1:
    ROUND_COUNT = int(sys.argv[1])
    failed_runs = int(sys.argv[2])
    timeout_fails = int(sys.argv[3])
    PROGRAM_START_TIME = int(float(sys.argv[4]))
else:
    ROUND_COUNT = 0
    failed_runs = 0
    timeout_fails = 0

Fail = False
user_order = [[feinter, 'feinter.png'], [hitter, 'hitter.png'], [blader, 'blader.png']]
boss_pos = feinter.get_enemy_pos('sun.png')

# Thread Init - Used for movement sequences
threads = []


def await_finished_loading(windows):
    for w in windows:
        while not w.is_logo_bottom_left_or_right_loading(): # Looks at either side for logo - update for wiz loading screen update
            time.sleep(.2)

    for w in windows:
        while not w.is_idle():
            time.sleep(.5)

def clear_dialog(windows):
    for w in windows:
        w.clear_dialog()

def print_separator(*args):
    sides = '+'*16
    _str = " ".join([sides, " ".join(args), sides])
    l = len(_str)
    print('='*l)
    print(_str)
    print('='*l)

def print_rount_count(dungeon, roundcount, failed=0):
    print('-------- Dungeon Round:',dungeon,'Battle round:', roundcount, '', end = "")
    if(failed > 0):
        print('Failed Runs:',failed,'', end = "")
    if(timeout_fails > 0):
        print('Timeout Fails:',timeout_fails,'', end = "")
    print('--------')

def print_time(timer):
    minutes = math.floor(timer/60)
    seconds = math.floor(timer % 60)
    print('Round lasted {} minutes and {} seconds.'.format(minutes, seconds))

def logout_failsafe(windows):
    for w in windows:
        w.logout(isDungeon=True)

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

def afk_timeout_failsafe():
    global timeout_fails
    global START_TIME
    while True:
        if((time.time() - START_TIME) / 60 >= 15):
            timeout_fails += 1
            logout_failsafe([feinter, hitter, blader])
            spawn_program_and_die(['python', 'farm_catacombs_detritus_three.py',str(ROUND_COUNT), str(failed_runs), str(timeout_fails),str(PROGRAM_START_TIME)])
        time.sleep(5)
        # print("Current time:"+str((time.time() - START_TIME) / 60))

def display_metrics():
    global START_TIME #time when lap started
    global PROGRAM_START_TIME #time when python script was run
    global ROUND_COUNT
    global failed_runs
    global sp
    global style
    while(True):
        feinter.clear_console()
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
        if curr_minutes >= 14:
            lap_color = "ansired"
        elif curr_minutes >= 10:
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
        
        #number of failed runs
        str_buffer = str(failed_runs)
        #sp.write(str_buffer)
        with sp.hidden():
            print(HTML(
                u'<b>></b> <purple><u>Failed Runs</u></purple>'+"<b> : </b>"+'<i><ansigrey>'+str_buffer+'</ansigrey></i>'
            ), style=style)

        time.sleep(1)

def main():
    #clear python console
    global ROUND_COUNT
    global failed_runs
    global boss_pos
    global START_TIME

    while True:
        START_TIME = time.time()
        ROUND_COUNT += 1
        #print_separator('ROUND', str(ROUND_COUNT))

        """ Attempt to enter the dungeon """
        time.sleep(1)

        while not feinter.enter_dungeon_dialog():
            time.sleep(1)

        while not blader.enter_dungeon_dialog():
            time.sleep(1)

        while not hitter.enter_dungeon_dialog():
            time.sleep(1)

        random.shuffle(user_order)

        """ Quick sell every 10 rounds"""
        if(ROUND_COUNT % 10 == 0):
            feinter.quick_sell(False, False)
            hitter.quick_sell(False, False)
            blader.quick_sell(False, False)

        blader.clear_quest_buttons()
        hitter.clear_quest_buttons()

        """ Check health and use potion if necessary """
        user_order[0][0].use_potion_if_needed(refill=True, teleport_to_wizard=user_order[1][1], health_percent=80)
        user_order[1][0].use_potion_if_needed(refill=True, teleport_to_wizard=user_order[0][1], health_percent=80)
        user_order[2][0].use_potion_if_needed(refill=True, teleport_to_wizard=user_order[1][1], health_percent=80)

        user_order[0][0].press_key('x').wait(random.uniform(0.5, 1.5))
        user_order[1][0].press_key('x').wait(random.uniform(0.2, 1.7))
        user_order[2][0].press_key('x').wait(random.uniform(0.3, 1.3))

        await_finished_loading([feinter, hitter, blader])

        #print('All players have entered the dungeon')

        """ Run into first battle """
        #walk_to_next_battle("all", 1)
        feinter.hold_key('w', random.uniform(2.2, 3)).wait(1.5)
        clear_dialog([feinter, hitter, blader])
        blader.hold_key('w', random.uniform(2.3, 2.5))
        hitter.hold_key('w', random.uniform(2, 2.5))

        feinter.hold_key('w', random.uniform(1.3, 1.4))
        blader.hold_key('w', random.uniform(1.2, 1.3))
        hitter.hold_key('w', random.uniform(1.3, 3))


        feinter.wait_for_next_turn()

        inFight = True
        battle_round = 0

        while inFight:
            battle_round += 1
            print_rount_count(ROUND_COUNT, battle_round, failed_runs)
            
            random.shuffle(user_order)

            user_order[0][0].catacombs_detritus_attack(wizard_type = user_order[0][1], boss_pos = boss_pos, boss_battle=False)
            user_order[1][0].move_mouse(400,20,speped=.5)
            user_order[1][0].catacombs_detritus_attack(wizard_type = user_order[1][1], boss_pos = boss_pos, boss_battle=False)
            user_order[2][0].move_mouse(400,20,speped=.5)
            user_order[2][0].catacombs_detritus_attack(wizard_type = user_order[2][1], boss_pos = boss_pos, boss_battle=False)
            user_order[0][0].move_mouse(400,20,speped=.5)

            feinter.wait_for_end_of_round_dialog()
            
            if feinter.is_idle():
                inFight = False
            if feinter.find_button('done'):
                inFight = False
        #print("Battle 1 has ended")
        feinter.wait(.5)

        clear_dialog([feinter, hitter, blader])

        feinter.hold_key('w', random.uniform(.1, .2))
        blader.hold_key('w', random.uniform(.1, .2))

        time.sleep(1)

        threads = []

        t = Thread(target=hitter.hold_key, kwargs=dict(key='w', holdtime=3.604))
        threads.append(t)

        arr1 , arr2, arr3 = ['a','d','a'],[0.767,0.175,0.17],[0.189,1.609,2.481]

        t = Thread(target=hitter.navigate_keys, args=(arr1,arr2,arr3))
        threads.append(t)

        # Start all threads
        for x in threads:
            x.start()

        # Wait for all of them to finish
        for x in threads:
            x.join()

        threads = []

        feinter.wait(.5)
        clear_dialog([feinter, hitter, blader])

        #walk_to_next_battle("feinter", 2)

        threads = []

        t = Thread(target=hitter.hold_key, kwargs=dict(key='w', holdtime=5.5))
        threads.append(t)

        arr1 , arr2, arr3 = ['a','d','d'],[0.742,0.742,0.832],[0.14,2.361,5.427]

        t = Thread(target=hitter.navigate_keys, args=(arr1,arr2,arr3))
        threads.append(t)

        # Start all threads
        for x in threads:
            x.start()

        # Wait for all of them to finish
        for x in threads:
            x.join()

        threads = []

        #TP Other users
        feinter.teleport_to_friend('hitter.png')
        blader.teleport_to_friend('hitter.png').wait(random.uniform(2, 3))

        #Enter Next Fight
        feinter.hold_key('w', random.uniform(.7, .9))
        blader.hold_key('w', random.uniform(1.5, 1.6))
        hitter.hold_key('w', random.uniform(1.5, 1.6))

        feinter.wait_for_next_turn()

        inFight = True
        battle_round = 0

        while inFight:
            battle_round += 1
            print_rount_count(ROUND_COUNT, battle_round, failed_runs)
            
            random.shuffle(user_order)

            user_order[0][0].catacombs_detritus_attack(wizard_type = user_order[0][1], boss_pos = boss_pos, boss_battle=False)
            user_order[1][0].move_mouse(400,20,speped=.5)
            user_order[1][0].catacombs_detritus_attack(wizard_type = user_order[1][1], boss_pos = boss_pos, boss_battle=False)
            user_order[2][0].move_mouse(400,20,speped=.5)
            user_order[2][0].catacombs_detritus_attack(wizard_type = user_order[2][1], boss_pos = boss_pos, boss_battle=False)
            user_order[0][0].move_mouse(400,20,speped=.5)

            feinter.wait_for_end_of_round_dialog()
            if feinter.is_idle():
                inFight = False
            if feinter.find_button('done'):
                inFight = False
        #print("Battle 2 has ended")
        feinter.wait(.5)

        clear_dialog([feinter, hitter, blader])

        threads = []

        t = Thread(target=feinter.hold_key, kwargs=dict(key='w', holdtime=3.367))
        threads.append(t)

        arr1 , arr2, arr3 = ['d'],[0.336],[2.721]

        t = Thread(target=feinter.navigate_keys, args=(arr1,arr2,arr3))
        threads.append(t)

        # Start all threads
        for x in threads:
            x.start()

        # Wait for all of them to finish
        for x in threads:
            x.join()
        
        time.sleep(.5)

        feinter.press_key('x').wait(.2)
        clear_dialog([feinter])


        feinter.hold_key('d',0.7)

        feinter.hold_key('w',1.5)

        
        # Wait for loading
        await_finished_loading([feinter])
        
        # Move forward just a tad
        feinter.hold_key('w', .7).wait(.2)

        clear_dialog([feinter, hitter, blader])

        hitter.teleport_to_friend('feinter.png')
        blader.teleport_to_friend('feinter.png').wait(.3)

        await_finished_loading([blader])

        feinter.hold_key('w', random.uniform(1.3, 1.4))
        blader.hold_key('w', random.uniform(1.2, 1.3))
        hitter.hold_key('w', random.uniform(1.3, 3))

        # Begin Fight Section
        feinter.wait_for_next_turn()
        
        boss_pos = feinter.get_enemy_pos('sun.png')
        #print('Boss at pos', boss_pos)
        
        inFight = True
        Fail = False
        battle_round = 0

        while inFight:
            battle_round += 1
            print_rount_count(ROUND_COUNT, battle_round, failed_runs)

            
            if(battle_round >= 5):
                #print("Boss Battle failed")
                #print("Exiting...")   
                failed_runs = failed_runs+1
                # Restarts program on fail
                logout_failsafe([feinter, hitter, blader])
                spawn_program_and_die(['python', 'farm_catacombs_detritus_three.py',str(ROUND_COUNT), str(failed_runs), str(timeout_fails),str(PROGRAM_START_TIME)]) 
                break

            random.shuffle(user_order)

            user_order[0][0].catacombs_detritus_attack(wizard_type = user_order[0][1], boss_pos = boss_pos, boss_battle=True)
            user_order[1][0].move_mouse(400,20,speped=.5)
            user_order[1][0].catacombs_detritus_attack(wizard_type = user_order[1][1], boss_pos = boss_pos, boss_battle=True)
            user_order[2][0].move_mouse(400,20,speped=.5)
            user_order[2][0].catacombs_detritus_attack(wizard_type = user_order[2][1], boss_pos = boss_pos, boss_battle=True)
            user_order[0][0].move_mouse(400,20,speped=.5)

            feinter.wait_for_end_of_round_dialog()
            if feinter.is_idle():
                inFight = False
            if feinter.find_button('done'):
                inFight = False

        #print("Exiting...")
        # Random User logout
        user_order[0][0].logout()

        await_finished_loading([user_order[0][0]])

        user_order[1][0].teleport_to_friend(user_order[0][1])
        user_order[2][0].teleport_to_friend(user_order[0][1]).wait(random.uniform(1, 3))
        
        #print('Successfully exited the dungeon')
        print_time(time.time() - START_TIME)



# Threading for afk timeout
afk_thread = Thread(target=afk_timeout_failsafe, args=())
metric_thread = Thread(target=display_metrics,args=())
afk_thread.start()


try:
    sp.start()
    metric_thread.start()
    time.sleep(2)
    main()
except KeyboardInterrupt:
    
    sp.write('Interrupted')
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)