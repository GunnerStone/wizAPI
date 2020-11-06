from wizAPI import *
import time
import math

""" Register windows """
try:
    blader = wizAPI().register_window(nth=2)
    hitter = wizAPI().register_window(nth=1)
    feinter = wizAPI().register_window(nth=0)
except IndexError:
    print('You need 3 wizard101 accounts to run this particular bot. 2 or less accounts detected')
    exit()

""" compare x positions of windows to make sure 'hitter' is the farthest left, and 'feinter' is the farthest right, and 'blader' is middle """
if (hitter.get_window_rect()[0] > feinter.get_window_rect()[0]):
    # Switch them, if not
    hitter, feinter = feinter, hitter

if(hitter.get_window_rect()[0] > blader.register_window()[0]):
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

while True:
    START_TIME = time.time()
    ROUND_COUNT += 1
    print_separator('ROUND', str(ROUND_COUNT))

    """ Attempt to enter the dungeon """
    time.sleep(1)
    feinter.hold_key('s', .8).wait(1)

    while not feinter.enter_dungeon_dialog():
        (feinter.hold_key('w', 1.5)
         .hold_key('s', 2)
         .wait(1.5))

    hitter.teleport_to_friend('friend_match.png').wait(4)
    blader.teleport_to_friend('friend_match.png').wait(4)

    while not hitter.enter_dungeon_dialog():
        time.sleep(1)

    while not blader.enter_dungeon_dialog():
        time.sleep(1)

    """ Allows for health regen """
    time.sleep(1)

    feinter.press_key('x')
    hitter.press_key('x')
    blader.press_key('x')

    await_finished_loading([feinter, hitter, blader])

    print('All players have entered the dungeon')

    """ Check health and use potion if necessary """
    feinter.use_potion_if_needed()
    hitter.use_potion_if_needed()
    blader.use_potion_if_needed()

    """ Run into battle """
    feinter.hold_key('w', 1.5)
    blader.hold_key('w', 3)
    hitter.hold_key('w', 3)

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

        """ Feinter plays """
        # Check to see if deck is crowded with unusable spells
        cn = len(feinter.find_unusable_spells())
        if cn > 2:
            feinter.discard_unusable_spells(cn)

        # Play
        if battle_round % 2 == 1:
            if feinter.enchant('feint', 'potent'):
                feinter.cast_spell('feint-potent').at_target(boss_pos)

            elif feinter.find_spell('feint'):
                feinter.cast_spell('feint').at_target(boss_pos)

            else:
                feinter.pass_turn()
        else:
            if feinter.find_spell('feint'):
                feinter.cast_spell('feint').at_target(boss_pos)

            elif feinter.find_spell('feint-potent'):
                feinter.cast_spell('feint-potent').at_target(boss_pos)

            else:
                feinter.pass_turn()

        """ Blader plays """
        # Check to see if deck is crowded with unusable spells
        cn = len(blader.find_unusable_spells())
        if cn > 2:
            blader.discard_unusable_spells(cn)

        # Play
        if battle_round % 2 == 1:
            if feinter.enchant('feint', 'potent'):
                blader.cast_spell('feint-potent').at_target(boss_pos)

            elif blader.find_spell('feint'):
                blader.cast_spell('feint').at_target(boss_pos)

            else:
                blader.pass_turn()
        else:
            if blader.find_spell('feint'):
                blader.cast_spell('feint').at_target(boss_pos)

            elif blader.find_spell('feint-potent'):
                blader.cast_spell('feint-potent').at_target(boss_pos)

            else:
                blader.pass_turn()

        """ Hitter plays """
        # Check to see if deck is crowded with unusable spells
        cn = len(hitter.find_unusable_spells())
        # Discard the spells
        if cn > 2:
            hitter.discard_unusable_spells(cn)

        # Play
        if (hitter.find_spell('glowbug-squall', threshold=0.05, max_tries=3) and
                hitter.enchant('glowbug-squall', 'epic')):
            hitter.find_spell('glowbug-squall-enchanted', max_tries=4)
            hitter.cast_spell('glowbug-squall-enchanted')

        elif hitter.find_spell('tempest-enchanted', max_tries=1):
            hitter.cast_spell('tempest-enchanted')

        elif hitter.enchant('tempest', 'epic'):
            hitter.find_spell('tempest-enchanted', max_tries=4)
            hitter.cast_spell('tempest-enchanted')

        elif hitter.find_spell('glowbug-squall-enchanted', threshold=.05):
            hitter.cast_spell('glowbug-squall-enchanted')

        elif hitter.find_spell('glowbug-squall', threshold=.05):
            hitter.cast_spell('glowbug-squall')

        else:
            hitter.pass_turn()

        feinter.wait_for_end_of_round()
        if feinter.is_idle():
            inFight = False
    print("Battle has ended")

    print("Exiting...")
    feinter.wait(2).face_arrow().hold_key('w', 3).wait(1)

    if not feinter.is_DS_loading():
        """ Retry exiting """
        time.sleep(2)
        while not feinter.is_DS_loading():
            feinter.hold_key('s', 3)
            if feinter.is_DS_loading():
                break
            feinter.face_arrow()
            if feinter.is_DS_loading():
                break
            feinter.hold_key('w', 3.5).wait(2)

    await_finished_loading([feinter])
    print('Successfully exited the dungeon')
    print_time(time.time() - START_TIME)
