from machine import Signal
from BSP import BSP
import sys
import gc
import ubinascii

if sys.implementation._machine == 'Raspberry Pi Pico W with RP2040':
    import network       # https://docs.micropython.org/en/latest/library/network.WLAN.html#network.WLAN.status
    STA = None
    AP = None
    
    class PicoNet():
        
        def __init__(self):
            print(" -> Network initialization ...           ", end='')
            self.STA = network.WLAN(network.STA_IF)
            self.AP = network.WLAN(network.AP_IF)
            print('done')
       
    @property
    def AP_MAC(self):
        if self.AP.active():
            return ubinascii.hexlify(self.AP.config('mac'),':').decode().upper()
        else:
            return "inactive"
        
    @property
    def STA_MAC(self):
        if self.STA.active():
            return ubinascii.hexlify(self.STA.config('mac'),':').decode().upper()
        else:
            return "inactive"

class GlobalVars():
    Net = None
    Board = None
    
    def __init__(self):
        if sys.implementation._machine == 'Raspberry Pi Pico W with RP2040':
            self.Net = PicoNet()
        self.Board = BSP()
        if self.Net != None:
            self.Board.WiFi_STA(self.Net.STA)
            self.Board.WiFi_AP(self.Net.AP)
        
    def deinit(self):
        if self.Net != None and self.Net.AP.active():
            self.Net.AP.active(False)
        self.Board.deinit()