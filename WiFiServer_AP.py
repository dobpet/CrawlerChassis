import network
import socket
import time
import uasyncio
import io


class WebServer:
    PasswordChange = 'xxxx'
    
    wlan = None
    ssid = None
    password = None
    
    ap = None
    ssid_ap = None
    password_ap = None
    IP_AP = None
    
    
    status = None
    addr = None
    s = None
    
    __com = None
    __com2 = None
    __recon = None
    
    blick = False
    #<meta http-equiv="refresh" content="15" name="viewport" content="width=device-width, initial-scale=1" charset="UTF-8">
    __html = """<!DOCTYPE html>
    <html>
        <head>
            <title>Car control</title>
            <style>
                h1 {text-align: center;}
                h2 {text-align: center;}
                p {text-align: center;}
            </style>
        </head>
        <meta name="viewport" content="width=device-width, initial-scale=1" charset="UTF-8">
        <body style="background-color:black;color:yellow;" text-align: center;>
            <hr>
            <h1 style="color:DodgerBlue">Car - information</h1>
            <br>
            <hr>
            <h1 style="color:DodgerBlue">WiFi settings:</h1>
            <center>
                <form>
                    Password for write settings: <input type="text" name="password" value="****">
                    <br>
                    <!--SettingWiFi-->
                    <br>
                    <input type="submit" value="Save settings to controler">
                </form>
            </center>
            <hr>
        </body>
    </html>
    """

    __max_wait = 10
    
    def __init__(self, SavedParameters, StartConsumeEl):
        self.SavedParameters = SavedParameters
        self.StartConsumeEl = StartConsumeEl
        
        print("in process")
        
        self.AP_Activate()
                
        for Network in self.SavedParameters.dictionary['Network']:
            self.ssid = Network['SSID']
            self.password = Network['pass']
            
            self.wlan = network.WLAN(network.STA_IF)
            self.wlan.active(True)
            self.wlan.config(pm = 0xa11140) # Disable power-save mode
            print ("        - connection to SSID: ", self.ssid)
            self.wlan.connect(self.ssid, self.password)
            
            while self.__max_wait > 0:
                if self.wlan.status() < 0 or self.wlan.status() >= 3:
                    break
                self.__max_wait -= 1
    #             print('       - waiting for connection...')
                time.sleep(1)
            

            if self.wlan.status() == 3:
#                 self.__com = uasyncio.create_task(uasyncio.start_server(self.Communication, "0.0.0.0", 80))
#                 self.__recon = uasyncio.create_task(self.Reconnect())
                break
            
            self.ssid = 'none'
        self.__com = uasyncio.create_task(uasyncio.start_server(self.Communication, "0.0.0.0", 80))
        self.__com2 = uasyncio.create_task(uasyncio.start_server(self.Communication2, "0.0.0.0", 502))
        self.__recon = uasyncio.create_task(self.Reconnect())

    def AP_Activate(self):
        self.ssid_ap = self.SavedParameters.dictionary['AP_SSID']
        self.password_ap = self.SavedParameters.dictionary['AP_Pass']
        
        ap = network.WLAN(network.AP_IF)
        ap.config(essid = self.ssid_ap, password = self.password_ap)
        ap.active(True)
        
        while ap.active() == False:
          pass
        
        print('        - AP connecting prepared: ')
        print(ap.ifconfig())
        self.IP_AP = ap.ifconfig()[0]
        print(self.IP_AP)

    async def Reconnect(self):
        while True:
            await uasyncio.sleep(60)
            
            if self.wlan.status() != 3:
                self.wlan.connect(self.ssid, self.password)
    
    async def Communication2(self, reader, writer):
        print('Communication2')
        DataS = await reader.read(16)
        DataS = DataS.decode('utf-8')
        print('WiFi Data received: ' + DataS)
        
        ParsData = DataS.split(":")
                    
#         if ParsData[0] == 'CM1':
#             CheckCommTime = utime.ticks_ms()
            
#             MotorLeft.SetSpeedProc(int(ParsData[1]))
#             MotorRight.SetSpeedProc(int(ParsData[2]))
#             Servo1.SetPosition(int(ParsData[3]))
#             Servo2.SetPosition(int(ParsData[4]))
#             Servo3.SetPosition(int(ParsData[5]))
#             Servo4.SetPosition(int(ParsData[6]))
   

   
    async def Communication(self, reader, writer):
        self.blick = True
        request_line = await reader.readline()
        print("Web client request:", request_line)

        while await reader.readline() != b"\r\n":
            pass

        request = str(request_line)
#decode ----------------------------------------------------------
        EndPos = request.find(' HTTP/1.1')
        
        Password = 'NotEntered'
        
        PassPos = request.find('password=')
        if PassPos >=0: #read password
            passEnd = request.find('&', PassPos)
            if passEnd >= 0:
                Password = request[PassPos+9: passEnd]   
                    
        if (request.find('?') >= 0) and (Password == self.PasswordChange):
            print('Password OK for change parameters.')
            startS = request.find('?') + 1
            stopS = 0
            EndString = False
            checkEnable = '0'
            
            while ((startS < EndPos) and not EndString):
                stopS = request.find('&', startS)
                if  stopS < 0:
                    stopS = request.find(' ', startS)
                    EndString = True
                resultSave = request[startS:stopS]
                try:
                    pos = resultSave.find('=')
                    tag = resultSave[:pos-1]
                    tagGroup = None
    #                 print(resultSave[:pos-1])
    #                 print(resultSave[pos-1:pos])
    #                 print(resultSave[pos+1:])

                    if (tag == "SSID") or (tag == "pass"):
                        tagGroup = "Network"
                    
                        
                    if tagGroup:
                        if (tagGroup == "Network"):
                            self.SavedParameters.dictionary[tagGroup][int(resultSave[pos-1:pos])-1][resultSave[:pos-1]] = resultSave[pos+1:] #MyClass.dictionary['Network'][0]['SSID']

                    
                except:
                    print('parameter dont exist: ', resultSave)
                startS = stopS + 1
                
            self.SavedParameters.SaveSettings()
        
#end decode ------------------------------------------------------        
        
#         led_on = request.find('/light/on')
#         led_off = request.find('/light/off')
#         print( 'led on = ' + str(led_on))
#         print( 'led off = ' + str(led_off))
# 
#         stateis = ""
#         if led_on == 6:
#             print("led on")
#             led.value(1)
#             stateis = "LED is ON"
#      
#         if led_off == 6:
#             print("led off")
#             led.value(0)
#             stateis = "LED is OFF"

#         response = html % stateis
        writer.write('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        
        #writer.write(self.__html)
        
        buf = io.StringIO(self.__html)
        while True:
            
            t = buf.readline()
            if t != '':
                t = t.rstrip('\n')                                           
                
                if t.find('<!--SettingWiFi-->') > 0:
                    t = '\n'
                    for x in range(2):
                        t = t + '<table>'
                        t = t + '  <tr>'
                        t = t + '    <td>SSID:</td>'
                        t = t + '    <td><input type="text" name="SSID' + str(x + 1) + '" value="' + str(self.SavedParameters.dictionary['Network'][x]['SSID']) + '"></td>'
                        t = t + '    <td> password:</td>'
                        t = t + '    <td><input type="password" name="pass' + str(x + 1) + '" value="' + str(self.SavedParameters.dictionary['Network'][x]['pass']) + '"></td>'
                        t = t + '  </tr>'
                        t = t + '</table>'
                        
                    
                writer.write(t)
            else:
                break
            

        await writer.drain()
        await writer.wait_closed()
        print("Client disconnected")
        self.blick = False
        
# async def main():        
#     myClass = WebServer()
#     while True:
#             print("heartbeat")
#             await uasyncio.sleep(5)
# 
# uasyncio.run(main())
