from wizAPI import *
import time
import math
import random

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

def await_finished_loading(windows):
    for w in windows:
        while not w.is_DS_loading():
            time.sleep(.2)

    for w in windows:
        while not w.is_idle():
            time.sleep(.5)


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


ROUND_COUNT = 0
user_order = [[feinter, 'friend_feinter.png'], [hitter, 'friend_hitter.png'], [blader, 'friend_blader.png']]

while True:
    START_TIME = time.time()
    ROUND_COUNT += 1
    print_separator('ROUND', str(ROUND_COUNT))

    """ Quick sell every 10 rounds"""
    if(ROUND_COUNT % 10 == 0):
        feinter.quick_sell(False, False)
        hitter.quick_sell(False, False)
        blader.quick_sell(False, False)

    """ Attempt to enter the dungeon """
    time.sleep(1)

    while not feinter.enter_dungeon_dialog():
        (feinter.hold_key('w', 1.5)
         .hold_key('s', 2)
         .wait(1.5))

    while not blader.enter_dungeon_dialog():
        time.sleep(1)

    while not hitter.enter_dungeon_dialog():
        time.sleep(1)

    """ Allows for health regen """
    time.sleep(1)

    random.shuffle(user_order)

    user_order[0][0].press_key('x').wait(random.uniform(0.5, 1.5))
    user_order[1][0].press_key('x').wait(random.uniform(0.2, 1.7))
    user_order[2][0].press_key('x').wait(random.uniform(0.3, 1.3))

    await_finished_loading([feinter, hitter, blader])

    print('All players have entered the dungeon')

    """ Check health and use potion if necessary """
    feinter.use_potion_if_needed()
    hitter.use_potion_if_needed()
    blader.use_potion_if_needed()

    """ Run into battle """
    feinter.hold_key('w', random.uniform(1.4, 1.55))
    blader.hold_key('w', random.uniform(1.4, 1.55))
    hitter.hold_key('w', random.uniform(2, 3))

    feinter.wait_for_next_turn()

    boss_pos = feinter.get_enemy_pos('bossmatch.png')
    print('Boss at pos', boss_pos)

    friend_pos = feinter.get_friendly_pos('star.png')
    print('Boss at pos', boss_pos)

    inFight = True
    battle_round = 0

    while inFight:
        battle_round += 1
        print('-------- Battle round', battle_round, '--------')
        
        random.shuffle(user_order)

        user_order[0][0].lm_attack(wizard_type = user_order[0][1], boss_pos = boss_pos)
        user_order[1][0].lm_attack(wizard_type = user_order[1][1], boss_pos = boss_pos)
        user_order[2][0].lm_attack(wizard_type = user_order[2][1], boss_pos = boss_pos)

        feinter.wait_for_end_of_round()
        if feinter.is_idle():
            inFight = False
    print("Battle has ended")

    print("Exiting...")
    
    random.shuffle(user_order)
    
    driver_random = user_order
    driver = driver_random[0][0]

    """ Wait should be between 0.2 - 1.0 based on individual load speeds """
    driver.wait(2).face_arrow().hold_key('w', 3).wait(.2)

    if not driver.is_DS_loading():
        """ Retry exiting """
        time.sleep(2)
        while not driver.is_DS_loading():
            driver.hold_key('s', 3)
            if driver.is_DS_loading():
                break
            driver.face_arrow()
            if driver.is_DS_loading():
                break
            driver.hold_key('w', 3.5).wait(2)

    await_finished_loading([driver])
    print('Successfully exited the dungeon')

    driver.hold_key('s', random.uniform(0.6, 0.9)).wait(random.uniform(0.8, 2))

    driver_random[1][0].teleport_to_friend(driver_random[0][1])
    driver_random[2][0].teleport_to_friend(driver_random[0][1]).wait(random.uniform(4, 6))

    print_time(time.time() - START_TIME)
