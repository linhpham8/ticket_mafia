import subprocess,os,threading,datetime;
from robot.libraries.BuiltIn import BuiltIn
from robot.libraries.Screenshot import Screenshot
import numpy as np
import sys
import time

def get_screen_size():
    appiumlib = BuiltIn().get_library_instance('AppiumLibrary')
    window_size = appiumlib.get_element_size("//XCUIElementTypeApplication")
    print(window_size)
    max_width = window_size["width"] - 1
    max_height = window_size["height"] - 1 
    return max_width,max_height


    
    
def swipe_down(maxAttempt):
    count =0
    max = int(maxAttempt)
    maxwidth,maxheight = get_screen_size()
    starty = int(maxheight * 0.50)
    endy = int(maxwidth*0.20) 
    startx = int(maxwidth*0.50)
    appiumlib = BuiltIn().get_library_instance('AppiumLibrary')
    
  
    while count<max:
        count=count+1
        appiumlib.swipe(startx, starty, startx, endy)
        time.sleep(3)

def swipe_up(maxAttempt):
    count =0
    max = int(maxAttempt)
    maxwidth,maxheight = get_screen_size()
    startx = int(maxwidth*0.50)
    starty = int(maxwidth*0.50) 
    
    endx = int(maxheight * 0)
    endy = int(maxheight * 1.5)
    
    appiumlib = BuiltIn().get_library_instance('AppiumLibrary')
    #print("=============")
    #print(startx, starty , endx, endy)
     
    while count<max:
        count=count+1
        appiumlib.swipe(startx, starty , endx, endy)
        time.sleep(3)        

        
def swipe_right(maxAttempt):
    count =0
    max = int(maxAttempt)
    maxwidth,maxheight = get_screen_size()
    starty = int(maxheight * 0.8)
    startx = int(maxwidth*0.8)
    endx = int(maxwidth*0.20) 
    
    appiumlib = BuiltIn().get_library_instance('AppiumLibrary')
    
  
    while count<max:
        count=count+1
        appiumlib.swipe(startx, starty, endx, starty)
        time.sleep(3)
    



