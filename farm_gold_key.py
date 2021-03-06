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

str_buffer = "FML Gold Key 3p Bot Running"
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
            feinter.quick_sell(sell_crown_items=False, sell_jewels=False, sell_housing_items=False)
            hitter.quick_sell(sell_crown_items=False, sell_jewels=False, sell_housing_items=False)
            blader.quick_sell(sell_crown_items=False, sell_jewels=False, sell_housing_items=False)

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
        feinter.hold_key('w', 1.4).wait(2)
        clear_dialog([feinter, hitter, blader])
        blader.hold_key('w', 1.4)
        hitter.hold_key('w', 1.4)

        feinter.hold_key('w', random.uniform(2.9, 3))
        blader.hold_key('w', random.uniform(2.9, 3))
        hitter.hold_key('w', random.uniform(2.9, 3))

        feinter.hold_key('w', random.uniform(1, 1.2))
        blader.hold_key('w', random.uniform(1, 1.2))
        hitter.hold_key('w', random.uniform(1, 1.2))

        feinter.wait_for_next_turn()

        inFight = True
        battle_round = 0

        boss_pos = feinter.get_enemy_pos('life.png')
        
        while inFight:
            battle_round += 1
            print_rount_count(ROUND_COUNT, battle_round, failed_runs)
            
            random.shuffle(user_order)

            user_order[0][0].gold_key_attack(wizard_type = user_order[0][1], boss_pos = boss_pos)
            user_order[1][0].gold_key_attack(wizard_type = user_order[1][1], boss_pos = boss_pos)
            user_order[2][0].gold_key_attack(wizard_type = user_order[2][1], boss_pos = boss_pos)

            feinter.wait_for_end_of_round_dialog()
            
            if feinter.is_idle():
                inFight = False
            if feinter.find_button('done'):
                inFight = False
        #print("Battle 1 has ended")
        feinter.wait(.5)
 
        # Random User logout
        user_order[0][0].logout(isDungeon=True)

        await_finished_loading([user_order[0][0]])

        user_order[1][0].teleport_to_friend(user_order[0][1])
        user_order[2][0].teleport_to_friend(user_order[0][1]).wait(random.uniform(1, 3))
        
        #print('Successfully exited the dungeon')
        print_time(time.time() - START_TIME)

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