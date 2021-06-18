from numpy.core.numeric import True_
import win32gui
import pyautogui
import cv2
import time
import numpy
import ctypes
import math

# import only system from os 
from os import system, name 


class api:
    def __init__(self, handle=None):
        self._handle = handle
        self._spell_memory = {}
        self._friends_area = (625, 65, 20, 240)
        self._spell_area = (245, 290, 370, 70)
        self._enemy_area = (68, 26, 650, 35)
        self._friendly_area = (136, 536, 650, 70)
        self._login_area = (307,553+36,187,44)

        self.true_wizards = []
        self.wizards = []
        self.hitting_school = "storm"
        self.round_count    = 0
        self.failed_runs    = 0
        self.start_time     = 0
        self.round_start    = 0
        self.quick_sell_def = [True, 10]
        self.total_wizards  = 1

    region_offset = (5,5,0,0)

    class Wizard(object):
        """Object for Defining Wizards"""
        def __init__(self, icon, name, wind):
            self.icon = icon
            self.name = name
            self.win  = wind
        
    def wait(self, s):
        """ Alias for time.sleep() that return self for function chaining """
        time.sleep(s)
        return self
    
    # define our clear function 
    def clear_console(self): 
        # for windows 
        if name == 'nt': 
            _ = system('cls') 
        # for mac and linux(here, os.name is 'posix') 
        else: 
            _ = system('clear') 


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

    def register_windows(self, count = 1):
        if(count < 1):
            print("You must have a value of 1 or greater passed to register_windows")
            exit()

        self.total_wizards = count

        """ Register windows """
        try:
            if(count == 1):
                hitter = api().register_window(nth=0) # Furthest Left
            if(count >= 2): 
                feinter = api().register_window(nth=0) # Furthest Right 
                hitter = api().register_window(nth=1) # Furthest Left
            if(count >= 3): 
                blader = api().register_window(nth=2) # Middle
        except IndexError:
            print('You need ', count ,' wizard101 accounts to run this particular bot.')
            exit()
        
        """ compare x positions of windows to make sure 'hitter' is the farthest left, and 'feinter' is the farthest right, and 'blader' is middle """
        if(count >= 2):
            if (hitter.get_window_rect()[0] > feinter.get_window_rect()[0]):
                # Switch them, if not
                hitter, feinter = feinter, hitter
        if(count >= 3):
            if(hitter.get_window_rect()[0] > blader.get_window_rect()[0]):
                hitter, blader = blader, hitter

            if(blader.get_window_rect()[0] > feinter.get_window_rect()[0]):
                blader, feinter = feinter, blader

        "Create Array of Wizards"
        if(count == 1):
            self.wizards.append(self.Wizard("hitter.png", "hitter", hitter))
            self.true_wizards.append(self.Wizard("hitter.png", "hitter", hitter))
            
        if(count >= 2): 
            self.wizards.append(self.Wizard("feinter.png", "feinter", feinter))
            self.true_wizards.append(self.Wizard("feinter.png", "feinter", feinter))
        if(count >= 3): 
            self.wizards.append(self.Wizard("blader.png", "blader", blader))
            self.true_wizards.append(self.Wizard("blader.png", "blader", blader))
            
        """Hitter will ALWAYS enter fight last"""
        if(count >= 2):
            self.wizards.append(self.Wizard("hitter.png", "hitter", hitter))
            self.true_wizards.append(self.Wizard("hitter.png", "hitter", hitter))
    

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
        x+=self.region_offset[0]
        y+=self.region_offset[1]
        #print(pyautogui.pixel(x+wx,y+wy))
        #print(rgb)
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
            region[0] += self.region_offset[0]
            region[1] += wy
            region[1] += self.region_offset[1]

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
            region[0] += self.region_offset[0]
            region[1] += wy
            region[1] += self.region_offset[1]

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
            self.wait_pet_loading()
            return self
        else:
            #print('Friend cound not be found')
            return False

    def enter_dungeon_dialog(self):
        """ Detects if the 'Enter Dungeon' dialog is present """
        self.set_active()
        return (self.pixel_matches_color((253, 550), (4, 195, 4), 5) and
                self.pixel_matches_color((284, 550), (20, 218, 11), 5))
                
    def is_pet_icon_visible(self):
        self.set_active()
        x,y = (126,535)
        roi_image = self.screenshotRAM(region=(x,y,26,17))
        found = self.match_image(roi_image,'pet_icon.png') or self.find_button('done') or self.find_button('more')
        return found

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
            self.wait(.5)
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
        elif(health_percent==60):
            POSITION = (26,541)            
            COLOR = (220, 43, 60)
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
        COLOR = (66, 13, 82)
        THRESHOLD = 12
        return not self.pixel_matches_color(POSITION, COLOR, threshold=THRESHOLD)

    def clear_dialog(self):
        for w in self.wizards:
            w.win.move_mouse(350, 350)
            while(w.win.find_button('done') or w.win.find_button('more')):
                w.win.press_key('space').wait(.2)

    def await_finished_loading(self):
        for w in self.wizards:
            while w.win.is_pet_icon_visible():
                time.sleep(.2)
        
        for w in self.wizards:
            while ((not w.win.is_pet_icon_visible()) and (not w.win.find_button('more')) and (not w.win.find_button('done'))):
                time.sleep(.2)

    def print_separator(self, *arg):
        """
            Print human readable strings to terminal
        """
        sides = '+'*16
        _str = " ".join([sides, " ".join(arg), sides])
        l = len(_str)
        print('='*l)
        print(_str)
        print('='*l)


    def print_time(self, timer):
        """
            Prints human readable time to terminal
        """
        minutes = math.floor(timer/60)
        seconds = math.floor(timer % 60)
        print('Round lasted {} minutes and {} seconds.'.format(minutes, seconds))

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

        # if num_enemies == 1:
        #     print(num_enemies, 'enemy in battle')
        # else:
        #     print(num_enemies, 'enemies in battle')
        return num_enemies

    def quick_sell(self):
        """ Quick sell every X rounds"""
        if(self.round_count % self.quick_sell_def[1] == 0 and self.quick_sell_def[0]):
            self.wizards[0].win.perform_quick_sell(False, False)
            if(self.total_wizards >= 2):
                self.wizards[1].win.perform_quick_sell(False, False)
            if(self.total_wizards >= 3):
                self.wizards[2].win.perform_quick_sell(False, False)

    def perform_quick_sell(self, sell_crown_items, sell_jewels):
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
        if(self.match_image(self.screenshotRAM((350, 415, 100, 20)), 'buttons/yes.png', threshold=.1)):
            self.click(410, 432, delay=.6)

        """ Remove warning about pet sell"""
        if(self.match_image(self.screenshotRAM((350, 385, 100, 20)), 'buttons/yes.png', threshold=.1)):
            self.click(400, 405, delay=.6)

        """ Remove warning about max gold"""
        #self.screenshot("gold_test.png",region=(355, 415, 100, 20))
        if(self.match_image(self.screenshotRAM((355, 415, 100, 20)), 'buttons/yes.png', threshold=.1)):
            self.click(400, 425, delay=.6)

        """ Closes user's bag """
        self.press_key('b')
    
        (self.set_active()
            .move_mouse(669, 189, speed=0.5))

    def use_potion_if_needed(self, refill=False, teleport_to_wizard="", health_percent=33, teleport=False, teleport_friend_img="",greedy_tp=False): #Health Position defaults to 1/3
        
        self.set_active()
        mana_low = self.is_mana_low()
        health_low = self.is_health_low(health_percent)
        # if mana_low:
        #     print('Mana is low, using potion')
        # if health_low:
        #     print('Health is low, using potion')
        if mana_low or health_low:
            #print('Clicking Potion')
            self.click(160, 590, delay=.2) 
            self.wait(1)
            if(self.is_mana_low() or self.is_health_low(health_percent) and refill): #IF Refill == true, all wiz must have HILDA marked in commons
                #print('Refilling')
                if(teleport):
                    self.teleport_to_friend(teleport_friend_img)
                else:
                    self.recall_location()
                    
                #Waits for user to finish loading
                if not greedy_tp:
                    self.wait_pet_loading()
                    self.wait(.1)
                else:
                    self.wait_pet_loading()
                    self.wait(.1)

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
                    if(teleport == False):
                        self.mark_location()
                    self.wait(.5)
                    self.teleport_to_friend(teleport_to_wizard)

                else: # Marks location to waste mana before buying potions
                    if(teleport == False):
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

    def mark_location(self):
        self.press_key('pagedown')

    def recall_location(self):
        self.press_key('pageup')
    
    def pass_turn(self):
        self.click(254, 398, delay=.5).move_mouse(200, 400)
        return self

    def wait_pet_loading(self):
        #wait for pet icon to disappear
        while self.is_pet_icon_visible():
                #print("pet icon is visible")
                time.sleep(.2)
        #wait for pept icon to reappear
        while ((not self.is_pet_icon_visible()) and (not self.find_button('more')) and (not self.find_button('done'))):
            time.sleep(.2)

    def is_pet_icon_visible(self):
        self.set_active()
        x,y = (126,535)
        roi_image = self.screenshotRAM(region=(x,y,26,17))
        found = self.match_image(roi_image,'pet_icon.png') or self.find_button('done') or self.find_button('more')
        return found

    def find_button(self, button_img):
        """ 
        Checks if more or done are on screen
        """

        screenshot = self.screenshotRAM(region=(136, 536, 650, 87))

        found = self.match_image(screenshot, 'buttons/' + button_img + '.png', threshold=.1)

        if found is not False:
            return True
        else:
            return False
    def is_turn_to_play(self):
        """ matches a yellow pixel in the 'pass' button """
        #return self.pixel_matches_color((238, 398), (255, 255, 0), 20)
        return self.is_turn_to_play_pass()
    
    def is_turn_to_play_pass(self):
        roi = (190, 385, 440, 40)
        #roi = (roi[0]+self.region_offset[0],roi[1]+self.region_offset[1],roi[2]+self.region_offset[2],roi[3]+self.region_offset[3])
        pic = self.screenshotRAM(region=roi)

        found = self.match_image(pic, 'buttons/pass.png', threshold=.1)

        if found is not False:
            return True
        else:
            return False

    def wait_for_next_turn(self):
        """ Wait for spell round to begin """
        while self.is_turn_to_play():
            self.wait(1)

        #print('Spell round begins')

        """ Start detecting if it's our turn to play again """
        while not self.is_turn_to_play():
            self.wait(1)

        #print('Our turn to play')
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
        while not (self.is_turn_to_play_pass() or self.is_idle() or self.find_button('done') or self.find_button('more')):
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
        #return self.pixel_matches_color((140, 554), (252, 146, 206), 2)
        return self.is_pet_icon_visible()

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
            #print(count)
            try:
                # Try accessing from memory
                card_pos = self._spell_memory["unusable"][0]
            except (KeyError, IndexError):
                result = self.find_unusable_spells(limit=1)
                if len(result) is not 0:
                    card_pos = result[0]
                else:
                    break
            #print(card_pos)
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
            #print('Casting', spell)
            self.flush_spell_memory()
            return self.select_spell(spell_type, spell)
        else:
            return False

    def enchant(self, spell_type, spell_name, enchant_type, enchant_name, threshold=0.15, silent_fail=False):
        """ Attemps the enchant 'spell_name' with 'enchant_name' """
        if self.find_spell(spell_type, spell_name, threshold=threshold) and self.find_spell(enchant_type, enchant_name, recapture=False, threshold=threshold):
            #print('Enchanting', spell_name, 'with', enchant_name)
            self.select_spell(enchant_type, enchant_name)
            self.select_spell(spell_type, spell_name)
            self.flush_spell_memory()
            return self
        else:
            # if not silent_fail:
            #     print("One or more spells couldn't be found:",spell_name, enchant_name)
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
        x = (174 * (target_pos - 1)) + 130 +self.region_offset[0]
        y = 50+self.region_offset[1]
        self.click(x, y, delay=.2)
        return self

    def at_friendly(self, target_pos):
        """ Clicks the target, based on position 1, 2, 3, or 4 """
        x = (174 * (target_pos - 1)) + 150 +self.region_offset[0]
        y = 600+self.region_offset[1]
        self.click(x, y, delay=.2)
        return self

    def attack(self, wizard, boss_pos):
        wizard_type = wizard.name

        if(wizard_type == "feinter"):
            """ Feinter plays """
            # Check to see if deck is crowded with unusable spells
            cn = len(self.find_unusable_spells())
            if cn > 2:
                self.discard_unusable_spells(cn)

            # Play
            if self.enchant('Death', 'feint', 'Sun', 'potent') or self.find_spell('Death', 'feint-potent'):
                self.cast_spell('Death', 'feint-potent').at_target(boss_pos)
                return

            elif self.find_spell('Death', 'feint'):
                self.cast_spell('Death', 'feint').at_target(boss_pos)
                return

            else:
                self.pass_turn()
                return
        
        if(wizard_type == "hitter"):
            hitter = self.hitting_school.capitalize()
            if (hitter=="Storm"):
                attack_spell = "tempest"
                attack_e_spell = "tempest-enchanted"
            elif (hitter=="Fire"):
                attack_spell = "meteor-strike"
                attack_e_spell = "meteor-strike-enchanted"
            elif (hitter=="Ice"):
                attack_spell = "blizzard"
                attack_e_spell = "blizzard_enchanted"
            elif (hitter=="Myth"):
                attack_spell = "humungofrog"
                attack_e_spell = "humungofrog_enchanted"
            elif (hitter=="Death"):
                attack_spell = "deer_knight"
                attack_e_spell = "deer_knight_enchanted"
            elif (hitter=="Life"):
                attack_spell = "ratatoskrs_spin"
                attack_e_spell = "ratatoskrs_spin_enchanted"
            """ Hitter plays """
            # Play - 
            if self.find_spell('Star','frenzy'):
                self.cast_spell('Star','frenzy')
                return
            elif self.enchant(hitter, attack_spell, 'Sun', 'epic'):
                self.cast_spell(hitter, attack_e_spell, threshold=.15)
                return
            elif self.find_spell(hitter, attack_e_spell, max_tries=2):
                self.cast_spell(hitter, attack_e_spell)
                return
            else:
                self.pass_turn()
                return
        
        
        if(wizard_type == "blader"):
            """ Blader plays """
            # Check to see if deck is crowded with unusable spells
            cn = len(self.find_unusable_spells())
            if cn > 2:
                self.discard_unusable_spells(cn)

            # Play
            if self.find_spell('Death', 'mass_feint'):
                self.cast_spell('Death', 'mass_feint')
                return
            elif self.enchant('Balance','elemental_blade','Sun','sharpen'):
                self.cast_spell('Balance','enchanted_elemental_blade').at_friendly(2)
                return
            elif self.find_spell('Life', 'pigsie'):
                self.cast_spell('Life', 'pigsie')
                return
            else:
                self.pass_turn()
                return

