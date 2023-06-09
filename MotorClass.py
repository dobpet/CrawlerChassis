"""
constructor:
    - instance = MotorClass(self, PinForward, PinBackward, Ramp):
methode for cyclic function:
    - instance.SpeedUpdate()
control of motor:
    - instance.SetSpeed(speed) //speed in range MinSpeed and MaxSpeed
    - instance.SetSpeedProc(proc) //speed in range -100 to 100 %
read actual speed:
    - speed = instance.GetActualSpeed()

example:

    PinForward = machine.PWM(machine.Pin(9))
    PinBackward = machine.PWM(machine.Pin(8))
    Motor = MotorClass.MotorClass(PinForward,PinBackward, 5000)

    speed = 60000
    Motor.SetSpeed(speed)

    while True:
        
        if (Motor.GetActualSpeed() >= speed):
            Motor.SetSpeed(-speed)
        elif (Motor.GetActualSpeed() <= -speed):
            Motor.SetSpeed(speed)
"""
from machine import Pin
import utime
import uasyncio

class MotorClass:

    # Global Variables
    __ActualSpeed = 0
    __ReqSpeed = 0
    __Ramp = 5000 #time from 0% to 100% of speed
    MinSpeed = 15000 #From 0 to this set point (duty)
    MaxSpeed = 60000 #Maximum of value for duty command
    
    __PinForward = None    #machine.PWM(machine.Pin(x))
    __PinBackward = None
    
    __LastInterTime = 0 # Last Time from intervention
    __RegP = 1000    # regulation parameter
    __RegT = 100    # ms regulation parameter
    
    def SetRamp(self, Ramp):
        self.__Ramp = Ramp
        temp = Ramp / self.__RegT
        self.__RegP = int((self.MaxSpeed - self.MinSpeed) / temp)
        print("Calculated regulator P: " + str(self.__RegP))
        
    def __init__(self, PinForward, PinBackward, Ramp):
        self.__PinForward = PinForward
        self.__PinForward.freq(1000)
        self.__PinBackward = PinBackward
        self.__PinBackward.freq(1000)
        self.SetRamp(Ramp)
        self.__com = uasyncio.create_task(self.SpeedUpdate())
    
    def __TimeAction(self):
        if (utime.ticks_ms() - self.__LastInterTime) > self.__RegT:
            self.__LastInterTime = utime.ticks_ms()
            return True
        else:
            return False
        
    def SetSpeed(self, Speed):
        if ((Speed < self.MaxSpeed) or (Speed > - self.MaxSpeed)):
            #print("DutySpeedSet: " + str(Speed))
            self.__ReqSpeed = Speed
    
    def SetSpeedProc(self, Proc):#in range -100 to 100%
        if ((Proc <= 100) and (Proc >= -100)):
            DutySpeed = (self.MaxSpeed / 100) * Proc
            self.SetSpeed(DutySpeed)   
        
    
    def GetActualSpeed(self):
        return(self.__ActualSpeed)
    
    def SpeedCalculate(self):
        if self.__TimeAction():
            """ linear calculation of speed"""
            if (((self.__ActualSpeed - self.__ReqSpeed) < self.__RegP) and (abs(self.__ActualSpeed - self.__ReqSpeed) >= self.__RegP )):                
                self.__ActualSpeed = self.__ActualSpeed + self.__RegP
            elif (((self.__ActualSpeed - self.__ReqSpeed) > self.__RegP) and (abs(self.__ActualSpeed - self.__ReqSpeed) >= self.__RegP )):
                self.__ActualSpeed = self.__ActualSpeed - self.__RegP
            else:
                self.__ActualSpeed = self.__ReqSpeed
            
            """ motor run from the minimum duty """
            if ((self.__ActualSpeed < self.MinSpeed) and (self.__ActualSpeed >= 0) and (self.__ReqSpeed > self.MinSpeed)):
                self.ActualSpeed = self.MinSpeed
            elif ((self.__ActualSpeed > -self.MinSpeed) and (self.__ActualSpeed <= 0) and (self.__ReqSpeed < - self.MinSpeed)):
                self.__ActualSpeed = - self.MinSpeed
            elif (self.__ActualSpeed < self.MinSpeed) and (self.__ActualSpeed > - self.MinSpeed):
                self.__ActualSpeed = 0

            """ set maximum speed for command """   
            if (self.__ActualSpeed > self.MaxSpeed):
                self.__ActualSpeed = self.MaxSpeed
            elif (self.__ActualSpeed < - self.MaxSpeed):
                self.__ActualSpeed = - self.MaxSpeed
            
            #print("SpeedCalculate: actual " + str(self.ActualSpeed) + " request " + str(self.ReqSpeed))
    
    def MoveForward30k(self):
        self.__PinForward.duty_u16(30000)
        self.__PinBackward.duty_u16(0)
    
    def MoveBackward30k(self):
        self.__PinForward.duty_u16(0)
        self.__PinBackward.duty_u16(30000)
       
    def MoveForward(self, Speed):
        self.__PinForward.duty_u16(int(abs(Speed)))
        self.__PinBackward.duty_u16(0)
    
    def MoveBackward(self, Speed):
        self.__PinForward.duty_u16(0)
        self.__PinBackward.duty_u16(int(abs(Speed)))
        
    def MoveStop(self):
        self.__PinForward.duty_u16(0)
        self.__PinBackward.duty_u16(0)
        
    async def SpeedUpdate(self):
        while True:
            self.SpeedCalculate()
            #print("DutySpeedSet: " + str(self.__ActualSpeed))
            if (self.__ActualSpeed > 0):
                self.MoveForward(self.__ActualSpeed)
            elif (self.__ActualSpeed < 0):
                self.MoveBackward(self.__ActualSpeed)
            else:
                self.MoveStop()
            
            await uasyncio.sleep_ms(100)

async def main():    
    PinForward = machine.PWM(machine.Pin(9))
    PinBackward = machine.PWM(machine.Pin(8))
    Motor = MotorClass.MotorClass(PinForward,PinBackward, 5000)

    speed = 60000
    Motor.SetSpeed(speed)

    while True:
        
        if (Motor.GetActualSpeed() >= speed):
            Motor.SetSpeed(-speed)
        elif (Motor.GetActualSpeed() <= -speed):
            Motor.SetSpeed(speed)
