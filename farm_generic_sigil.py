from wizAPI import *
import time
import math
import random
import sys

""" Register windows """
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

def clear_dialog(windows):
    for w in windows:
        w.clear_dialog()

def await_finished_loading(windows):
    for w in windows:
        while w.is_pet_icon_visible():
            time.sleep(.2)
    
    for w in windows:
        while ((not w.is_pet_icon_visible()) and (not w.find_button('more')) and (not w.find_button('done'))):
            time.sleep(.2)


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


def print_time(timer):
    minutes = math.floor(timer/60)
    seconds = math.floor(timer % 60)
    print('Round lasted {} minutes and {} seconds.'.format(minutes, seconds))

# Global vars
if len(sys.argv) == 2:
    HITTING_SCHOOL = str(sys.argv[1]).lower()
    ROUND_COUNT = 0
    failed_runs = 0
    timeout_fails = 0
    # ROUND_COUNT = int(sys.argv[1])
    # failed_runs = int(sys.argv[2])
    # timeout_fails = int(sys.argv[3])
    # PROGRAM_START_TIME = int(float(sys.argv[4]))
else:
    HITTING_SCHOOL = "storm"
    ROUND_COUNT = 0
    failed_runs = 0
    timeout_fails = 0

user_order = [[feinter, 'feinter.png'], [hitter, 'hitter.png'], [blader, 'blader.png']]

while True:
    START_TIME = time.time()
    ROUND_COUNT += 1
    print_separator('ROUND', str(ROUND_COUNT))

    """ Quick sell every 10 rounds"""
    if(ROUND_COUNT % 10 == 0):
        feinter.quick_sell(False, False)
        hitter.quick_sell(False, False)
        blader.quick_sell(False, False)

    """ Check health and use potion if necessary """
    user_order[0][0].use_potion_if_needed(refill=True, teleport_to_wizard=user_order[1][1], health_percent=60)
    user_order[1][0].use_potion_if_needed(refill=True, teleport_to_wizard=user_order[0][1], health_percent=60)
    user_order[2][0].use_potion_if_needed(refill=True, teleport_to_wizard=user_order[1][1], health_percent=60)

    # """ Attempt to enter the dungeon """
    time.sleep(1)

    while not feinter.enter_dungeon_dialog():
        time.sleep(1)

    while not blader.enter_dungeon_dialog():
        time.sleep(1)

    while not hitter.enter_dungeon_dialog():
        time.sleep(1)

    """ Allows for health regen """
    time.sleep(1)

    random.shuffle(user_order)

    # Enter Dungeon
    user_order[0][0].press_key('x').wait(random.uniform(0.5, 1.5))
    user_order[1][0].press_key('x').wait(random.uniform(0.2, 1.7))
    user_order[2][0].press_key('x').wait(random.uniform(0.3, 1.3))

    await_finished_loading([feinter, hitter, blader])

    print('All players have entered the dungeon')

    clear_dialog([feinter,hitter,blader])

    """ Run into battle """
    feinter.hold_key('w', random.uniform(0.5, 0.5))
    blader.hold_key('w', random.uniform(0.5, 0.5))
    hitter.hold_key('w', random.uniform(0.5, 0.5))

    clear_dialog([feinter, hitter, blader])


    while (not feinter.is_turn_to_play()):
        feinter.hold_key('w', random.uniform(1.2, 1.3))
        blader.hold_key('w', random.uniform(1.2, 1.3))
        hitter.hold_key('w', random.uniform(1.2, 1.3))

    #remove auto mouse off of cards
    feinter.hold_key('s', random.uniform(0.1, 0.15))
    blader.hold_key('s', random.uniform(0.1, 0.15))
    hitter.hold_key('s', random.uniform(0.1, 0.15))
    feinter.hold_key('s', random.uniform(0.1, 0.15))
    blader.hold_key('s', random.uniform(0.1, 0.15))
    hitter.hold_key('s', random.uniform(0.1, 0.15))

    # feinter.wait_for_next_turn()

    #boss_pos = feinter.get_enemy_pos('storm.png')
    boss_pos = False
    #if no boss make it 1
    if (not boss_pos):
        boss_pos = 1
    else:
        boss_pos = feinter.get_enemy_pos('fire.png')

    print('Boss at pos', boss_pos)

    inFight = True
    battle_round = 0

    while inFight:
        battle_round += 1
        print('-------- Battle round', battle_round, '--------')
        
        random.shuffle(user_order)
        user_order[0][0].mass_feint_attack(wizard_type = user_order[0][1], boss_pos = boss_pos, hitter=HITTING_SCHOOL)
        user_order[1][0].mass_feint_attack(wizard_type = user_order[1][1], boss_pos = boss_pos, hitter=HITTING_SCHOOL)
        user_order[2][0].mass_feint_attack(wizard_type = user_order[2][1], boss_pos = boss_pos, hitter=HITTING_SCHOOL)

        feinter.set_active()
        feinter.wait_for_end_of_round_dialog()
        if feinter.is_idle():
            inFight = False
        if feinter.find_button('more'):
            inFight = False
        if feinter.find_button('done'):
            inFight = False
    clear_dialog([feinter,blader,hitter])
    print("Battle has ended")

    print("Exiting...")
    
    random.shuffle(user_order)
    
    driver_random = user_order
    driver = driver_random[0][0]

    """ Wait should be between 0.2 - 1.0 based on individual load speeds """
    driver.logout(isDungeon=True)

    await_finished_loading([driver])
    print('Successfully exited the dungeon')

    driver_random[1][0].teleport_to_friend(driver_random[0][1])
    driver_random[2][0].teleport_to_friend(driver_random[0][1])

    print_time(time.time() - START_TIME)