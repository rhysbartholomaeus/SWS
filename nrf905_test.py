import spidev
from time import sleep
import RPi.GPIO as GPIO



class Radio:
    CSN  = 26 # SPI ON/OFF
    DR   = 12 # DATA READY
    PWR  = 11 # NRF905 HIGH/LOW PWR
    CE   = 13 # TRX_CE
    TxEN = 15 # TxEN (TX OR RX MODE)
    CD   = 16 # CARRIER DETECT                                                                                                           
    AM   = 7  # ADDRESS MATCH
    spi = spidev.SpiDev() # SPI OBJECT
    
    data = bytearray(32)
    charArray = "\0"*32
    
    def __init__(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(self.CSN,GPIO.OUT)
        GPIO.output(self.CSN,GPIO.HIGH)
        GPIO.setup(self.DR,GPIO.IN)
        GPIO.setup(self.AM,GPIO.IN)
        GPIO.setup(self.CD,GPIO.IN)
        GPIO.setup(self.PWR,GPIO.OUT)
        GPIO.output(self.PWR,GPIO.HIGH) # TURN RF ON
        GPIO.setup(self.CE,GPIO.OUT)
        GPIO.output(self.CE,GPIO.LOW)
        GPIO.setup(self.TxEN,GPIO.OUT)
        GPIO.output(self.TxEN, GPIO.LOW) # SET TO RX MODE
        sleep(0.1)        

    def openSpi(self):
        self.spi.open(0,0)
        self.spi.max_speed_hz=106000        
    
    def lightOn(self):
        
        GPIO.setup(37,GPIO.OUT)
        while(True):
            sleep(0.5)
            GPIO.output(37,GPIO.HIGH)
            sleep(0.5)
            GPIO.output(37,GPIO.LOW)

    def gpioLow(self):
        GPIO.output(self.CSN,GPIO.LOW)
        GPIO.output(self.PWR,GPIO.LOW)

    def writeConfig(self):
        self.openSpi()
        GPIO.output(self.CSN,GPIO.LOW) # LET NRF KNOW WE ARE WRITING TO IT
        self.spi.xfer([0x00])[0] # WRITE TO CONFIG REG
        self.spi.xfer([0x0A])[0] # CHANNEL NUMBER
        self.spi.xfer([0x0C])[0]# OUTPUT PWR, RESEND DISABLE, NORMAL RX CURRENT
        self.spi.xfer([0x44]) # 4 Byte ADDRS
        self.spi.xfer([0x20]) # RX SET TO 32 BYTE ADDR
        self.spi.xfer([0x20]) # TX SET TO 32 BYTE ADDR
        self.spi.xfer([0xCC]) # RX ADDR
        self.spi.xfer([0xCC]) # RX ADDR
        self.spi.xfer([0xCC]) # RX ADDR
        self.spi.xfer([0xCC]) # RX ADDR
        self.spi.xfer([0x58]) # CRC EN, 8 bit CRC, EXT CLK OFF, 16MHZ
        GPIO.output(self.CSN,GPIO.HIGH) # NRF CAN RESUME LISTENING
        self.spi.close()

    def readConfig(self):
        self.openSpi()
        GPIO.output(self.CSN,GPIO.LOW)
        self.spi.xfer([0x10])
        data = ""
        sysInfo = []
        #sleep(0.1)
        for i in range(10):
            sysInfo+= self.spi.xfer([0x00])
            data = str(sysInfo)
        #data = self.spi.readbytes(10)      
        GPIO.output(self.CSN,GPIO.HIGH)
        #GPIO.output(self.CE,GPIO.LOW)
        #output =  ''.join(["0x%02X " % x for x in sysInfo]).strip()
        #print("Config values: " +output)

        #print("\nConfig values: "+data)
        """try:
            print("This is data: "+(data))
        except:
            print("No data")
    """
        self.spi.close()

        
    def listen(self):
        self.openSpi()
        GPIO.output(self.TxEN,GPIO.LOW)  # RX MODE
        GPIO.output(self.CE,GPIO.HIGH)   # RX SHOCKBURST
        sleep(0.1)                       # SLEEP WHILE NRF CONFIGURES RX SHOCKBURST
        #GPIO.setup(37,GPIO.OUT) # LIGHT
        #print("\nListening...\n")
        while(GPIO.input(self.DR)==GPIO.LOW):
            # Do something
            x = 0
            sleep(0.1)
        
        GPIO.output(self.CE,GPIO.LOW)   # LETS TURN OFF RX/TX
        GPIO.output(self.CSN,GPIO.LOW)  # PULL CSN LOW
        self.spi.xfer2([0x24])          # REQUEST RX DATA
        #data = []
        for i in range(32):
            self.data[i]= self.spi.xfer2([0x00])[0]
           
       # for item in self.data:
       #     print(item)
       # for value in data:
       #     if(value!='0' or value!=0):
       #         print((value))
        #print("\nDR went high\n")
        #GPIO.output(37,GPIO.HIGH)
        sleep(0.2)
        GPIO.output(self.CE,GPIO.HIGH)   # TURN RX BACK ON
        GPIO.output(self.CSN,GPIO.HIGH)  # STOP REQUESTING
        #GPIO.output(37,GPIO.LOW)
        self.spi.close()


    def reverseByteArr(self, array):
        output =  ''.join(["0x%02X " % x for x in array]).strip()
        print(output)
        returnArr = bytearray(32)
        count=0
        for byte in array:
             #self.charArray[count] = byte
             high = byte >> 4
             low  = byte & 0x0F
             byte = high|low
             #byte = byte >> 4
             
             #byte = ((byte & 0xF0) >> 4) | ((byte & 0x0F) << 4)
             #byte = ((byte & 0xCC) >> 2) | ((byte & 0x33) << 2)
             #byte = ((byte & 0xAA) >> 1) | ((byte & 0x55) << 1)
             returnArr[count]= byte
             count+=1
        return returnArr  

         
        
if __name__ == "__main__":
    print("Running")
    try:
       # print(dir(GPIO))
        radio = Radio()
        radio.writeConfig()
        sleep(0.5)
        radio.readConfig()
        #sleep(1)
       # while(True):
        radio.listen()
       # print("This is the default array: ")
       # for item in radio.data:
       #     print(item, end=' ')
       # print("\n")

        print("[Radio online]")
        print("[Got message. Value is:]")
        array = radio.data
        sleep(5)
        outStr = ""
        for item in array:
            outStr+=chr(item)
        print(outStr)
        #radio.lightOn()
    except KeyboardInterrupt:
        print("Quitting...")
        #GPIO.output(37,GPIO.LOW)
        radio.gpioLow()
        radio.spi.close()
