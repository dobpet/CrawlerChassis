import Font
import gc
from machine import RTC

def rect(disp, X, Y, Width, Height, Fill=False):
    disp.rect(X, Y, Width, Height, 1, Fill)
    disp.pixel(X, Y, 0)
    disp.pixel(X + Width - 1, Y, 0)
    disp.pixel(X, Y + Height - 1, 0)
    disp.pixel(X + Width - 1, Y + Height - 1, 0)
    
def APIndicator(disp, X, Y, BlinkFlags, AP = None):
    disp.rect(X, Y, 17, 9, 0, False)
    #rect(disp, X, Y, 17, 9, False)
    if AP == None:
        Font.PrintString(disp, "--", X + 2, Y + 1, 1, 1)
    else:
        sts = AP.status()
        if sts == 0: # Link down
            #rect(disp, X, Y, 17, 9, False)
            Font.PrintString(disp, 'AP', X + 3, Y + 1, 1, 1)

def STAIndicator(disp, X, Y, BlinkFlags, STA = None):
    disp.rect(X, Y, 22, 9, 0, False)
    #rect(disp, X, Y, 22, 9, False)
    if STA == None:
        Font.PrintString(disp, "--", X + 4, Y + 1, 1, 1)
    else:
        sts = STA.status()
        if sts == 0: # Link down
            #rect(disp, X, Y, 17, 9, False)
            Font.PrintString(disp, 'STA', X + 2, Y + 1, 1, 1)

def DigitalIndicator(disp, X, Name, State, Selected):
    if Selected:
        disp.hline(X, 26, 5, 1)
        disp.hline(X+9, 26, 5, 1)
        disp.hline(X, 59, 5, 1)
        disp.hline(X+9, 59, 5, 1)
        disp.vline(X, 26, 5, 1)
        disp.vline(X+14, 26, 5, 1)
        disp.vline(X, 54, 5, 1)
        disp.vline(X+14, 54, 5, 1)
    rect(disp, X + 2, 28, 11, 30, State)
    if State:      
        Font.PrintStringV(disp, Name, X+4, 54, 1, 0)
    else:
        Font.PrintStringV(disp, Name, X+4, 54, 1, 1)

def PaintTitle(disp, BlinkFlags, Title = None, Subtitle = None, STA=None, AP=None):
    if Title != None and Subtitle != None:
        Font.PrintString(disp, Title, 0, 0, 0, 1)
        Font.PrintString(disp, Subtitle, 0, 8, 0, 1)
    else:
        dt = RTC().datetime()
        disp.rect(0, 0, 85, 15, 0, True)
        Font.PrintString(disp, '{:02d}'.format(dt[4]), 0, 0, 2, 1)
        if (BlinkFlags & 1) == 1:
            Font.PrintString(disp, ':', 23, 0, 2, 1)
        Font.PrintString(disp, '{:02d}'.format(dt[5]), 32, 0, 2, 1)    
        Font.PrintString(disp, '{0:02d}'.format(dt[6]), 59, 0, 1, 1)
    
    rect(disp, 86, 0, 41, 4)
    disp.rect(87, 1, 30 , 2, 0, True)
    mp = gc.mem_alloc() / (gc.mem_free() + gc.mem_alloc())
    disp.rect(87, 1, int(30 * mp), 2, 1, True)    
    
    APIndicator(disp, 86, 6, BlinkFlags, AP)
    STAIndicator(disp, 105, 6, BlinkFlags, STA)

def PageTitle(disp, Title):
    disp.hline(0, 18, 6, 1)
    disp.hline(0, 20, 6, 1)
    disp.hline(0, 22, 6, 1)
    x = Font.PrintString(disp, Title, 8, 17, 0, 1) + 1
    disp.hline(x, 18, 128 - x, 1)
    disp.hline(x, 20, 128 - x, 1)
    disp.hline(x, 22, 128 - x, 1)


def ScreenWiFi(disp, BlinkFlags, WiFi, Update):
    if not Update:
        PageTitle(disp, 'WiFi')
    disp.rect(0, 24, 128, 36, 0, True)
    if not WiFi:
        Font.PrintString(disp, 'COMMUNICATION', 28, 30, 1, 1)
        Font.PrintString(disp, 'INITIALIZING', 30, 42, 1, 1)
    else:
            text = WiFi.ssid#'network: ' 
            Font.PrintString(disp, text, 0, 30, 1, 1)
            
            if WiFi.wlan.status() == 3:
                text = 'connected'
            else:
                text = 'network failed'
            Font.PrintString(disp, text, 0, 40, 1, 1)    
                
            text = WiFi.wlan.ifconfig()[0]
            Font.PrintString(disp, text, 0, 50, 1, 1)
            
    return (None, None, True)

def ScreenWiFiAP(disp, BlinkFlags, WiFi, Update):
    if not Update:
        PageTitle(disp, 'WiFi AP')
    disp.rect(0, 24, 128, 36, 0, True)
    
    text = WiFi.ssid_ap
    Font.PrintString(disp, text, 0, 30, 1, 1)
    
    text = '****'
    Font.PrintString(disp, text, 0, 40, 1, 1)    
        
    text = WiFi.IP_AP
    Font.PrintString(disp, text, 0, 50, 1, 1)
            
    return (None, None, True)

        
def ScreenPowerStatus(disp, BlinkFlags, Update):
    if not Update:
        PageTitle(disp, 'POWER')
    return (None, None, True)

def ScreenInputStatus(disp, BlinkFlags, Update):
    if not Update:
        PageTitle(disp, 'DIGITAL INPUTS')
        DigitalIndicator(disp, (0 * 16), 'RST', False, False)
        DigitalIndicator(disp, (1 * 16), 'RDY', True, False)
        DigitalIndicator(disp, (2 * 16), '', False, False)
        DigitalIndicator(disp, (3 * 16), '', False, False)
        DigitalIndicator(disp, (4 * 16), '', False, False)
        DigitalIndicator(disp, (5 * 16), '', False, False)
        DigitalIndicator(disp, (6 * 16), '', False, False)
        DigitalIndicator(disp, (7 * 16), '', False, False)
    return (None, None, True)

def ScreenOutputStatus(disp, BlinkFlags, Connector6Pin, Value_5IOx, Update):
    if not Update:
        PageTitle(disp, 'DIGITAL OUTPUTS')
        DigitalIndicator(disp, (0 * 16), 'P14', Connector6Pin[0], False) #Pin P14
        DigitalIndicator(disp, (1 * 16), 'P13', Connector6Pin[1], False) #Pin P13
        DigitalIndicator(disp, (2 * 16), 'P12', Connector6Pin[2], False) #Pin P12
        DigitalIndicator(disp, (3 * 16), 'P05', Connector6Pin[3], False) #Pin Pin5
        DigitalIndicator(disp, (4 * 16), 'P01', Connector6Pin[4], False)
        DigitalIndicator(disp, (5 * 16), 'P00', Connector6Pin[5], False) #Pin Pin0
        DigitalIndicator(disp, (6 * 16), 'IO0', Value_5IOx[0], False)
        DigitalIndicator(disp, (7 * 16), 'IO1', Value_5IOx[1], False)        


    return (None, None, True)



