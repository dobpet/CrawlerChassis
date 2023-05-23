from machine import Pin, PWM, I2C, SPI, ADC, RTC
import uasyncio, utime, framebuf
import neopixel
from SSD1306 import SSD1306_I2C
from OLED_Graphics import *
import Font
from WiFiServer_AP import WebServer
from settings import param
    
    
class BSP():
    ####################################################################################################
    # CONSTANTS                                                                                        #
    ####################################################################################################
    BTN_MIN_PRESS_TIME       = const(5)
    BTN_MAX_SHORT_PRESS_TIME = const(500)
    BTN_LONG_PRESS_TIME      = const(2000)
    pix_res_x                = const(128)     # SSD1306 horizontal resolution
    pix_res_y                = const(64)      # SSD1306 vertical resolution
    ADC_LSB = 3.3 / (65535)
    
    SCR_STATUS_START         = const(0)
    SCR_STATUS_END           = const(3)
    
    ####################################################################################################
    # VARIABLES                                                                                        #
    ####################################################################################################
    Sys_I2C = None

    OLED = None                               # display
    NeoLEDs = None                            # NeoPixel LEDs
    Time = None                                # Real Time Clock
    __btnESC = Pin(3, Pin.IN, Pin.PULL_UP)    # ESC button (left top)
    __btnMinus = Pin(22, Pin.IN, Pin.PULL_UP) # - button (left bottom)
    __btnENT = Pin(20, Pin.IN, Pin.PULL_UP)   # ENT button (right top)
    __btnPlus = Pin(21, Pin.IN, Pin.PULL_UP)  # + button (right bottom)
    __btn_pt = [None, None, None, None]       # Buttons press ticks tuple
    __NeoLED = Pin(6, Pin.OUT)                # NeoPixel LEDs pin
    __PwrON = Pin(2, Pin.OUT)                 # Power ON pin
    __I2C1_SCL = Pin(11)
    __I2C1_SDA = Pin(10)
    
  
    
    __AUXIO_pins = [Pin(14, Pin.OUT, value=0),
                    Pin(13, Pin.OUT, value=0),
                    Pin(12, Pin.OUT, value=0),
                    Pin(5, Pin.OUT, value=0),
                    Pin(1, Pin.OUT, value=0),
                    Pin(0, Pin.OUT, value=0)]
    StartConsumeEl_1 = False #delete a row
    StartConsumeEl = [False]*6
    
    __5IO0_pin = Pin(4, Pin.OUT, value=0)#top left
    __5IO1_pin = Pin(15, Pin.OUT, value=0)#top right
    Value_5IOx = [False]*2
    #Value_5IOx[0] = True
    
    __myWebServer = None
    
    
    __BaseScreen = None                       # Current displayed screen
    __ScreenRequest = None                    # Requested screen
    __scrTitle = None                         # Title for screen
    __scrSubtitle = None                      # Subtitle for screen
    __scrHasTitle = None                      # Screen has title displayed
    __WiFiSTA = None
    __WiFiAP = None
    Periodic = None                           # Periodic task
    
    __btnESC_ShortPress = None
    __btnESC_LongPress = None
    __btnMinus_ShortPress = None
    __btnMinus_LongPress = None
    __btnENT_ShortPress = None
    __btnENT_LongPress = None
    __btnPlus_ShortPress = None
    __btnPlus_LongPress = None
    
    ####################################################################################################
    # PERIODIC ASYNCHRONOUS FUNCTION                                                                   #
    ####################################################################################################
    async def PeriodicAsync(self):
        InitCycles = 0
        CycleCnt = 0
        Ticks_500ms = None
        Ticks_200ms = None
        Time_Flags = 0
        sec = self.Time.datetime()[6]
        while self.Time.datetime()[6] == sec:
            pass
        v = utime.ticks_ms()
        Ticks_500ms = Ticks_200ms = v
        
        start_time = [utime.ticks_ms(), utime.ticks_ms(), utime.ticks_ms(), utime.ticks_ms(), utime.ticks_ms(), utime.ticks_ms(), utime.ticks_ms()]
        stop_time = [utime.ticks_ms(), utime.ticks_ms(), utime.ticks_ms(), utime.ticks_ms(), utime.ticks_ms(), utime.ticks_ms(), utime.ticks_ms()]
        while True:
            #---------------output-------------------------------------------------------------
        
            
            StartConsumeEl = False                  
            for x in range(0, 6):
                if self.StartConsumeEl[x]:
                    self.__AUXIO_pins[x].value(1)
                    StartConsumeEl = True
                else:
                    self.__AUXIO_pins[x].value(0)
                    

            # signalization of output switching
            if StartConsumeEl:
                self.NeoLEDs[0] = (10, 0, 0)
                self.Value_5IOx[1] = True
                self.__5IO1_pin.value(1)
            else:
                self.NeoLEDs[0] = (0, 0, 10)
                self.Value_5IOx[1] = False
                self.__5IO1_pin.value(0)
                

            # signalization of web connection
            if self.__myWebServer.blick:
                self.NeoLEDs[1] = (0, 0, 10)
            else:
                self.NeoLEDs[1] = (0, 0, 0)
            self.NeoLEDs.write()
            #---------------end output---------------------------------------------------------
            if self.__btnESC.value() == 0 and self.__btn_pt[0] != None:
                delta = utime.ticks_diff(utime.ticks_ms(), self.__btn_pt[0])
                if delta > BTN_LONG_PRESS_TIME:
                    self.__btn_pt[0] = None
                    if self.__btnESC_LongPress != None:
                        self.__btnESC_LongPress()
            if self.__btnMinus.value() == 0 and self.__btn_pt[1] != None:
                delta = utime.ticks_diff(utime.ticks_ms(), self.__btn_pt[1])
                if delta > BTN_LONG_PRESS_TIME:
                    self.__btn_pt[1] = None
                    if self.__btnMinus_LongPress != None:
                        self.__btnMinus_LongPress()
            if self.__btnENT.value() == 0 and self.__btn_pt[2] != None:
                delta = utime.ticks_diff(utime.ticks_ms(), self.__btn_pt[2])
                if delta > BTN_LONG_PRESS_TIME:
                    self.__btn_pt[2] = None
                    if self.__btnENT_LongPress != None:
                        self.__btnENT_LongPress()
            if self.__btnPlus.value() == 0 and self.__btn_pt[3] != None:
                delta = utime.ticks_diff(utime.ticks_ms(), self.__btn_pt[3])
                if delta > BTN_LONG_PRESS_TIME:
                    self.__btn_pt[3] = None
                    if self.__btnPlus_LongPress != None:
                        self.__btnPlus_LongPress()
            if utime.ticks_diff(utime.ticks_ms(), Ticks_500ms) > 500:
                Ticks_500ms += 500
                Time_Flags ^= 1
                Time_Flags |= 4
            if utime.ticks_diff(utime.ticks_ms(), Ticks_200ms) > 200:
                Ticks_200ms += 200
                Time_Flags ^= 2
                Time_Flags |= 4
            if InitCycles != None:                
                self.OLED.vline(InitCycles + 2, 59, 3, 1)
                InitCycles += 2;
                if InitCycles > 124:
                    InitCycles = None
                    self.OLED.fill(0)
                    self.__ScreenRequest = 0
                self.OLED.show()
            else:
                if (Time_Flags & 4) == 4:
                    Time_Flags &= ~4
                    scrUpdate = True
                    if self.__BaseScreen == None or self.__BaseScreen != self.__ScreenRequest:
                        self.OLED.fill(0)
                        scrUpdate = False
                        self.__BaseScreen = self.__ScreenRequest
                    if self.__BaseScreen == 0:
                        (self.__scrTitle, self.__scrSubtitle, self.__scrHasTitle) = ScreenWiFi(self.OLED, Time_Flags, self.__myWebServer, scrUpdate)
                    elif self.__BaseScreen == 1:
                        #(self.__scrTitle, self.__scrSubtitle, self.__scrHasTitle) = ScreenPowerStatus(self.OLED, Time_Flags, scrUpdate)
                        (self.__scrTitle, self.__scrSubtitle, self.__scrHasTitle) = ScreenWiFi(self.OLED, Time_Flags, self.__myWebServer, scrUpdate)
                    elif self.__BaseScreen == 2:
                        #(self.__scrTitle, self.__scrSubtitle, self.__scrHasTitle) = ScreenInputStatus(self.OLED, Time_Flags, scrUpdate)
                        (self.__scrTitle, self.__scrSubtitle, self.__scrHasTitle) = ScreenWiFiAP(self.OLED, Time_Flags, self.__myWebServer, scrUpdate)
                    elif self.__BaseScreen == 3:
                        (self.__scrTitle, self.__scrSubtitle, self.__scrHasTitle) = ScreenOutputStatus(self.OLED, Time_Flags, self.StartConsumeEl, self.Value_5IOx , scrUpdate)
                    
                    if self.__scrHasTitle:
                        PaintTitle(self.OLED, Time_Flags, self.__scrTitle, self.__scrSubtitle, self.__WiFiSTA, self.__WiFiAP)
                    
                    if not scrUpdate:
                        num = None
                        pos = None
                        if SCR_STATUS_START <= self.__BaseScreen <= SCR_STATUS_END:
                            num = SCR_STATUS_END - SCR_STATUS_START
                            pos = self.__BaseScreen
                        if num != None and pos != None:
                            for x in range(0, 128, 3):
                                self.OLED.pixel(x, 62, 1)
                            wdth = int(128 / (num + 1))
                            x = pos * wdth
                        rect(self.OLED, x, 61, wdth, 3, True)    
                        
                    self.OLED.show()
                    
            await uasyncio.sleep_ms(200)
    
    ####################################################################################################
    # BUTTONS IRQ HANDLER                                                                              #
    #################################################################################################### 
    def btn_IRQHandler(self, Pin):
        if Pin == self.__btnESC:
            if self.__btnESC.value() == 0 and self.__btn_pt[0] == None:
                self.__btn_pt[0] = utime.ticks_ms()
            elif self.__btnESC.value() == 1 and self.__btn_pt[0] != None:
                delta = utime.ticks_diff(utime.ticks_ms(), self.__btn_pt[0])
                self.__btn_pt[0] = None
                if delta > BTN_MIN_PRESS_TIME and  delta < BTN_MAX_SHORT_PRESS_TIME and self.__btnESC_ShortPress != None:
                    self.__btnESC_ShortPress()                   
        elif Pin == self.__btnMinus:
            if self.__btnMinus.value() == 0 and self.__btn_pt[1] == None:
                self.__btn_pt[1] = utime.ticks_ms()
            elif self.__btnMinus.value() == 1 and self.__btn_pt[1] != None:
                delta = utime.ticks_diff(utime.ticks_ms(), self.__btn_pt[1])
                self.__btn_pt[1] = None
                if delta > BTN_MIN_PRESS_TIME and  delta < BTN_MAX_SHORT_PRESS_TIME:
                    self.__btnMinus_LocalShortPress()
                    if self.__btnMinus_ShortPress != None:
                        self.__btnMinus_ShortPress()
        elif Pin == self.__btnENT:
            if self.__btnENT.value() == 0 and self.__btn_pt[2] == None:
                self.__btn_pt[2] = utime.ticks_ms()
            elif self.__btnENT.value() == 1 and self.__btn_pt[2] != None:
                delta = utime.ticks_diff(utime.ticks_ms(), self.__btn_pt[2])
                self.__btn_pt[2] = None
                if delta > BTN_MIN_PRESS_TIME and  delta < BTN_MAX_SHORT_PRESS_TIME and self.__btnENT_ShortPress != None:
                    self.__btnENT_ShortPress()
        elif Pin == self.__btnPlus:
            if self.__btnPlus.value() == 0 and self.__btn_pt[3] == None:
                self.__btn_pt[3] = utime.ticks_ms()
            elif self.__btnPlus.value() == 1 and self.__btn_pt[3] != None:
                delta = utime.ticks_diff(utime.ticks_ms(), self.__btn_pt[3])
                self.__btn_pt[3] = None
                if delta > BTN_MIN_PRESS_TIME and  delta < BTN_MAX_SHORT_PRESS_TIME:
                    self.__btnPlus_LocalShortPress()
                    if self.__btnPlus_ShortPress != None:
                        self.__btnPlus_ShortPress()
    
    # Local buttons press function
    def __btnMinus_LocalShortPress(self):
        if SCR_STATUS_START <= self.__BaseScreen <= SCR_STATUS_END and self.__BaseScreen > SCR_STATUS_START:
            self.__ScreenRequest = self.__BaseScreen - 1
    
    def __btnPlus_LocalShortPress(self):
         if SCR_STATUS_START <= self.__BaseScreen <= SCR_STATUS_END and self.__BaseScreen < SCR_STATUS_END:
            self.__ScreenRequest = self.__BaseScreen + 1
    
    # Buttons press callback functions
    def btnESC_ShortPress(self, callback):
        self.__btnESC_ShortPress = callback
        
    def btnESC_LongPress(self, callback):
        self.__btnESC_LongPress = callback
    
    def btnMinus_ShortPress(self, callback): 
        self.__btnMinus_ShortPress = callback
    
    def btnMinus_LongPress(self, callback):
        self.__btnMinus_LongPress = callback
    
    def btnENT_ShortPress(self, callback):
        self.__btnENT_ShortPress = callback
    
    def btnENT_LongPress(self, callback):
        self.__btnENT_LongPress = callback
        
    def btnPlus_ShortPress(self, callback):
        self.__btnPlus_ShortPress = callback
        
    def btnPlus_LongPress(self, callback):
        self.__btnPlus_LongPress = callback
    
    def __init__(self):
        print(" -> Switching power ON ...               ", end='')
        self.__PwrON.value(1)
        print('done')
        print(" -> Read saved parameters ...            ", end='')
        self.SavedParameters = param()
        print('done')
        print(" -> NeoPixel LED initialization ...      ", end='')
        self.NeoLEDs = neopixel.NeoPixel(self.__NeoLED, 2)
        self.NeoLEDs.write()
        print('done')
        print(" -> Buttons initialization ...           ", end='')
        self.Periodic = uasyncio.create_task(self.PeriodicAsync())
        self.__btnESC.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler = self.btn_IRQHandler)
        self.__btnMinus.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler = self.btn_IRQHandler)
        self.__btnENT.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler = self.btn_IRQHandler)
        self.__btnPlus.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler = self.btn_IRQHandler)
        print('done')
        print(" -> System I2C initialization ...        ", end = '')
        self.SysI2C = I2C(1, scl=self.__I2C1_SCL, sda=self.__I2C1_SDA, freq=400_000)
        print('done')
        print("      - {}".format(self.SysI2C))
        print("      - I2C scanning ...                 ",end = '')
        int_i2c_dev = self.SysI2C.scan()
        print("done")
        if 0x3C in int_i2c_dev:
            print("        - SSD1306 found on address 3Ch")
            print("        - initializing display ...       ",end = "")
            self.OLED = SSD1306_I2C(pix_res_x, pix_res_y, self.SysI2C)      # oled controller
            self.OLED.fill(0)
            self.OLED.contrast(5)
            #with open('/Images/BTECHi.pbm', 'rb') as f:
            with open('/Images/BTECHi.pbm', 'rb') as f:
                f.readline() # Magic number
                f.readline() # Creator comment
                f.readline() # Dimensions
                data = bytearray(f.read())
                fbuf = framebuf.FrameBuffer(data, 128, 55, framebuf.MONO_HLSB)
            self.OLED.blit(fbuf, 0, 9)
            rect(self.OLED, 0, 0, 127, 16, True)
            Font.PrintString(self.OLED, 'Car control', 25, 4, 0, 0)
            #self.OLED.rect(0,57, 124, 7, 1)
            rect(self.OLED, 0, 57, 128, 7)
            self.OLED.show()
            print("done")

        
        self.Time = RTC()
        
        print(" -> Web server initialization ...        ", end = '')
        self.__myWebServer = WebServer(self.SavedParameters, self.StartConsumeEl)
        print("                                         done")
        if self.__myWebServer.wlan.status() != 3:
            print('       - network connection failed')
        else:
            print('       - connected')
            print('       - SSID: ', self.__myWebServer.ssid)
            status = self.__myWebServer.wlan.ifconfig()
            print( '       - ip = ' + status[0] )
        
        
    
    def deinit(self):
        

        print(" -> Board deinitialization ...           ", end='')
        self.Periodic.cancel() 
        for i in range(self.NeoLEDs.n):
            self.NeoLEDs[i] = (0, 0, 0)
        self.NeoLEDs.write()
        if self.OLED != None:
            self.OLED.fill(0)
            self.OLED.show()
        print('done')
    
    ####################################################################################################
    # PROPERTIES                                                                                       #
    ####################################################################################################
    @property
    def BaseScreen(self):
        return self.__BaseScreen
    
    @BaseScreen.setter
    def BaseScreen(self, ScreenNumber):
        if self.__BaseScreen != ScreenNumber:
            self.__BaseScreen = ScreenNumber
    
    def WiFi_STA(self, STA):
        self.__WiFiSTA = STA
    
    def WiFi_AP(self, AP):
        self.__WiFiAP = AP
    
