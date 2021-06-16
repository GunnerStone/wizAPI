import win32gui
import pyautogui
import cv2
import time
import numpy
import ctypes

# import only system from os 
from os import system, name 


class wizAPI:
    def __init__(self, handle=None):
        self._handle = handle
        self._spell_memory = {}
        self._friends_area = (625, 65, 20, 240)
        self._spell_area = (245, 290, 370, 70)
        self._enemy_area = (68, 26, 650, 35)
        self._friendly_area = (136, 536, 650, 70)
        self._login_area = (307,553+36,187,44)

    
    region_offset = (5,5,0,0)

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

    def is_teamup_at(self,pos=0):
        """ Returns true if there is a teamup option available in window n (0-5)"""
        self.set_active()
        if (0 <= pos <=5):
            #check if pixel value of line is a shade of red
            #if yes, return true
            #if no, return false
            #32pixles * pos should give correct offset
            return self.pixel_matches_color(coords=(500,262+32*pos),rgb=(135, 36, 64),threshold=10)
        else:
            return False
    def select_teamup_at(self,pos=0):
        self.set_active()
        if (0 <= pos <=6):
            #check if pixel value of line is a shade of red
            #if yes, return true
            #if no, return false
            #32pixles * pos should give correct offset
            return self.click(500,262+32*pos)
        else:
            #Do nothing
            return self

    """ DRIVER FOR TEAMUP BOT"""
    successful_teamups = 0
    def join_teamup(self,world=0,page=0,school="Fire"):
        self.successful_teamups +=1
        
        #quicksell after N rounds
        if(self.successful_teamups % 10 == 0):
            self.quick_sell(False, False)
            self.wait(1)
        #Wait for kiosk to prompt user to press x
        self.reset_teamup_kiosk()
        while not self.is_on_kiosk():
            self.wait(.1)
        #boot-up teamup kiosk
        #print("Pressing x on terminal")
        self.press_key('x').wait(1)

        # Navigate and load up desired world for teamup
        self.select_world_teamup(pos=world,page=0)
        #move mouse out of the way of CV
        self.move_mouse(535,492,speed=.1)
        #load the list of displayed dungeons
        teamup_availability = self.give_teamup_available()

        #refresh page until team availability contains at least 1 true
        while (not any(teamup_availability)):
            self.wait(1)
            self.teamup_refresh()
            teamup_availability = self.give_teamup_available()
            

        #try to join first available non-long team
        # finding first True value 
        # using next() and enumerate() 
        teamup_index = next((i for i, j in enumerate(teamup_availability) if j), None) 
        self.select_teamup_at(teamup_index)
        #checks if teamup icon is showing (in queue) or pet icon is missing (already loading in)
        if(self.is_teamup_icon_showing() or (self.is_pet_icon_visible() is not False)):
            #Great we are in
            #wait for a lag in displaying the icon
            self.wait(.5)
            #wait until icon disappears (indicating loading screen into dungeon)
            self.wait_for_teamup_queue()
            self.wait(.1)
            #print("Loading...")
            if (self.is_teamup_canceled()):
                #print("Teamup was canceled, restarting")
                self.remove_queue_error_teamup().wait(1)
                self.reset_teamup_kiosk()
                return
            if (self.is_refresh_showing()):
                #refresh btn is showing so something errored out, restart program
                #logout to reset kiosk 'x' prompt
                self.reset_teamup_kiosk()
                return
            self.wait_pet_loading()
            #print("In Dungeon")
            self.clear_dialog()
            self.move_mouse(717,40)
            #wait for slow computer noobs to get in fight/load
            #otherwise no credit
            self.wait(.25)

            #Walk forward until fight starts
            while not self.is_turn_to_play():
                self.hold_key('w', 1)
            #print("In Fight")

            #print("Next turn found")
            inFight = True
            battle_round = 0

            while inFight:
                

                self.mass_feint_attack_teamup(wizard_type = "hitter",boss_pos=0,hitter=school)
            
                self.wait_for_end_of_round_dialog()
                
                if self.is_idle():
                    inFight = False
                if self.find_button('done'):
                    inFight = False
                if self.find_button('more'):
                    inFight = False
            #print("Battle 1 has ended")
            self.wait(.5)
            #remove any post-battle dialog (happens in few instances)
            self.clear_dialog()

            #potion managemant & use before teleporting home
            if( not self.use_potion_if_needed_tp_house()):
                #if no potion needed, just tp home
                self.teleport_home()
                self.wait_pet_loading()

            return
        else:
            #Teamup no longer available, remove error & try again
            #print("Team no longer joinable, restarting")
            self.remove_queue_error_teamup().wait(1)
            self.reset_teamup_kiosk()
            #self.join_teamup(world=world,page=0)
            return

    def is_refresh_showing(self):
        x, y = (523,474)#563,394
        self.set_active()
        large = self.screenshotRAM((x,y,19,24))
        result = self.match_image(largeImg=large, smallImg='buttons/refresh.png',threshold=.1)
        if result is not False:
            return True
        else:
            return False
    def give_teamup_available(self):
        """ Assumes Kiosk is already opened"""
        #Click world we care about
        #pages are saved in cache so no switching pages here, only selecting worlds
        
        #see how many active teamups are available on this world
        teamup_availability = [False,False,False,False,False,False] #6 slots
        for i in range(6):
            if self.is_teamup_at(i) is not False:
                #print("Found teamup at location "+str(i))
                teamup_availability[i] = True 
        #filter out long instances
        for i in range(6):
            if self.is_teamup_long(i) == True:
                #print("Found LONG at location "+str(i))
                teamup_availability[i] = False
        return teamup_availability

    def is_teamup_long(self,pos=0):
        """ Returns true if there is a timer icon on teamup (indicates long instance)"""
        self.set_active()
        if (0 <= pos <=5):
            x, y = (560,244)
            self.set_active()
            large = self.screenshotRAM((x,y+32*pos,30,30))
            result = self.match_image(largeImg=large, smallImg='icons/timer.png',threshold=.1)
            if result is not False:
                return True
            else:
                return False
        else:
            return False

    def close_teamup_kiosk(self):
        """ Refreshes availabel teamups """
        self.set_active()
        x, y = (565,492)
        self.click(x,y)
        return self

    def reset_teamup_kiosk(self):
        """Closes out of kiosk & resets 'x' prompt"""
        self.close_teamup_kiosk()
        #wiggle back & forth to reset 'x' prompt
        self.hold_key('w',.5)
        self.hold_key('s', .1)
        self.hold_key('w', .5)

    def is_teamup_canceled(self):
        x, y = (464,393)#563,394
        self.set_active()
        large = self.screenshotRAM((x,y,103,27))
        result = self.match_image(largeImg=large, smallImg='buttons/ok.png',threshold=.1)
        if result is not False:
            return True
        else:
            return False
    def is_teamup_icon_showing(self):
        self.set_active()
        x, y = (717,40)#563,394
        # # self.move_mouse(x, y)
        large = self.screenshotRAM((x,y,15,15))
        result = self.match_image(largeImg=large, smallImg='icons/teamup_btn.png',threshold=.1)
        if result is not False:
            return True
        else:
            return False
    
    def select_world_teamup(self,pos=0,page=0):
        self.set_active()
        if(0<=pos<=5):
            #scroll until at desired page
            for i in range(page):
                #x,y pos of the yellow page-arrow
                x, y = (570,212)
                self.click(x,y)

            #click on desired world pos
            x, y = (250,212)
            x = x+55*pos
            self.click(x,y)
            return self
        else:
            return self
    def teamup_refresh(self):
        """ Refreshes availabel teamups """
        self.set_active()
        x, y = (535,492)
        self.click(x,y)
        return self
    
    def is_queued_teamup(self):
        """ Returns true if wizard is queued on teamup"""
        self.set_active()
        x, y = (338,400)
        large = self.screenshotRAM((x,y,130,26))
        result = self.match_image(largeImg=large, smallImg='buttons/cancel_teamup.png',threshold=.1)
        if result is not False:
            return True
        else:
            return False

    def wait_for_teamup_queue(self):
        #waits until the teamup queue goes away
        self.set_active()
        x, y = (717,40)#563,394
        
        result = True
        while result is not False:
            large = self.screenshotRAM((x,y,15,15))
            result = self.match_image(largeImg=large, smallImg='icons/teamup_btn.png',threshold=.17)
            self.wait(.5)
        return self

    def cancel_queue_teamup(self):
        #clicks through buttons to cancel teamup queue
        #useful if queue is taking too long
        self.click(403,413)
        self.click(403,383)
        return self

    def teleport_home(self):
        self.press_key('home')
        return self

    def is_on_kiosk(self):
        """ Checks if there is 'x' to interract dialogue for teamup """
        self.set_active()
        x, y = (386,541)
        large = self.screenshotRAM((x,y,26,24))
        result = self.match_image(largeImg=large, smallImg='icons/x_btn.png',threshold=.1)
        if result is not False:
            return True
        else:
            return False

    def remove_queue_error_teamup(self):
        #if team is no longer avaiable, an error will display on screen
        #if wizard tries to click kiosk while already in a queue, same error will popup
        #clicks ok
        self.click(533,383).wait(.1)
        self.click(533,400).wait(.1)
        self.click(563,395).wait(.1)
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

    def use_potion_if_needed_tp_house(self,health_percent=33):
        self.set_active()
        mana_low = self.is_mana_low()
        health_low = self.is_health_low(health_percent)
        # print("Mana low? :"+str(mana_low))
        # print("Health low? :" +str(health_low))
        if mana_low or health_low:
            #print('Clicking Potion')
            self.click(160, 590, delay=.2) 
            self.wait(1)
            if(self.is_mana_low() or self.is_health_low(health_percent)):
                #kingsisle has a dumb bug where you cant tp mark location from instance
                #so teleport home, THEN to potion lady
                self.teleport_home()
                self.wait_pet_loading()
                self.wait(.1)
                self.recall_location()
                self.wait_pet_loading()
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
                    self.wait(16)
                    self.teleport_home()
                    self.wait_pet_loading()
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
                    self.wait(16)

                    #Gets back to dungeon
                    self.teleport_home()
                    self.wait_pet_loading()
                return True
        return False

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

    def bazaar_sell(self, friendly_img, teleport=False, teleport_friend_img="", await_loading=True):
        index = 0
        TypeIndex = 0
        
        if(teleport):
            self.teleport_to_friend(teleport_friend_img)
        else:
            self.recall_location()

        if(await_loading):
            #Waits for user to finish loading
            while not self.is_logo_bottom_left_or_right_loading():
                time.sleep(.2)

            while not self.is_idle():
                time.sleep(.5)

            if(teleport == False):
                self.mark_location()
        
        else:
            self.mark_location()
            

        # Goes to Sell tab
        self.press_key('x')
        self.click(230, 105)

        #Clicks first sellable item
        self.click(470, 270)

        while True:
            if(index < 7):
                if(self.match_image(self.screenshotRAM((175, 433, 150, 30)), 'buttons/sell.png', threshold=.1)):
                    # Clicks sell button
                    self.click(240, 457)
                    # Clicks Yess
                    self.click(405, 405).wait(.2)
                else:
                    index = index + 1
                    self.click(470, 270 + (index * 35))
            else:
                if(self.match_image(self.screenshotRAM((665, 325, 40, 70)), 'buttons/right_arrow.png', threshold=.1)):
                    # Click Arrow to next page
                    self.click(685, 365)
                    # Click first item on next page
                    index = -1
                    self.click(470, 270 + (index * 35))
                    index = 0
                    self.click(470, 270 + (index * 35))
                else:
                    #Moves to next "item" type
                    if(TypeIndex < 7):
                        TypeIndex = TypeIndex + 1
                        self.click(125 + (TypeIndex * 60), 170)
                        #Clicks first sellable item on new page
                        self.click(470, 270)
                        index = 0
                    else:    
                        break
        
        #Exits bazaar
        self.click(685, 535).wait(.2)

        # Goes back to friend
        self.teleport_to_friend(friendly_img)

        #Waits for user to finish loading
        while not self.is_logo_bottom_left_or_right_loading():
            time.sleep(.2)

        while not self.is_idle():
            time.sleep(.5)

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
        # else:
        #     print("Give a valid quest position")
        #close quest menu
        self.press_key('q')
        #get mouse out of the way of other things
        (self.set_active()
            .move_mouse(669, 189, speed=0.5))

    def mark_location(self):
        self.press_key('pagedown')

    def recall_location(self):
        self.press_key('pageup')

    def clear_dialog(self):
        self.move_mouse(350, 350)
        while(self.find_button('done') or self.find_button('more')):
            self.press_key('space').wait(.2)

    def clear_quest_buttons(self):
        while(self.match_image(self.screenshotRAM(region=(740, 390, 60, 60)), 'buttons/quest_dialog.png', threshold=.2)):
            self.click(770, 430, button='right', delay=.2)
            self.move_mouse(730, 430).wait(2)

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

    #Loremaster Random attack sequence
    def lm_attack(self, wizard_type, boss_pos):
        wizard_type = wizard_type.split('.')[0]

        #print(wizard_type)

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
            
            if self.enchant('Storm', 'tempest', 'Sun', 'epic'):
                self.cast_spell('Storm', 'tempest-enchanted')
            
            elif self.find_spell('Storm', 'tempest-enchanted', max_tries=2):
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
    def mass_feint_attack(self, wizard_type, boss_pos, hitter="Storm"):
        wizard_type = wizard_type.split('.')[0]

        #print(wizard_type)

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
            hitter = hitter.capitalize()
            #print("Hitter is:"+str(hitter))
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
            elif self.enchant(hitter, attack_spell, 'Sun', 'epic'):
                self.cast_spell(hitter, attack_e_spell, threshold=.15)
            elif self.find_spell(hitter, attack_e_spell, max_tries=2):
                self.cast_spell(hitter, attack_e_spell)
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
            elif self.enchant('Balance','elemental_blade','Sun','sharpen'):
                self.cast_spell('Balance','enchanted_elemental_blade').at_friendly(2)
            elif self.find_spell('Life', 'pigsie'):
                self.cast_spell('Life', 'pigsie')
            else:
                self.pass_turn()

    #One round strat for most mobs
    def mass_feint_attack_teamup(self, wizard_type, boss_pos, hitter="Storm"):
        wizard_type = wizard_type.split('.')[0]

        #print(wizard_type)

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
            hitter = hitter.capitalize()
            #print("Hitter is:"+str(hitter))
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
            # Check to see if deck is crowded with unusable spells
            cn = len(self.find_unusable_spells())
            # Discard the spells
            if cn > 2:
                self.discard_unusable_spells(cn)

            # Play - Storm
            if self.find_spell('Star','frenzy',max_tries=2):
                self.cast_spell('Star','frenzy')
            elif self.enchant(hitter, attack_spell, 'Sun', 'epic'):
                self.cast_spell(hitter, attack_e_spell, threshold=.15)
            elif self.find_spell(hitter, attack_e_spell, max_tries=2):
                self.cast_spell(hitter, attack_e_spell)
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
            else:
                self.pass_turn()
        
    #One round strat for most mobs
    def mass_feint_attack_lore(self, wizard_type, boss_pos):
        wizard_type = wizard_type.split('.')[0]

        #print(wizard_type)

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
            

            if self.enchant('Storm', 'tempest', 'Sun', 'epic'):
                self.cast_spell('Storm', 'tempest-enchanted')
            elif self.find_spell('Storm', 'tempest-enchanted', max_tries=2):
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

        #print(wizard_type)

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
                    self.cast_spell('Storm', 'tempest-enchanted')
                else:
                    self.pass_turn()
            else:
                if self.find_spell('Storm', 'tempest-enchanted', threshold=0.10):
                    self.cast_spell('Storm', 'tempest-enchanted')

                elif self.enchant('Storm', 'tempest', 'Sun', 'epic'):
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
                #Triple cleanse hitter
                elif self.find_spell('Storm', 'triple_cleanse_charm', threshold=0.10):
                    self.cast_spell('Storm', 'triple_cleanse_charm',threshold=.10).at_friendly(2) #Casts at third wizard
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

    def AMM_paradox_attack(self, wizard_type, boss_pos, boss_battle=False):
        wizard_type = wizard_type.split('.')[0]

        #print(wizard_type)

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
                #cast sharpened elemental blade
                elif self.enchant('Balance', 'elemental_blade', 'Sun', 'sharpen_b',threshold=.10):
                    self.cast_spell('Balance', 'enchanted_elemental_blade',threshold=.10).at_friendly(2) #Casts at third wizard

                else:
                    self.pass_turn()
            else:
                # Play

                #cast sharpened elemental blade
                if self.enchant('Balance', 'elemental_blade', 'Sun', 'sharpen_b',threshold=.10):
                    self.cast_spell('Balance', 'enchanted_elemental_blade',threshold=.10).at_friendly(2) #Casts at third wizard

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
                if self.find_spell('Storm', 'storm_prism', threshold=0.10):
                    self.cast_spell('Storm', 'storm_prism').at_target(boss_pos)

                elif self.find_spell('Storm', 'tempest-enchanted', threshold=0.10):
                    self.cast_spell('Storm', 'tempest-enchanted')
                
                elif self.enchant('Storm', 'tempest', 'Sun', 'epic'):
                    self.cast_spell('Storm', 'tempest-enchanted')
                else:
                    self.pass_turn()
            else:
                if self.enchant('Storm', 'tempest', 'Sun', 'epic'):
                    self.cast_spell('Storm', 'tempest-enchanted')

                elif self.find_spell('Storm', 'tempest-enchanted', threshold=0.10):
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
                elif self.enchant('Balance', 'elemental_blade', 'Sun', 'sharpen',threshold=.10):
                    self.cast_spell('Balance', 'enchanted_elemental_blade',threshold=.10).at_friendly(2) #Casts at third wizard
                else:
                    self.pass_turn()
            else:
                if self.find_spell('Death', 'mass_feint', threshold=0.10):
                    self.cast_spell('Death', 'mass_feint')
                else:
                    self.pass_turn()  

    def treemugger_attack(self, wizard_type, boss_pos):
            wizard_type = wizard_type.split('.')[0]

            #print(wizard_type)

            if(wizard_type == "feinter"):
                """ Feinter plays """
                # Check to see if deck is crowded with unusable spells
                cn = len(self.find_unusable_spells())
                if cn > 2:
                    self.discard_unusable_spells(cn)

                # Play
                
                #feint the boss on first round
                if self.enchant('Death', 'feint', 'Sun', 'potent'):
                    self.cast_spell('Death', 'feint-potent').at_target(boss_pos)

                elif self.find_spell('Death', 'feint-potent', threshold=0.10):
                    self.cast_spell('Death', 'feint-potent').at_target(boss_pos)               
                
                #cast sharpened elemental blade
                elif self.enchant('Balance', 'elemental_blade', 'Sun', 'sharpen',threshold=.10):
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
                # Play
                if self.find_spell('Death', 'feint', threshold=0.10):
                    self.cast_spell('Death', 'feint').at_target(boss_pos)

                elif self.find_spell('Storm', 'tempest-enchanted', threshold=0.10):
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
                #mass fient boss first round
                if self.find_spell('Death', 'mass_feint', threshold=0.10):
                    self.cast_spell('Death', 'mass_feint')
                #aegis blade
                elif self.enchant('Balance', 'elemental_blade', 'Sun', 'aegis'):
                    self.cast_spell('Balance', 'enchanted_elemental_blade').at_friendly(2) #Casts at third wizard
                #Triple cleanse hitter
                elif self.find_spell('Storm', 'triple_cleanse_charm', threshold=0.10):
                    self.cast_spell('Storm', 'triple_cleanse_charm',threshold=.10).at_friendly(2) #Casts at third wizard
                elif self.find_spell('Balance', 'enchanted_elemental_blade', threshold=0.10): #Checks if left over enchanted blade is not cast
                    self.cast_spell('Balance', 'enchanted_elemental_blade')
                elif self.find_spell('Life', 'pigsie', threshold=0.10):
                    self.cast_spell('Life', 'pigsie')
                elif self.find_spell('Life', 'unicorn', threshold=0.10):
                    self.cast_spell('Life', 'unicorn')
                else:
                    self.pass_turn() 

    def morganthe_attack(self, wizard_type, boss_pos):
            wizard_type = wizard_type.split('.')[0]
            if(wizard_type == "feinter"):
                """ Feinter plays """
                # Check to see if deck is crowded with unusable spells
                cn = len(self.find_unusable_spells())
                if cn > 2:
                    self.discard_unusable_spells(cn)

                # Play
                if self.find_spell('Balance', 'b_elemental_blade', threshold=0.10):
                    self.cast_spell('Balance', 'b_elemental_blade').at_friendly(2) #Casts at third wizard
                elif self.enchant('Balance', 'elemental_blade', 'Sun', 'sharpen_b'):
                    self.cast_spell('Balance', 'enchanted_elemental_blade').at_friendly(2) #Casts at third wizard
                elif self.find_spell('Balance', 'enchanted_elemental_blade', threshold=0.10):
                    self.cast_spell('Balance', 'enchanted_elemental_blade').at_friendly(2) #Casts at third wizard
                
                # Play
                elif self.enchant('Death', 'feint', 'Sun', 'potent'):
                    self.cast_spell('Death', 'feint-potent').at_target(3)
                elif self.find_spell('Death', 'feint-potent', threshold=0.10):
                    self.cast_spell('Death', 'feint-potent').at_target(3) #Casts at third wizard
                elif self.find_spell('Death', 'feint'):
                    self.cast_spell('Death', 'feint').at_target(3)
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
                if self.find_spell('Storm', 'mass_prism', threshold=0.14):
                    self.cast_spell('Storm', 'mass_prism')
                elif self.enchant('Storm', 'storm_blade', 'Sun', 'sharpen'):
                    self.cast_spell('Storm', 'enchanted_storm_blade').at_friendly(2) #Casts at third wizard
                elif self.find_spell('Storm', 'enchanted_storm_blade', threshold=0.10):
                    self.cast_spell('Storm', 'enchanted_storm_blade').at_friendly(2) #Casts at third wizard
                elif self.enchant('Storm', 'tempest', 'Sun', 'epic'):
                    self.find_spell('Storm', 'tempest-enchanted', threshold=0.10)
                    self.cast_spell('Storm', 'tempest-enchanted')
                elif self.find_spell('Storm', 'tempest-enchanted', threshold=0.10):
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
                
                if self.enchant('Balance', 'elemental_blade', 'Sun', 'sharpen'):
                    self.cast_spell('Balance', 'enchanted_elemental_blade').at_friendly(2) #Casts at third wizard
                elif self.find_spell('Balance', 'enchanted_elemental_blade', threshold=0.10):
                    self.cast_spell('Balance', 'enchanted_elemental_blade').at_friendly(2) #Casts at third wizard
                elif self.find_spell('Death', 'mass_feint', threshold=0.10):
                    self.cast_spell('Death', 'mass_feint')
                elif self.find_spell('Storm', 'b_storm_blade', threshold=0.10):
                    self.cast_spell('Storm', 'b_storm_blade').at_friendly(2) #Casts at third wizard
                else:
                    self.pass_turn() 
    def chronus_attack(self, wizard_type, boss_pos,round_num):
            wizard_type = wizard_type.split('.')[0]

            #If its first turn, cast stun block
            if (round_num < 2):
                if(wizard_type == "feinter"):
                    """ Feinter plays """
                    # Play
                    self.cast_spell('Ice', 'stun_block').at_friendly(4) #Casts at first wizard
                elif (wizard_type == "hitter"):
                    """ Hitter plays """
                    # Play
                    self.cast_spell('Ice', 'stun_block').at_friendly(2) #Casts at first wizard
                elif (wizard_type == "blader"):
                    """ Blader plays """
                    # Play
                    self.cast_spell('Ice', 'stun_block').at_friendly(3) #Casts at first wizard
            else:
                if(wizard_type == "feinter"):
                    """ Feinter plays """
                    # Play
                    if self.enchant('Death', 'feint', 'Sun', 'potent'):
                        self.cast_spell('Death', 'feint-potent').at_target(boss_pos)  
                    elif self.find_spell('Death', 'feint', threshold=0.14):
                        self.cast_spell('Death', 'feint').at_target(boss_pos) 
                    else:
                        self.pass_turn()

                if(wizard_type == "hitter"):
                    """ Hitter plays """
                    # Play
                    if self.find_spell('Death', 'b_feint', threshold=0.14):
                        self.cast_spell('Death', 'b_feint').at_target(boss_pos)
                    elif self.find_spell('Fire', 'incindiate', threshold=0.10):
                        self.cast_spell('Fire', 'incindiate')             
                    else:
                        self.pass_turn()

                if(wizard_type == "blader"):
                    """ Blader plays """
                    # Play
                    if self.find_spell('Star', 'furnace', threshold=0.14):
                        self.cast_spell('Star', 'furnace')
                    elif self.enchant('Fire', 'scald', 'Sun', 'epic'):
                        self.cast_spell('Fire', 'scald-enchanted')           
                    else:
                        self.pass_turn()
    def riddler_attack(self, wizard_type, boss_pos,round_num):
            wizard_type = wizard_type.split('.')[0]

            self.move_mouse(400,40)
            if(wizard_type == "feinter"):
                """ Feinter plays """
                # Play
                if self.find_spell('Death', 'mass_feint', threshold=0.14):
                    self.cast_spell('Death', 'mass_feint')
                elif self.enchant('Balance', 'elemental_blade', 'Sun', 'sharpen'):
                    self.cast_spell('Balance', 'enchanted_elemental_blade',threshold=0.8).at_friendly(3) 
                elif self.find_spell('Balance','enchanted_elemental_blade',threshold=0.8):
                    self.cast_spell('Balance', 'enchanted_elemental_blade').at_friendly(3) 
                else:
                    self.pass_turn()

            if(wizard_type == "hitter"):
                """ Hitter plays """
                # Play
                if self.enchant('Balance', 'elemental_blade', 'Sun', 'sharpen_b'):
                    self.cast_spell('Balance', 'enchanted_elemental_blade').at_friendly(3) 
                elif self.find_spell('Balance','enchanted_elemental_blade'):
                    self.cast_spell('Balance', 'enchanted_elemental_blade').at_friendly(3) 
                elif self.find_spell('Fire', 'incindiate', threshold=0.10):
                    self.cast_spell('Fire', 'incindiate')             
                else:
                    self.pass_turn()

            if(wizard_type == "blader"):
                """ Blader plays """
                # Play
                if self.find_spell('Star', 'frenzy', threshold=0.14):
                    self.cast_spell('Star', 'frenzy')
                elif self.enchant('Fire', 'scald', 'Sun', 'epic'):
                    self.cast_spell('Fire', 'scald-enchanted')    
                elif self.find_spell('Fire','scald-enchanted'):
                    self.cast_spell('Fire','scald-enchanted')       
                else:
                    self.pass_turn()
            self.move_mouse(400,40)
    def medulla_attack(self, wizard_type, boss_pos,round_num):
            wizard_type = wizard_type.split('.')[0]

            self.move_mouse(400,40)
            if(wizard_type == "feinter"):
                """ Feinter plays """
                # Play
                if self.find_spell('Death', 'mass_feint', threshold=0.14):
                    self.cast_spell('Death', 'mass_feint')
                elif self.enchant('Balance', 'elemental_blade', 'Sun', 'sharpen'):
                    self.cast_spell('Balance', 'enchanted_elemental_blade',threshold=0.8).at_friendly(3) 
                elif self.enchant('Balance', 'elemental_trap', 'Sun', 'potent'):
                    self.cast_spell('Balance', 'enchanted_elemental_trap',threshold=0.8).at_target(1)
                elif self.enchant('Balance', 'elemental_blade', 'Sun', 'sharpen_b'):
                    self.cast_spell('Balance', 'enchanted_elemental_blade').at_friendly(3) 
                elif self.find_spell('Balance','enchanted_elemental_blade'):
                    self.cast_spell('Balance', 'enchanted_elemental_blade').at_friendly(3) 
                else:
                    self.pass_turn()

            if(wizard_type == "hitter"):
                """ Hitter plays """
                # Play
                if self.enchant('Balance', 'elemental_blade', 'Sun', 'sharpen_b'):
                    self.cast_spell('Balance', 'enchanted_elemental_blade').at_friendly(3) 
                elif self.find_spell('Fire', 'incindiate', threshold=0.10):
                    self.cast_spell('Fire', 'incindiate')
                elif self.enchant('Fire', 'fuel', 'Sun', 'potent'):
                    self.cast_spell('Fire', 'fuel-enchanted').at_target(1)
                elif self.find_spell('Fire', 'fuel'):
                    self.cast_spell('Fire','fuel').at_target(1)        
                elif self.find_spell('Fire','firetrap'):
                    self.cast_spell('Fire','firetrap').at_target(1)
                else:
                    self.pass_turn()

            if(wizard_type == "blader"):
                """ Blader plays """
                # Play
                if self.find_spell('Star', 'frenzy'):
                    self.cast_spell('Star', 'frenzy')
                elif self.enchant('Fire', 'scald', 'Sun', 'epic'):
                    self.cast_spell('Fire', 'scald-enchanted')    
                elif self.find_spell('Fire','scald-enchanted'):
                    self.cast_spell('Fire','scald-enchanted')
                elif self.find_spell('Fire','mass-fire-trap'):
                    self.cast_spell('Fire','mass-fire-trap')
                elif self.find_spell('Fire','fireblade'):
                    self.cast_spell('Fire','fireblade').at_friendly(3)     
                elif self.enchant('Fire', 'firedragon', 'Sun', 'epic'):
                    self.cast_spell('Fire', 'firedragon-enchanted')      
                else:
                    self.pass_turn()
            self.move_mouse(400,40)