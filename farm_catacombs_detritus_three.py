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
user_order = [[feinter, 'feinter.png'], [hitter, 'hitter.png'], [blader, 'blader.png']]
boss_pos = feinter.get_enemy_pos('sun.png')

while True:
    START_TIME = time.time()
    ROUND_COUNT += 1
    print_separator('ROUND', str(ROUND_COUNT))

    # feinter.mark_location()

    """ Quick sell every 25 rounds"""
    if(ROUND_COUNT % 3 == 0):
        feinter.quick_sell(False, False)
        hitter.quick_sell(False, False)
        blader.quick_sell(False, False)

    """ Attempt to enter the dungeon """
    time.sleep(1)

    while not feinter.enter_dungeon_dialog():
        time.sleep(1)

    while not blader.enter_dungeon_dialog():
        time.sleep(1)

    while not hitter.enter_dungeon_dialog():
        time.sleep(1)

    random.shuffle(user_order)

    user_order[0][0].press_key('x').wait(random.uniform(0.5, 1.5))
    user_order[1][0].press_key('x').wait(random.uniform(0.2, 1.7))
    user_order[2][0].press_key('x').wait(random.uniform(0.3, 1.3))

    await_finished_loading([feinter, hitter, blader])

    print('All players have entered the dungeon')

    """ Check health and use potion if necessary """
    user_order[0][0].use_potion_if_needed()
    user_order[1][0].use_potion_if_needed()
    user_order[2][0].use_potion_if_needed()

    """ Run into first battle """
    feinter.hold_key('w', random.uniform(2, 3)).wait(1)
    feinter.clear_dialog(1)
    blader.clear_dialog(1)
    hitter.clear_dialog(1)
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

    feinter.clear_dialog(1)
    blader.clear_dialog(1)
    hitter.clear_dialog(1)

    # Move one user to next fight
    hitter.wait(2).face_arrow()
    while hitter.find_button('done') is not True:
        hitter.hold_key('w', 1)

    #Clears Belgrim Dialogue
    feinter.clear_dialog(1)
    blader.clear_dialog(1)
    hitter.clear_dialog(1)

    hitter.wait(2).hold_key('a', 0.7).wait(.2)
    hitter.wait(2).hold_key('w', 2.8).wait(.2)
    hitter.wait(2).hold_key('d', .6).wait(.2)
    hitter.wait(2).hold_key('w', 2.8).wait(.2)
    hitter.wait(2).hold_key('d', .6).wait(.2)

    #TP Other users
    feinter.teleport_to_friend('hitter.png')
    blader.teleport_to_friend('hitter.png').wait(random.uniform(1, 3))

    #Enter Next Fight
    feinter.hold_key('w', random.uniform(.2, .3))
    blader.hold_key('w', random.uniform(1.3, 1.4))
    hitter.hold_key('w', random.uniform(1.3, 1.4))

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

    feinter.clear_dialog(1)
    blader.clear_dialog(1)
    hitter.clear_dialog(1)

    # Move one user to next fight
    hitter.wait(2).face_arrow().wait(.3)
    hitter.hold_key('a', .01)
    hitter.hold_key('w', 3).wait(.2)
    hitter.press_key('x').wait(.2)
    # Goes through 5 dialog boxes
    hitter.clear_dialog(5)
    hitter.wait(.5).face_arrow().wait(.2)
    hitter.hold_key('a', .01)
    hitter.hold_key('w', 2.1)
    # Wait for loading
    await_finished_loading([hitter])
    
    # Move forward just a tad
    hitter.hold_key('w', .7).wait(.2)

    feinter.clear_dialog(6)
    blader.clear_dialog(6)
    hitter.clear_dialog(6)

    feinter.teleport_to_friend('hitter.png')
    blader.teleport_to_friend('hitter.png').wait(.3)

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
    
    # feinter.recall_location()
    feinter.logout()

    await_finished_loading([feinter])
    print('Successfully exited the dungeon')

    hitter.teleport_to_friend('feinter.png')
    blader.teleport_to_friend('feinter.png').wait(random.uniform(1, 3))

    print_time(time.time() - START_TIME)
