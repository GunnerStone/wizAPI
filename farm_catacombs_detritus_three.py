from wizAPI import *
import time
import math
import random
from threading import Thread

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
        while not w.is_logo_bottom_right_loading() or is_logo_bottom_left_loading(): # Looks at either side for logo - update for wiz loading screen update
            time.sleep(.2)

    for w in windows:
        while not w.is_idle():
            time.sleep(.5)

def clear_dialog(windows, total_dialog):
    for w in windows:
        w.clear_dialog(total_dialog)

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

# All code for battle approaches
def walk_to_next_battle(wiz, battle):
    threads = []

    if(battle == 1):
        if(wiz == "all"):
            feinter.hold_key('w', random.uniform(2.2, 3)).wait(1)
            clear_dialog([feinter, hitter, blader], 1)
            blader.hold_key('w', random.uniform(2.3, 2.5))
            hitter.hold_key('w', random.uniform(2, 2.5))

            feinter.hold_key('w', random.uniform(1.3, 1.4))
            blader.hold_key('w', random.uniform(1.2, 1.3))
            hitter.hold_key('w', random.uniform(1.3, 3))

    if(battle == 2):
        if(wiz == "feinter"):
            t = Thread(target=feinter.hold_key, args=('w', 4.114, 0))
            threads.append(t)

            t = Thread(target=feinter.hold_key, args=('a', 0.119, 0.806))
            threads.append(t)

            t = Thread(target=feinter.hold_key, args=('a', 0.146, 1.388))
            threads.append(t)

            t = Thread(target=feinter.hold_key, args=('d', 0.035, 2.48))
            threads.append(t)
            
            for x in threads:
                x.start()

            # Wait for all of them to finish
            for x in threads:
                x.join()

            feinter.wait(.5)

            clear_dialog([feinter, hitter, blader], 1)

            threads = []

            t = Thread(target=feinter.hold_key, args=('w', 5.462, 0))
            threads.append(t)

            t = Thread(target=feinter.hold_key, args=('a', 0.693, 0.668))
            threads.append(t)

            t = Thread(target=feinter.hold_key, args=('d', 0.508, 2.848))
            threads.append(t)

            t = Thread(target=feinter.hold_key, args=('d', 0.118, 3.518))
            threads.append(t)

        if(wiz == "hitter"):
            # # Move one user to next fight
            # hitter.wait(2).face_arrow()
            # while hitter.find_button('done') is not True:
            #     hitter.hold_key('w', 1)

            # # Walking Sequence from Battle 1 to Battle 2
            # hitter.wait(2).hold_key('a', 0.7).wait(.2)
            # hitter.wait(2).hold_key('w', 2.8)
            # hitter.wait(2).hold_key('d', .6)
            # hitter.wait(2).hold_key('w', 2.8)
            # hitter.wait(2).hold_key('d', .6)
            t = Thread(target=hitter.hold_key, args=('w', 3.4, 0))
            threads.append(t)

            t = Thread(target=hitter.hold_key, args=('a', 0.7, 0.9))
            threads.append(t)

            t = Thread(target=hitter.hold_key, args=('d', 0.1, 2.0))
            threads.append(t)

            for x in threads:
                x.start()

            # Wait for all of them to finish
            for x in threads:
                x.join()

            hitter.wait(.5)

            clear_dialog([feinter, hitter, blader], 1)


    # Start all threads
    for x in threads:
        x.start()

    # Wait for all of them to finish
    for x in threads:
        x.join()

ROUND_COUNT = 0
user_order = [[feinter, 'feinter.png'], [hitter, 'hitter.png'], [blader, 'blader.png']]
boss_pos = feinter.get_enemy_pos('sun.png')

# Thread Init - Used for movement sequences
threads = []

while True:
    START_TIME = time.time()
    ROUND_COUNT += 1
    print_separator('ROUND', str(ROUND_COUNT))

    # feinter.mark_location()

    

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

    """ Check health and use potion if necessary """
    user_order[0][0].use_potion_if_needed(refill=True, teleport_to_wizard=user_order[1][1], health_percent=80)
    user_order[1][0].use_potion_if_needed(refill=True, teleport_to_wizard=user_order[0][1], health_percent=80)
    user_order[2][0].use_potion_if_needed(refill=True, teleport_to_wizard=user_order[1][1], health_percent=80)

    user_order[0][0].press_key('x').wait(random.uniform(0.5, 1.5))
    user_order[1][0].press_key('x').wait(random.uniform(0.2, 1.7))
    user_order[2][0].press_key('x').wait(random.uniform(0.3, 1.3))

    await_finished_loading([feinter, hitter, blader])

    print('All players have entered the dungeon')

    """ Run into first battle """
    #walk_to_next_battle("all", 1)
    feinter.hold_key('w', random.uniform(2.2, 3)).wait(1.5)
    clear_dialog([feinter, hitter, blader], 1)
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
        print('-------- Battle round', battle_round, '--------')
        
        random.shuffle(user_order)

        user_order[0][0].catacombs_detritus_attack(wizard_type = user_order[0][1], boss_pos = boss_pos, boss_battle=False)
        user_order[1][0].catacombs_detritus_attack(wizard_type = user_order[1][1], boss_pos = boss_pos, boss_battle=False)
        user_order[2][0].catacombs_detritus_attack(wizard_type = user_order[2][1], boss_pos = boss_pos, boss_battle=False)

        feinter.wait_for_end_of_round_dialog()
        
        if feinter.is_idle():
            inFight = False
        if feinter.find_button('done'):
            inFight = False
    print("Battle 1 has ended")
    feinter.wait(.5)

    clear_dialog([feinter, hitter, blader], 1)

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

    clear_dialog([feinter, hitter, blader], 1)

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
    blader.hold_key('w', random.uniform(1.3, 1.4))
    hitter.hold_key('w', random.uniform(1.4, 1.5))

    feinter.wait_for_next_turn()

    inFight = True
    battle_round = 0

    while inFight:
        battle_round += 1
        print('-------- Battle round', battle_round, '--------')
        
        random.shuffle(user_order)

        user_order[0][0].catacombs_detritus_attack(wizard_type = user_order[0][1], boss_pos = boss_pos, boss_battle=False)
        user_order[1][0].catacombs_detritus_attack(wizard_type = user_order[1][1], boss_pos = boss_pos, boss_battle=False)
        user_order[2][0].catacombs_detritus_attack(wizard_type = user_order[2][1], boss_pos = boss_pos, boss_battle=False)

        feinter.wait_for_end_of_round_dialog()
        if feinter.is_idle():
            inFight = False
        if feinter.find_button('done'):
            inFight = False
    print("Battle 2 has ended")
    feinter.wait(.5)

    clear_dialog([feinter, hitter, blader], 1)

    """
    # Move one user to next fight
    hitter.wait(2).face_arrow().wait(.3)
    hitter.hold_key('a', .01)
    hitter.hold_key('w', 3).wait(.2)
    hitter.press_key('x').wait(.2)
    """

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
    clear_dialog([feinter],5)


    feinter.hold_key('d',0.7)

    feinter.hold_key('w',1.5)

    
    # Wait for loading
    await_finished_loading([feinter])
    
    # Move forward just a tad
    feinter.hold_key('w', .7).wait(.2)

    clear_dialog([feinter, hitter, blader], 6)

    hitter.teleport_to_friend('feinter.png')
    blader.teleport_to_friend('feinter.png').wait(.3)

    await_finished_loading([blader])

    feinter.hold_key('w', random.uniform(1.3, 1.4))
    blader.hold_key('w', random.uniform(1.2, 1.3))
    hitter.hold_key('w', random.uniform(1.3, 3))

    # Begin Fight Section
    feinter.wait_for_next_turn()
    
    boss_pos = feinter.get_enemy_pos('sun.png')
    print('Boss at pos', boss_pos)
    
    inFight = True
    battle_round = 0

    while inFight:
        battle_round += 1
        print('-------- Battle round', battle_round, '--------')
        
        random.shuffle(user_order)

        user_order[0][0].catacombs_detritus_attack(wizard_type = user_order[0][1], boss_pos = boss_pos, boss_battle=True)
        user_order[1][0].catacombs_detritus_attack(wizard_type = user_order[1][1], boss_pos = boss_pos, boss_battle=True)
        user_order[2][0].catacombs_detritus_attack(wizard_type = user_order[2][1], boss_pos = boss_pos, boss_battle=True)

        feinter.wait_for_end_of_round_dialog()
        if feinter.is_idle():
            inFight = False
        if feinter.find_button('done'):
            inFight = False
    print("Boss Battle")
    
    print("Exiting...")

    # Random User logout
    user_order[0][0].logout()

    await_finished_loading([user_order[0][0]])
    print('Successfully exited the dungeon')

    user_order[1][0].teleport_to_friend(user_order[0][1])
    user_order[2][0].teleport_to_friend(user_order[0][1]).wait(random.uniform(1, 3))

    print_time(time.time() - START_TIME)
