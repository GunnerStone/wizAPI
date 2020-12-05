import win32gui
import pyautogui
import cv2
import time
import numpy
import ctypes


class wizAPI:
    def __init__(self, handle=None):
        self._handle = handle
        self._spell_memory = {}
        self._friends_area = (625, 65, 20, 240)
        self._spell_area = (245, 290, 370, 70)
        self._enemy_area = (68, 26, 650, 35)
        self._friendly_area = (136, 536, 650, 70)
        self._login_area = (307,553+36,187,44)

    def wait(self, s):
        """ Alias for time.sleep() that return self for function chaining """
        time.sleep(s)
        return self

    def register_window(self, name="Wizard101", nth=0):
        """ Assigns the instance to a wizard101 window (Required before using any other API functions) """
        def win_enum_callback(handle, param):
            if name == str(win32gui.GetWindowText(handle)):
                param.append(handle)

        handles = []
        # Get all windows with the name "Wizard101"
        win32gui.EnumWindows(win_enum_callback, handles)
        handles.sort()
        # Assigns the one at index nth
        self._handle = handles[nth]
        return self

    def is_active(self):
        """ Returns true if the window is focused """
        return self._handle == win32gui.GetForegroundWindow()

    def set_active(self):
        """ Sets the window to active if it isn't already """
        if not self.is_active():
            """ Press alt before and after to prevent a nasty bug """
            pyautogui.press('alt')
            win32gui.SetForegroundWindow(self._handle)
            pyautogui.press('alt')
        return self

    def get_window_rect(self):
        """Get the bounding rectangle of the window """
        rect = win32gui.GetWindowRect(self._handle)
        return [rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1]]

    def match_image(self, largeImg, smallImg, threshold=0.1, debug=False):
        """ Finds smallImg in largeImg using template matching """
        """ Adjust threshold for the precision of the match (between 0 and 1, the lowest being more precise """
        """ Returns false if no match was found with the given threshold """
        method = cv2.TM_SQDIFF_NORMED

        # Read the images from the file
        # print(type(smallImg))
        # print(type(largeImg))
        if(type(smallImg) is str):
            small_image = cv2.imread(smallImg)
        else:
            small_image = cv2.cvtColor(numpy.array(smallImg), cv2.COLOR_RGB2BGR)
        if(type(largeImg) is str):
            large_image = cv2.imread(largeImg)
        else:
            large_image = cv2.cvtColor(numpy.array(largeImg), cv2.COLOR_RGB2BGR)
        
        w, h = small_image.shape[:-1]

        result = cv2.matchTemplate(small_image, large_image, method)

        # We want the minimum squared difference
        mn, _, mnLoc, _ = cv2.minMaxLoc(result)

        if (mn >= threshold):
            return False

        # Extract the coordinates of our best match
        x, y = mnLoc

        if debug:
            # Draw the rectangle:
            # Get the size of the template. This is the same size as the match.
            trows, tcols = small_image.shape[:2]

            # Draw the rectangle on large_image
            cv2.rectangle(large_image, (x, y),
                          (x+tcols, y+trows), (0, 0, 255), 2)

            # Display the original image with the rectangle around the match.
            cv2.imshow('output', large_image)

            # The image is only displayed if we call this
            cv2.waitKey(0)

        # Return coordinates to center of match
        return (x + (w * 0.5), y + (h * 0.5))

    def pixel_matches_color(self, coords, rgb, threshold=0):
        """ Matches the color of a pixel relative to the window's position """
        wx, wy = self.get_window_rect()[:2]
        x, y = coords
        # self.move_mouse(x, y)
        return pyautogui.pixelMatchesColor(x + wx, y + wy, rgb, tolerance=threshold)

    def move_mouse(self, x, y, speed=.5):
        """ Moves to mouse to the position (x, y) relative to the window's position """
        wx, wy = self.get_window_rect()[:2]
        pyautogui.moveTo(wx + x, wy + y, speed)
        return self

    def click(self, x, y, delay=.1, speed=.5, button='left'):
        """ Moves the mouse to (x, y) relative to the window and presses the mouse button """
        (self.set_active()
         .move_mouse(x, y, speed=speed)
         .wait(delay))

        pyautogui.click(button=button)
        return self

    def screenshot(self, name, region=False):
        """ 
        - Captures a screenshot of the window and saves it to 'name' 
        - Can also be used the capture specific parts of the window by passing in the region arg. (x, y, width, height) (Relative to the window position) 

        """
        self.set_active()
        # region should be a tuple
        # Example: (x, y, width, height)
        window = self.get_window_rect()
        if not region:
            # Set the default region to the area of the window
            region = window
        else:
            # Adjust the region so that it is relative to the window
            wx, wy = window[:2]
            region = list(region)
            region[0] += wx
            region[1] += wy

        pyautogui.screenshot(name, region=region)
    
    def screenshotRAM(self, region=False):
        """ 
        - Captures a screenshot of the window and saves it to 'name' 
        - Can also be used the capture specific parts of the window by passing in the region arg. (x, y, width, height) (Relative to the window position) 

        """
        self.set_active()
        # region should be a tuple
        # Example: (x, y, width, height)
        window = self.get_window_rect()
        if not region:
            # Set the default region to the area of the window
            region = window
        else:
            # Adjust the region so that it is relative to the window
            wx, wy = window[:2]
            region = list(region)
            region[0] += wx
            region[1] += wy

        return pyautogui.screenshot(region=region)

    def teleport_to_friend(self, match_img):
        """
        Completes a set of actions to teleport to a friend.
        The friend must have the proper symbol next to it
        symbol must match the image passed as 'match_img'

        """
        self.set_active()
        # Check if friends already opened (and close it)
        while self.pixel_matches_color((780, 364), (230, 0, 0), 40):
            self.click(780, 364).wait(0.2)

        # Open friend menu
        self.click(780, 50)

        # Find friend that matches friend match_img
        friend_area = self.screenshotRAM(region=self._friends_area)

        found = self.match_image(
            friend_area, 'icons/friends/' + match_img)

        if found is not False:
            x, y = found
            offset_x, offset_y = self._friends_area[:2]
            (self.click(offset_x + x + 50, offset_y + y)  # Select friend
             .click(450, 115)  # Select port
             .click(415, 395)  # Select yes
             )
            return self
        else:
            print('Friend cound not be found')
            return False

    def enter_dungeon_dialog(self):
        """ Detects if the 'Enter Dungeon' dialog is present """
        self.set_active()
        return (self.pixel_matches_color((253, 550), (4, 195, 4), 5) and
                self.pixel_matches_color((284, 550), (20, 218, 11), 5))

    def is_logo_bottom_left_loading(self):
        self.set_active()
        return self.pixel_matches_color((108, 551), (252, 127, 5), 30)

    def is_logo_bottom_right_loading(self):
        self.set_active()
        return self.pixel_matches_color((623, 490+36), (255, 130, 16), 30)

    def is_logo_bottom_left_or_right_loading(self):
        self.set_active()
        return self.pixel_matches_color((170, 532), (252, 127, 5), 30) or self.pixel_matches_color((108, 551), (252, 127, 5), 30)

    def logout(self,isDungeon=False):
        self.set_active()
        self.press_key('esc')
        #move mouse to quit button & click
        self.click(265,482+36,delay=.2)
        #if in dungeon, acknowledge the prompt
        if(isDungeon==True):
            self.click(411,386+36,delay=.2)
        #wait until loading is done
        play_btn = self.screenshotRAM(region=self._login_area)

        found = self.match_image(play_btn, 'buttons/play.png' , threshold=.2)

        while (found == False):
            self.wait(1)
            play_btn = self.screenshotRAM(region=self._login_area)
            found = self.match_image(play_btn, 'buttons/play.png' , threshold=.2)
            
        #press play button
        self.click(405,573+36,delay=.2)

    def accurate_delay(self, delay):
        ''' Function to provide accurate time delay in millisecond
        '''
        _ = time.perf_counter() + delay
        while time.perf_counter() < _:
            pass

    def hold_key(self, key, holdtime=0.0):
        """ 
        Holds a key for a specific amount of time, usefull for moving with the W A S D keys 
        """
        self.set_active()
        start = time.time()
        pyautogui.keyDown(key)
        """
        while time.time() - start < holdtime:
            pass
        """
        time.sleep(holdtime)
        pyautogui.keyUp(key)

        return self
        # if(waittime > 0):
        #     self.accurate_delay(waittime)
        # pyautogui.keyDown(key)
        # self.accurate_delay(holdtime)
        # pyautogui.keyUp(key)

    def navigate_keys(self, keys, holdtimes, waittimes):
        #keys []
        #holdtimes []
        #waittimes []
        #assume they are in order
        curr_time = 0.0
            
        for i in range(len(keys)):
            #wait until key needs to be pressed
            delay_time = waittimes[i]-curr_time

            """start = time.time()
            while time.time() - start < delay_time:
                pass
            """
            time.sleep(delay_time)

            #hold key down for specified time
            pyautogui.keyDown(keys[i])
            start = time.time()
            """
            while time.time() - start < holdtimes[i]:
                pass
            """
            time.sleep(holdtimes[i]-.15)
            pyautogui.keyUp(keys[i])

            curr_time = waittimes[i]+holdtimes[i]
            

        return self
    def press_key(self, key):
        """
        Presses a key, useful for pressing 'x' to enter a dungeon
        """
        self.set_active()
        pyautogui.press(key)
        return self

    def is_health_low(self, health_percent):
        self.set_active()
        time.sleep(.3)
        # Matches a pixel in the lower third of the health globe
        if(health_percent==33):
            POSITION = (23, 563)
            COLOR = (126, 41, 3)
        elif(health_percent==80):
            POSITION = (26,531)
            COLOR = (242, 52, 81)
            
        
        THRESHOLD = 15
        #Prints out color of pixel that triggers health low
        #used to see how much you need to change threshold
        # if not self.pixel_matches_color(POSITION, COLOR, threshold=THRESHOLD):
        #     wx, wy = self.get_window_rect()[:2]
        #     print(pyautogui.pixel(26+wx,531+wy))
        return not self.pixel_matches_color(POSITION, COLOR, threshold=THRESHOLD)

    def is_mana_low(self):
        self.set_active()
        # Matches a pixel in the lower third of the mana globe
        POSITION = (79, 591)
        COLOR = (66, 13, 83)
        THRESHOLD = 10
        return not self.pixel_matches_color(POSITION, COLOR, threshold=THRESHOLD)

    def use_potion_if_needed(self, refill=False, teleport_to_wizard="", health_percent=33): #Health Position defaults to 1/3
        self.set_active()
        mana_low = self.is_mana_low()
        health_low = self.is_health_low(health_percent)

        if mana_low:
            print('Mana is low, using potion')
        if health_low:
            print('Health is low, using potion')
        if mana_low or health_low:
            print('Clicking Potion')
            self.click(160, 590, delay=.2) 
            self.wait(1)
            if(self.is_mana_low() or self.is_health_low(health_percent) and refill): #IF Refill == true, all wiz must have HILDA marked in commons
                print('Refilling')
                self.recall_location()
                #Waits for user to finish loading
                while not self.is_logo_bottom_left_or_right_loading():
                    time.sleep(.2)

                while not self.is_idle():
                    time.sleep(.5)

                #Waits for hilda confirmation to pop
                time.sleep(1)
                #Begin Potion Buy
                if(self.is_mana_low): # Buys potion before marking location
                    # Opens Dialog
                    self.press_key('x')
                    self.wait(.5)

                    #Potion Clicks
                    self.click(555, 300)
                    self.click(261, 491)
                    self.click(515, 470)
                    self.click(410, 390)
                    self.click(555, 300)
                    self.click(261, 491)
                    self.click(685, 540)
                    self.wait(.5)
                    
                    # Get back to Dungeon
                    self.mark_location()
                    self.wait(.5)
                    self.teleport_to_friend(teleport_to_wizard)

                    #Waits for user to finish loading
                    while not self.is_logo_bottom_left_or_right_loading():
                        time.sleep(.2)

                    while not self.is_idle():
                        time.sleep(.5)
                else: # Marks location to waste mana before buying potions
                    self.mark_location()
                    self.wait(.5)
                    self.press_key('x')
                    self.wait(.5)

                    #Potion Clicks
                    self.click(555, 300)
                    self.click(261, 491)
                    self.click(515, 470)
                    self.click(410, 390)
                    self.click(555, 300)
                    self.click(261, 491)
                    self.click(685, 540)
                    self.wait(.5)

                    #Gets back to dungeon
                    self.teleport_to_friend(teleport_to_wizard)

                    #Waits for user to finish loading
                    while not self.is_logo_bottom_left_loading():
                        time.sleep(.2)

                    while not self.is_idle():
                        time.sleep(.5)


    def pass_turn(self):
        self.click(254, 398, delay=.5).move_mouse(200, 400)
        return self

    def is_turn_to_play(self):
        """ matches a yellow pixel in the 'pass' button """
        return self.pixel_matches_color((238, 398), (255, 255, 0), 20)
    
    def is_turn_to_play_pass(self):
        pic = self.screenshotRAM(region=(190, 385, 440, 40))

        found = self.match_image(pic, 'buttons/pass.png', threshold=.1)

        if found is not False:
            return True
        else:
            return False

    def wait_for_next_turn(self):
        """ Wait for spell round to begin """
        while self.is_turn_to_play():
            self.wait(1)

        print('Spell round begins')

        """ Start detecting if it's our turn to play again """
        while not self.is_turn_to_play():
            self.wait(1)

        print('Our turn to play')
        return self

    def wait_for_turn_to_play(self):
        while not self.is_turn_to_play():
            self.wait(.5)

    def wait_for_end_of_round_dialog(self):
        """ Similar to wait_for_next_turn, but also detects if its the end of the battle """
        """ Wait for spell round to begin """
        while self.is_turn_to_play():
            self.wait(1)

        """ Start detecting if it's our turn to play again """
        """ Or if it's the end of the battle """
        while not (self.is_turn_to_play_pass() or self.is_idle() or self.find_button('done')):
            self.wait(1)
        return self

    def wait_for_end_of_round(self):
        """ Similar to wait_for_next_turn, but also detects if its the end of the battle """
        """ Wait for spell round to begin """
        while self.is_turn_to_play_pass():
            self.wait(1)

        """ Start detecting if it's our turn to play again """
        """ Or if it's the end of the battle """
        while not (self.is_turn_to_play_pass() or self.is_idle()):
            self.wait(1)
        return self

    def is_idle(self):
        """ Matches a pink pixel in the pet icon (only visible when not in battle) """
        return self.pixel_matches_color((140, 554), (252, 146, 206), 2)

    def find_spell(self, spell_type, spell_name, threshold=0.10, max_tries=2, recapture=True):
        """ 
        Attempts the find the spell passed is 'spell_name'
        returns False if not found with the given threshold
        Use recapture=False to not re-take the screenshot of the spell_area
        Adds spell position to memory for later use
        """
        self.set_active()
        tries = 0
        res = False

        spell_area = self.screenshotRAM(region=self._spell_area)

        while not res and tries < max_tries:
            tries += 1

            if tries > 1:
                # Wait 1 second before re-trying
                self.wait(1)
                recapture = True


            if recapture:
                self.mouse_out_of_area(self._spell_area)
                spell_area = self.screenshotRAM(region=self._spell_area)

            res = self.match_image(
                spell_area, ('spells/' + spell_type +  '/' + spell_name + '.png'), threshold)

        if res is not False:
            x, y = res
            offset_x, offset_y = self._spell_area[:2]
            spell_pos = (offset_x + x, offset_y + y)
            # Remember location
            self._spell_memory[spell_name] = spell_pos
            return spell_pos
        else:
            return False

    def find_unusable_spells(self, limit=-1):
        """ Returns an array of the positions of unusable spells (grayed out) """
        """ Useful for farming Loremaster, it prevents getting a crowded deck if you learn a new spell """
        self.set_active()
        self.mouse_out_of_area(self._spell_area)
        spell_area = self.screenshotRAM(region=self._spell_area)
        w, h = (28, 38)  # The size of the gray area we're looking for
        #img = cv2.imread('spell_area.png')
        img = cv2.cvtColor(numpy.array(spell_area), cv2.COLOR_RGB2BGR)
        rows, cols = img.shape[:2]
        pts = []

        # Determine if a pixel is gray enough
        def isGray(pixel, threshold):
            return abs(int(min(*pixel)) - int(max(*pixel))) <= threshold

        i = 2
        j = 0
        while j < (cols - w):
            """ find a rectangle with no color """
            grayScale = True
            for y in range(h):
                for x in range(w):
                    pixel = img[i + y, j + x]
                    if not isGray(pixel, threshold=30):
                        grayScale = False

                    if not grayScale:
                        break

                if not grayScale:
                    break

            if grayScale:
                offset_x, offset_y = self._spell_area[:2]
                spell_pos = (offset_x + j + w/2, offset_y + i+h/2)
                pts.append(spell_pos)
                j += w
                # Break if we've reached the limit in requested areas
                if limit > 0 and len(pts) >= limit:
                    break

            j += 1

        self._spell_memory["unusable"] = pts
        return pts

    def discard_unusable_spells(self, limit=-1):
        count = 0
        while True:
            count += 1
            print(count)
            try:
                # Try accessing from memory
                card_pos = self._spell_memory["unusable"][0]
            except (KeyError, IndexError):
                result = self.find_unusable_spells(limit=1)
                if len(result) is not 0:
                    card_pos = result[0]
                else:
                    break
            print(card_pos)
            # Right click the card position
            self.click(*card_pos, button='right', delay=.2)
            # Flush card memory
            self.flush_spell_memory()

    def flush_spell_memory(self):
        """ 
        This action gets called everytime there is a destructive action to the spells (The spells change position)
        For example: Casting, Enchanting, Discarding
        """
        self._spell_memory = {}
        return

    def select_spell(self, spell_type, spell):
        """ 
        Clicks on a spell
        Attemps to look in memory to see if we already have found this spell
        Returns false if the spell can't be found
        """
        try:
            spell_pos = self._spell_memory[spell]
        except KeyError:
            spell_pos = self.find_spell(spell_type, spell)

        if spell_pos is not False:
            self.click(*spell_pos, delay=.3)
            return self
        else:
            return False

    def cast_spell(self, spell_type, spell,threshold=.15):
        """ 
        Clicks on the spell and clears memory cache
        if the spell requires a target, chain it with .at_target([enemy_pos])
        """
        if self.find_spell(spell_type, spell,threshold):
            print('Casting', spell)
            self.flush_spell_memory()
            return self.select_spell(spell_type, spell)
        else:
            return False

    def enchant(self, spell_type, spell_name, enchant_type, enchant_name, threshold=0.15, silent_fail=False):
        """ Attemps the enchant 'spell_name' with 'enchant_name' """
        if self.find_spell(spell_type, spell_name, threshold=threshold) and self.find_spell(enchant_type, enchant_name, recapture=False, threshold=threshold):
            print('Enchanting', spell_name, 'with', enchant_name)
            self.select_spell(enchant_type, enchant_name)
            self.select_spell(spell_type, spell_name)
            self.flush_spell_memory()
            return self
        else:
            if not silent_fail:
                print("One or more spells couldn't be found:",
                      spell_name, enchant_name)
            return False

    def get_enemy_pos(self, enemy_img):
        """ 
        Attemps to find the position of an enemy the matches the image provided 
        returns 1, 2, 3, or 4 if found
        otherwise returns False

        (In my example, the image to match is the balance symbol, as only the Loremaster has it in this fight. It could also be a screenshot of the name of the enemy in question)
        """

        enemy_area = self.screenshotRAM(region=self._enemy_area)

        found = self.match_image(enemy_area, 'icons/enemy/' + enemy_img, threshold=.2)

        if found is not False:
            found_x, _ = found
            enemy_pos = round((found_x - 60) / 170) + 1
            return enemy_pos
        else:
            return False
    def get_friendly_pos(self, friendly_img):
        """ 
        Checks if player is in position - posisble use case includes checking if there are 3 or two wizards in battle
        """

        friendly_area = self.screenshotRAM(region=self._friendly_area)

        found = self.match_image(friendly_area, 'icons/teammate/' + friendly_img, threshold=.2)

        if found is not False:
            found_x, _ = found
            friend_pos = round((found_x - 60) / 170) + 1
            return friend_pos
        else:
            return False
    def at_target(self, target_pos):
        """ Clicks the target, based on position 1, 2, 3, or 4 """
        x = (174 * (target_pos - 1)) + 130
        y = 50
        self.click(x, y, delay=.2)
        return self

    def at_friendly(self, target_pos):
        """ Clicks the target, based on position 1, 2, 3, or 4 """
        x = (174 * (target_pos - 1)) + 150
        y = 600
        self.click(x, y, delay=.2)
        return self

    def mouse_out_of_area(self, area):
        """ Move the mouse outside of an area, to make sure the mouse doesn't interfere with image matching """
        # Adjust the region so that it is relative to the window
        wx, wy = self.get_window_rect()[:2]
        region = list(area)
        region[0] += wx
        region[1] += wy

        def in_area(area):
            px, py = pyautogui.position()
            x, y, w, h = area
            return (px > x and px < (x + w) and py > y and py < (y + h))

        while in_area(region):
            pyautogui.moveRel(0, -100, duration=0.5)

        return self

    def face_arrow(self):
        """ Faces the questing arrow, useful for finding your way out of a dungeon """
        self.set_active()
        pyautogui.keyDown('a')
        count = 0
        while not self.pixel_matches_color((385, 531), (133, 120, 14), 2):
            count += 1
            pass
        pyautogui.keyUp('a')
        self.hold_key('d', min(count / 100, 0.2))
        return self

    def count_enemies(self):
        Y = 75
        COLOR = (207, 186, 135)
        num_enemies = 0
        for i in range(4):
            X = (174 * (i)) + 203
            if self.pixel_matches_color((X, Y), COLOR, threshold=30):
                num_enemies += 1

        if num_enemies == 1:
            print(num_enemies, 'enemy in battle')
        else:
            print(num_enemies, 'enemies in battle')
        return num_enemies

    def quick_sell(self, sell_crown_items, sell_jewels):
        """ 
        Quick sells everything unlocked
        """

        """ Opens user's bag """
        self.press_key('b')
        """ Clicks on the quick sell icon in the bag """
        self.click(158, 535, delay=1)
        """ Clicks the "All" tab on the top of the quick sell interface """
        self.click(183, 178, delay=.3)
        """ Clicks the "All" Button within the all tab """
        self.click(417, 223, delay=.3)
        """ Clicks yes or no for selling crowns """
        if(sell_crown_items is True):
            self.click(406, 399, delay=.3)
        else:    
            self.click(513, 399, delay=.3)

        """ Clicks next twice to get to jewels page """
        if(sell_jewels is False):
            self.click(675, 173, delay=.3)
            self.click(675, 173, delay=.3)
            self.click(417, 223, delay=.3)
                
        """ Clicks sell X for X """
        self.click(263, 495, delay=.3)

        """ Clicks sell on sell screen """
        self.click(400, 488, delay=.3)

        """ Remove warning about gold overflow"""
        self.click(410,432, delay=.6)

        """ Closes user's bag """
        self.press_key('b')
    
        (self.set_active()
            .move_mouse(669, 189, speed=0.5))

    def set_active_quest(self,quest_index=1):
        #Opens users quest log
        self.press_key('q')
        #clicks on quest at given index
        if(quest_index==1):
            self.click(267,202,delay=.2)
        elif(quest_index==2):
            self.click(517,202,delay=.2)
        elif(quest_index==3):
            self.click(267,430,delay=.2)
        elif(quest_index==4):
            self.click(267,430,delay=.2)
        else:
            print("Give a valid quest position")
        #close quest menu
        self.press_key('q')
        #get mouse out of the way of other things
        (self.set_active()
            .move_mouse(669, 189, speed=0.5))

    def mark_location(self):
        self.press_key('pagedown')

    def recall_location(self):
        self.press_key('pageup')

    def clear_dialog(self, total_dialog):
        for x in range(total_dialog):
            self.press_key('space').wait(.2)

    def find_button(self, button_img):
        """ 
        Checks if player is in position - posisble use case includes checking if there are 3 or two wizards in battle
        """

        screenshot = self.screenshotRAM(region=(136, 536, 650, 87))

        found = self.match_image(screenshot, 'buttons/' + button_img + '.png', threshold=.1)

        if found is not False:
            return True
        else:
            return False

    #Loremaster Random attack sequence
    def lm_attack(self, wizard_type, boss_pos):
        wizard_type = wizard_type.split('.')[0]

        print(wizard_type)

        if(wizard_type == "feinter"):
            """ Feinter plays """
            # Check to see if deck is crowded with unusable spells
            cn = len(self.find_unusable_spells())
            if cn > 2:
                self.discard_unusable_spells(cn)

            # Play
            if self.enchant('Death', 'feint', 'Sun', 'potent'):
                self.cast_spell('Death', 'feint-potent').at_target(boss_pos)

            elif self.find_spell('Death', 'feint'):
                self.cast_spell('Death', 'feint').at_target(boss_pos)

            else:
                self.pass_turn()
        
        if(wizard_type == "hitter"):
            """ Hitter plays """
            # Check to see if deck is crowded with unusable spells
            cn = len(self.find_unusable_spells())
            # Discard the spells
            if cn > 2:
                self.discard_unusable_spells(cn)

            # Play
            if (self.find_spell('Storm', 'glowbug-squall', threshold=0.05, max_tries=3) and
                    self.enchant('Storm', 'glowbug-squall', 'Sun', 'epic')):
                self.find_spell('Storm', 'glowbug-squall-enchanted', max_tries=4)
                self.cast_spell('Storm', 'glowbug-squall-enchanted')

            elif self.find_spell('Storm', 'tempest-enchanted', max_tries=1):
                self.cast_spell('Storm', 'tempest-enchanted')

            elif self.enchant('Storm', 'tempest', 'Sun', 'epic'):
                self.find_spell('Storm', 'tempest-enchanted', max_tries=4)
                self.cast_spell('Storm', 'tempest-enchanted')

            elif self.find_spell('Storm', 'glowbug-squall-enchanted', threshold=.05):
                self.cast_spell('Storm', 'glowbug-squall-enchanted')

            elif self.find_spell('Storm', 'glowbug-squall', threshold=.05):
                self.cast_spell('Storm', 'glowbug-squall')

            else:
                self.pass_turn()
        
        if(wizard_type == "blader"):
            """ Blader plays """
            # Check to see if deck is crowded with unusable spells
            cn = len(self.find_unusable_spells())
            if cn > 2:
                self.discard_unusable_spells(cn)

            # Play
            if self.enchant('Death', 'feint', 'Sun', 'potent'):
                self.cast_spell('Death', 'feint-potent').at_target(boss_pos)

            elif self.find_spell('Death', 'feint'):
                self.cast_spell('Death', 'feint').at_target(boss_pos)

            else:
                self.pass_turn()

    #One round strat for most mobs
    def mass_feint_attack(self, wizard_type, boss_pos):
        wizard_type = wizard_type.split('.')[0]

        print(wizard_type)

        if(wizard_type == "feinter"):
            """ Feinter plays """
            # Check to see if deck is crowded with unusable spells
            cn = len(self.find_unusable_spells())
            if cn > 2:
                self.discard_unusable_spells(cn)

            # Play
            if self.enchant('Death', 'feint', 'Sun', 'potent'):
                self.cast_spell('Death', 'feint-potent').at_target(boss_pos)

            elif self.find_spell('Death', 'feint'):
                self.cast_spell('Death', 'feint').at_target(boss_pos)

            else:
                self.pass_turn()
        
        if(wizard_type == "hitter"):
            """ Hitter plays """
            # Check to see if deck is crowded with unusable spells
            cn = len(self.find_unusable_spells())
            # Discard the spells
            if cn > 2:
                self.discard_unusable_spells(cn)

            # Play
            if self.find_spell('Storm', 'tempest-enchanted', max_tries=2):
                self.cast_spell('Storm', 'tempest-enchanted')

            elif self.enchant('Storm', 'tempest', 'Sun', 'epic'):
                self.find_spell('Storm', 'tempest-enchanted', max_tries=2)
                self.cast_spell('Storm', 'tempest-enchanted')

            else:
                self.pass_turn()
        
        if(wizard_type == "blader"):
            """ Blader plays """
            # Check to see if deck is crowded with unusable spells
            cn = len(self.find_unusable_spells())
            if cn > 2:
                self.discard_unusable_spells(cn)

            # Play
            if self.find_spell('Death', 'mass_feint'):
                self.cast_spell('Death', 'mass_feint')
            elif self.find_spell('Life', 'pigsie'):
                self.cast_spell('Life', 'pigsie')
            elif self.find_spell('Life', 'unicorn'):
                self.cast_spell('Life', 'unicorn')
            else:
                self.pass_turn()
        
    #One round strat for most mobs
    def mass_feint_attack_lore(self, wizard_type, boss_pos):
        wizard_type = wizard_type.split('.')[0]

        print(wizard_type)

        if(wizard_type == "feinter"):
            """ Feinter plays """
            # Check to see if deck is crowded with unusable spells
            cn = len(self.find_unusable_spells())
            if cn > 2:
                self.discard_unusable_spells(cn)

            # Play
            if self.enchant('Death', 'feint', 'Sun', 'potent'):
                self.cast_spell('Death', 'feint-potent').at_target(boss_pos)

            elif self.find_spell('Death', 'feint'):
                self.cast_spell('Death', 'feint').at_target(boss_pos)

            else:
                self.pass_turn()
        
        if(wizard_type == "hitter"):
            """ Hitter plays """
            # Check to see if deck is crowded with unusable spells
            cn = len(self.find_unusable_spells())
            # Discard the spells
            if cn > 2:
                self.discard_unusable_spells(cn)

            # Play
            if self.find_spell('Storm', 'tempest-enchanted', max_tries=2):
                self.cast_spell('Storm', 'tempest-enchanted')

            elif self.enchant('Storm', 'tempest', 'Sun', 'epic'):
                self.find_spell('Storm', 'tempest-enchanted', max_tries=2)
                self.cast_spell('Storm', 'tempest-enchanted')

            else:
                self.pass_turn()
        
        if(wizard_type == "blader"):
            """ Blader plays """
            # Check to see if deck is crowded with unusable spells
            cn = len(self.find_unusable_spells())
            if cn > 2:
                self.discard_unusable_spells(cn)

            # Play
            if self.find_spell('Death', 'mass_feint'):
                self.cast_spell('Death', 'mass_feint')
            elif self.enchant('Death', 'feint', 'Sun', 'potent'):
                self.cast_spell('Death', 'feint-potent').at_target(boss_pos)
            elif self.find_spell('Death', 'feint'):
                self.cast_spell('Death', 'feint').at_target(boss_pos)
            else:
                self.pass_turn()

        #Catacombs Detritus Extract attack sequence
    def catacombs_detritus_attack(self, wizard_type, boss_pos, boss_battle=False):
        wizard_type = wizard_type.split('.')[0]

        print(wizard_type)

        if(wizard_type == "feinter"):
            """ Feinter plays """
            # Check to see if deck is crowded with unusable spells
            cn = len(self.find_unusable_spells())
            if cn > 2:
                self.discard_unusable_spells(cn)

            if(boss_battle):
                # Play
                
                #feint the boss on first round
                if self.enchant('Death', 'feint', 'Sun', 'potent'):
                    self.cast_spell('Death', 'feint-potent').at_target(boss_pos)
                                
                #cast blue elemental blade
                elif self.find_spell('Balance', 'b_elemental_blade', threshold=0.10):
                    self.cast_spell('Balance', 'b_elemental_blade',threshold=.10).at_friendly(2) #Casts at third wizard
                
                #cast sharpened elemental blade
                elif self.enchant('Balance', 'elemental_blade', 'Sun', 'sharpen',threshold=.10):
                    self.cast_spell('Balance', 'enchanted_elemental_blade',threshold=.10).at_friendly(2) #Casts at third wizard

                else:
                    self.pass_turn()
            else:
                # Play

                #cast sharpened elemental blade
                if self.enchant('Balance', 'elemental_blade', 'Sun', 'sharpen',threshold=.10):
                    self.cast_spell('Balance', 'enchanted_elemental_blade',threshold=.10).at_friendly(2) #Casts at third wizard

                #cast blue elemental blade
                elif self.find_spell('Balance', 'b_elemental_blade', threshold=0.10):
                    self.cast_spell('Balance', 'b_elemental_blade',threshold=.10).at_friendly(2) #Casts at third wizard

                else:
                    self.pass_turn()
        
        if(wizard_type == "hitter"):
            """ Hitter plays """
            # Check to see if deck is crowded with unusable spells
            cn = len(self.find_unusable_spells())
            # Discard the spells
            if cn > 2:
                self.discard_unusable_spells(cn)
            if(boss_battle):
                # Play
                if self.find_spell('Death', 'feint', threshold=0.10):
                    self.cast_spell('Death', 'feint').at_target(boss_pos)
                
                elif self.enchant('Storm', 'storm_blade', 'Sun', 'aegis'):
                    self.cast_spell('Storm', 'enchanted_storm_blade').at_friendly(2) #Casts at third wizard
                
                elif self.find_spell('Storm', 'tempest-enchanted', threshold=0.10):
                    self.cast_spell('Storm', 'tempest-enchanted')
                
                elif self.enchant('Storm', 'tempest', 'Sun', 'epic'):
                    self.find_spell('Storm', 'tempest-enchanted', threshold=0.10)
                    self.cast_spell('Storm', 'tempest-enchanted')
                else:
                    self.pass_turn()
            else:
                if self.find_spell('Storm', 'tempest-enchanted', threshold=0.10):
                    self.cast_spell('Storm', 'tempest-enchanted')

                elif self.enchant('Storm', 'tempest', 'Sun', 'epic'):
                    self.find_spell('Storm', 'tempest-enchanted', threshold=0.10)
                    self.cast_spell('Storm', 'tempest-enchanted')

                else:
                    self.pass_turn()
        if(wizard_type == "blader"):
            """ Blader plays """
            # Check to see if deck is crowded with unusable spells
            cn = len(self.find_unusable_spells())
            if cn > 2:
                self.discard_unusable_spells(cn)

            # Play
            if(boss_battle):
                #mass fient boss first round
                if self.find_spell('Death', 'mass_feint', threshold=0.10):
                    self.cast_spell('Death', 'mass_feint')
                #aegis blade
                elif self.enchant('Balance', 'elemental_blade', 'Sun', 'aegis'):
                    self.cast_spell('Balance', 'enchanted_elemental_blade').at_friendly(2) #Casts at third wizard
                #blue storm blade
                elif self.find_spell('Storm', 'b_storm_blade', threshold=0.10):
                    self.cast_spell('Storm', 'b_storm_blade',threshold=.10).at_friendly(2) #Casts at third wizard
                elif self.find_spell('Balance', 'enchanted_elemental_blade', threshold=0.10): #Checks if left over enchanted blade is not cast
                    self.cast_spell('Balance', 'enchanted_elemental_blade')
                elif self.find_spell('Life', 'pigsie', threshold=0.10):
                    self.cast_spell('Life', 'pigsie')
                elif self.find_spell('Life', 'unicorn', threshold=0.10):
                    self.cast_spell('Life', 'unicorn')
                else:
                    self.pass_turn()
            else:
                if self.find_spell('Death', 'mass_feint', threshold=0.10):
                    self.cast_spell('Death', 'mass_feint')
                elif self.find_spell('Life', 'pigsie', threshold=0.10):
                    self.cast_spell('Life', 'pigsie')
                elif self.find_spell('Life', 'unicorn', threshold=0.10):
                    self.cast_spell('Life', 'unicorn')
                else:
                    self.pass_turn()      


