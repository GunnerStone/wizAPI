import enum
from api import *
import time
import math
import random
import sys
import pathlib


main = api()

main.register_windows(count = 3)
main.load_config(pathlib.Path().absolute(), "farm_generic")

while True:
    main.start_time = time.time()
    main.round_count += 1
    main.print_separator('ROUND', str(main.round_count))

    main.quick_sell()

    """ Check health and use potion if necessary """
    for i, wizard in enumerate(main.wizards):
        wizard.win.use_potion_if_needed(refill = True, teleport_to_wizard = main.wizards[ i + 1 if (i != len(main.wizards) - 1) else i - 1].icon, health_percent = 60)

    # """ Attempt to enter the dungeon """
    time.sleep(1)

    for wizard in main.wizards: 
        while not wizard.win.enter_dungeon_dialog():
            time.sleep(1)

    """ Allows for health regen """
    time.sleep(1)

    random.shuffle(main.wizards)

    # Enter Dungeon
    for wizard in main.wizards:
        wizard.win.press_key('x').wait(random.uniform(0.5, 1.5))

    main.await_finished_loading()

    print('All players have entered the dungeon')

    main.clear_dialog()

    """ Run into battle """
    for wizard in main._wizards:
        wizard.win.hold_key('w', random.uniform(0.5, 0.5))

    main.clear_dialog()

    while (not main.wizards[0].win.is_turn_to_play()):
        for wizard in main._wizards:
            wizard.win.hold_key('w', random.uniform(1.2, 1.3))

    #remove auto mouse off of cards
    for i in range(2):
        for wizard in main._wizards:
            wizard.win.hold_key('s', random.uniform(0.1, 0.15))

    #if no boss make it 1
    if ('boss' not in main.config["config"]):
        boss_pos = 1
    else:
        boss_pos = main.wizards[0].win.get_enemy_pos(main.wizards[0].win.config["config"]["boss"]["school"] + '.png')

    print('Boss at pos', boss_pos)

    inFight = True
    battle_round = 0

    while inFight:
        battle_round += 1
        print('-------- Battle round', battle_round, '--------')
        
        random.shuffle(main.wizards)
        
        for wizard in main.wizards:
            main.attack(wizard, boss_pos)

        main.wizards[0].win.set_active()
        main.wizards[0].win.wait_for_end_of_round_dialog()
        if main.wizards[0].win.is_idle():
            inFight = False
        if main.wizards[0].win.find_button('more'):
            inFight = False
        if main.wizards[0].win.find_button('done'):
            inFight = False

    main.clear_dialog()
    print("Battle has ended")

    print("Exiting...")
    
    random.shuffle(main.wizards)
    
    driver_random = main.wizards
    driver = driver_random[0]

    """ Wait should be between 0.2 - 1.0 based on individual load speeds """
    driver.win.logout(isDungeon=True)

    driver.win.wait_pet_loading()
    print('Successfully exited the dungeon')

    driver_random[1].win.teleport_to_friend(driver_random[0].icon)
    driver_random[2].win.teleport_to_friend(driver_random[0].icon)

    main.print_time(time.time() - main.start_time)
