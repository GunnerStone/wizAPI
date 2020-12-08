from wizAPI import *
import time
import math
import random

""" Register windows """
try:
    hitter = wizAPI().register_window(nth=0) # Furthest Right 
except IndexError:
    print('You need 3 wizard101 accounts to run this particular bot. 2 or less accounts detected')
    exit()

def await_finished_loading(windows):
    for w in windows:
        while not w.is_logo_bottom_left_or_right_loading():
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

while True:
    START_TIME = time.time()
    ROUND_COUNT += 1
    print_separator('ROUND', str(ROUND_COUNT))

    # """ Quick sell at bazaar every 10 rounds"""
    if(ROUND_COUNT % 10 == 0):
        hitter.quick_sell(sell_crown_items=False, sell_jewels=False)

    # """ Attempt to enter the dungeon """
    time.sleep(1)

    """ Allows for health regen """
    time.sleep(1)

    # Enter Dungeon
    hitter.hold_key('s', .2).wait(random.uniform(0.5, 1))
    hitter.hold_key('w', .4).wait(random.uniform(1.1, 1.2))

    await_finished_loading([hitter])

    print('All players have entered the dungeon')

    """ Run into battle """
    hitter.hold_key('w', random.uniform(2, 3))

    hitter.wait_for_next_turn()

    boss_pos = hitter.get_enemy_pos('storm.png')
    print('Boss at pos', boss_pos)

    inFight = True
    battle_round = 0

    while inFight:
        battle_round += 1
        print('-------- Dungeon Round:', ROUND_COUNT,', Battle Round:', battle_round, '--------')
        
        """ Hitter plays """
        # Check to see if deck is crowded with unusable spells
        cn = len(hitter.find_unusable_spells())
        # Discard the spells
        if cn > 2:
            hitter.discard_unusable_spells(cn)

        # Play
        if hitter.find_spell('Storm', 'extract_tempest', max_tries=1):
            hitter.cast_spell('Storm', 'extract_tempest')

        elif hitter.enchant('Storm', 'tempest', 'Myth', 'extract_undead'):
            hitter.find_spell('Storm', 'extract_tempest', max_tries=4)
            hitter.cast_spell('Storm', 'extract_tempest')


        else:
            hitter.pass_turn()

        hitter.wait_for_end_of_round()
        if hitter.is_idle():
            inFight = False
    print("Battle has ended")

    print("Exiting...")
    

    """ Wait should be between 0.2 - 1.0 based on individual load speeds """
    hitter.logout(isDungeon=True)

    await_finished_loading([hitter])
    print('Successfully exited the dungeon')

    print_time(time.time() - START_TIME)
