import serial
import time
from enum import Enum
from abc import abstractmethod
#from gpiozero import DigitalOutputDevice

# 433 band [430 - 440]


class RF_DataRate(Enum):
    RATE_2400 = 1
    RATE_4800 = 2
    RATE_9600 = 3
    RATE_19200 = 4


class UART_Rate(Enum):
    UART_1200 = 0
    UART_2400 = 1
    UART_4800 = 2
    UART_9600 = 3
    UART_19200 = 4
    UART_38400 = 5
    UART_57600 = 6


class ACP_Radio:
    port: serial.Serial

    def __init__(self, port: serial.Serial):
        if port is None:
            raise Exception()
        self.port = port

    @abstractmethod
    def enterConfigMode(self):
        pass

    @abstractmethod
    def exitConfigMode(self):
        pass

    def __parse_config(self, response: bytes) -> tuple[int, RF_DataRate, int, UART_Rate, bool]:
        # Parse response
        args = response.decode(errors="ignore").split(' ')
        if len(args) != 6:
            raise Exception(f'Invalid reply: {args}')
        #print("'"+str(args[0])+"'")
        #if str(args[0]) != str("PARA"):
            #raise Exception(f'Invalid ARG0: {args[0]}')

        # Frequency in kHz
        freq = int(args[1])

        # Data rate
        drate = int(args[2])
        if drate == RF_DataRate.RATE_2400.value:
            drate = RF_DataRate.RATE_2400
        elif drate == RF_DataRate.RATE_4800.value:
            drate = RF_DataRate.RATE_4800
        elif drate == RF_DataRate.RATE_9600.value:
            drate = RF_DataRate.RATE_9600
        elif drate == RF_DataRate.RATE_19200.value:
            drate = RF_DataRate.RATE_19200
        else:
            raise Exception(f'Invalid DATA_RATE: {args[2]}')

        # Output power
        power = int(args[3])

        # UART baudrate
        brate = int(args[4])
        if brate == UART_Rate.UART_1200.value:
            brate = UART_Rate.UART_1200
        elif brate == UART_Rate.UART_2400.value:
            brate = UART_Rate.UART_2400
        elif brate == UART_Rate.UART_4800.value:
            brate = UART_Rate.UART_4800
        elif brate == UART_Rate.UART_9600.value:
            brate = UART_Rate.UART_9600
        elif brate == UART_Rate.UART_19200.value:
            brate = UART_Rate.UART_19200
        elif brate == UART_Rate.UART_38400.value:
            brate = UART_Rate.UART_38400
        elif brate == UART_Rate.UART_57600.value:
            brate = UART_Rate.UART_57600
        else:
            raise Exception(f'Invalid BUAD_RATE: {args[4]}')

        # Parity
        parity = True if int(args[5][0:1]) else False

        return (freq, drate, power, brate, parity)

    def configureRadio(self, frequency: int = 433000, dataRate: RF_DataRate = RF_DataRate.RATE_9600, outputPower: int = 9, serialRate: UART_Rate = UART_Rate.UART_9600, parity: bool = False) -> bool:
        # Check parameters
        if (frequency < 430000) or (frequency > 440000):
            return False
        if outputPower < 0 or outputPower > 9:
            return False

        # Build command
        cmd = f'WR {frequency} {dataRate.value} {outputPower} {serialRate.value} {1 if parity else 0}\r\n'

        # Send command
        self.port.write(cmd.encode())

        # Get reply (same as RD command)
        rsp = self.port.readline()
        self.__parse_config(rsp)

        return True

    def getConfiguration(self) -> tuple[int, RF_DataRate, int, UART_Rate, bool]:
        # Send command
        cmd = 'RD\r\n'
        self.port.write(cmd.encode())

        # Wait response
        rsp = self.port.readline()
        if rsp is None:
            raise Exception('No reply')

        return self.__parse_config(rsp)


# class Rasp_Radio(ACP_Radio):
#     def __init__(self, port, gpioSET: DigitalOutputDevice):
#         super().__init__(port)
#         if gpioSET is None:
#             raise Exception()
#         self.gpioSET = gpioSET
#         gpioSET.off()

#     def enterConfigMode(self):
#         self.gpioSET.on()
#         time.sleep(0.1)

#     def exitConfigMode(self):
#         self.gpioSET.off()
#         time.sleep(0.5)


class USB_Radio(ACP_Radio):
    def __init__(self, port):
        super().__init__(port)
        self.port.rts = False

    def enterConfigMode(self):
        self.port.rts = True
        time.sleep(0.1)

    def exitConfigMode(self):
        self.port.rts = False
        time.sleep(0.5)
