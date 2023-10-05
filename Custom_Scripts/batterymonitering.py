import smbus
import serial
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import threading

fromaddr = "cstacftcsolarchennai@gmail.com"
toaddr = "sselvamanikandan@ftcsolar.com"
mcu = serial.Serial()
mcu.port = "/dev/ttyUSB2"  # MCU connected to USB2
mcu.baudrate = 115200  # For MCU
bus = smbus.SMBus(3)
LTC4015 = 0x68  # LTC4015 connected to i2c bus no 3. And address is on hardware refer schematics
# For below Adress refer data sheet 
VBAT = 0x3A
IBAT = 0x3D
VIN = 0x3B
IIN = 0x3E
VSYS = 0x3C
DIE_TEMP = 0x3F
STATUS = 0x39
CON_BIT = 0x14
QCOUNT = 0x13
QCOUNT_PRE_FACTOR = 0x12
CHARGER_STATE = 0x34
IIN_LIMIT_SETTING = 0x15

# Global Decleartions 
RSNSI = 4  # 4 miliohm
RSNSB = 10  # 10 miliohm
CELL = 7  # Battery configuration
# Calculated values 
QCount_Prescalr = 27.47  # refer the calculation sheet


def System_Status():
    TS = str(int(time.time()))
    try:
        CPU_Temp = open("/sys/devices/virtual/thermal/thermal_zone0/temp", "r")
        CPU_Temp = int(CPU_Temp.read()) / 1000
    except:
        CPU_Temp = "-NA-"
    B_Temp = open("/sys/class/hwmon/hwmon0/temp1_input", "r")
    B_Temp = int(B_Temp.read()) / 1000
    file = open('system.txt', 'a')
    file.write('\n')
    file.write(str(int(time.time())))
    file.write('\t')
    file.write("System")
    file.write('\t')
    file.write(str(CPU_Temp))
    file.write('\t')
    file.write(str(B_Temp))


def Batt_Charger_Operation_Status():
    Con_data = bus.read_i2c_block_data(LTC4015, CON_BIT, 2)
    Con_data = Con_data[1] << 8 | Con_data[0]
    if (Con_data & 1 << 8):
        print("Battery Charger operation suspended")
        result = 0
    else:
        result = 1
        print("Battery charger in operation ")
    return result

def Current_Write_reg(data):
    Con_data  = data   # 19                       # Set the 8th bit to 0 to enable battery charging
    data1 =  (Con_data >> 8) & 0xFF     # Split 16bit data to 2 8bit data data1 is MSB, data0 is LSB
    data0 =  Con_data & 0xFF
    data = [data0, data1]
    bus.write_i2c_block_data(LTC4015, IIN_LIMIT_SETTING, data )

def batt_charger_operation_disable():
    Con_data = bus.read_i2c_block_data(LTC4015, CON_BIT, 2)
    Con_data = Con_data[1] << 8 | Con_data[0]  # merge 2 8 bit data to 16bit data
    if (Con_data & 0 << 8):
        Con_data = Con_data & 1 << 8  # Set the 8th bit to 1 to disable battery charging
        data1 = (Con_data >> 8) & 0xFF  # Split 16bit data to 2 8bit data data1 is MSB, data0 is LSB
        data0 = Con_data & 0xFF
        data = [data0, data1]
        bus.write_i2c_block_data(LTC4015, CON_BIT, data)
        Con_data = bus.read_i2c_block_data(LTC4015, CON_BIT, 2)
        Con_data = Con_data[1] << 8 | Con_data[0]
        if (Con_data & 1 << 8):
            print("Battery charger operation suspended")
            result = 1
        else:
            print("Failed to suspend the battery charger operation")
            print("After fail of bit 8 Configuration bits in Hex :", hex(Con_data))
            result = 2  # if failed on Enable

    else:
        print("Battery charger operation suspended ")
        result = 3  # if already in operation
    return result

def Batt_Charger_Operation_Enable():
    Con_data = bus.read_i2c_block_data(LTC4015, CON_BIT, 2)
    Con_data = Con_data[1] << 8 | Con_data[0]  # merge 2 8 bit data to 16bit data
    if (Con_data & 1 << 8):
        Con_data = Con_data & 0 << 8  # Set the 8th bit to 0 to enable battery charging
        data1 = (Con_data >> 8) & 0xFF  # Split 16bit data to 2 8bit data data1 is MSB, data0 is LSB
        data0 = Con_data & 0xFF
        data = [data0, data1]
        bus.write_i2c_block_data(LTC4015, CON_BIT, data)
        Con_data = bus.read_i2c_block_data(LTC4015, CON_BIT, 2)
        Con_data = Con_data[1] << 8 | Con_data[0]
        if (Con_data & 0 << 8):
            print("Battery charger set to charge")
            result = 1
        else:
            print("Failed to Enable the battery charger ")
            print("After fail of bit 8 Configuration bits in Hex :", hex(Con_data))
            result = 2  # if failed on Enable
    else:
        print("Battery charger in operation ")
        result = 3  # if alreadu in operation
    return result


def Mesurement_System_Status():
    Con_data = bus.read_i2c_block_data(LTC4015, CON_BIT, 2)
    Con_data = Con_data[1] << 8 | Con_data[0]
    if (Con_data & 1 << 4):
        print("Measurement System ON")
        result = 1
    else:
        print("Measurement System OFF ")
        result = 0
    return result


def Mesurement_System_Enable():
    Con_data = bus.read_i2c_block_data(LTC4015, CON_BIT, 2)
    Con_data = Con_data[1] << 8 | Con_data[0]
    if (Con_data & 1 << 4):
        print("Measurement System ON")
        result = 3
    else:
        print("Measurement System OFF  so ON now ")
        Con_data |= 1 << 4
        data1 = (Con_data >> 8) & 0xFF
        data0 = Con_data & 0xFF
        data = [data0, data1]
        bus.write_i2c_block_data(LTC4015, CON_BIT, data)
        Con_data = bus.read_i2c_block_data(LTC4015, CON_BIT, 2)
        Con_data = Con_data[1] << 8 | Con_data[0]  # merge 2 8 bit data to 16bit data
        if (Con_data & 1 << 4):
            print("Measurement System ON")
            result = 1
        else:
            print("Failed to ON the measurementsystem")
            print("After fail of bit 4 Configuration bits in Hex :", hex(Con_data))
            result = 2
    return result


def Columb_Counter_Status():
    Con_data = bus.read_i2c_block_data(LTC4015, CON_BIT, 2)
    Con_data = Con_data[1] << 8 | Con_data[0]
    if (Con_data & 1 << 2):
        print("Columb Counter ON")
        result = 1
    else:
        print("Columb Counter OFF")
        result = 0
    return result


def Columb_Counter_Enable():
    Con_data = bus.read_i2c_block_data(LTC4015, CON_BIT, 2)
    Con_data = Con_data[1] << 8 | Con_data[0]
    if (Con_data & 1 << 2):
        print("Columb Counter ON")
        result = 3
    else:
        print("Columb Counter OFF So ON Now")
        Con_data |= 1 << 2
        data1 = (Con_data >> 8) & 0xFF
        data0 = Con_data & 0xFF
        data = [data0, data1]
        bus.write_i2c_block_data(LTC4015, CON_BIT, data)
        Con_data = bus.read_i2c_block_data(LTC4015, CON_BIT, 2)
        Con_data = Con_data[1] << 8 | Con_data[0]  # merge 2 8 bit data to 16bit data
        if (Con_data & 1 << 2):
            print("Columb Counter ON")
            result = 1
        else:
            print("Failed to ON the Columb counter")
            print("After fail of bit 2 Configuration bits in Hex :", hex(Con_data))
            result = 2
    return result


def Read_SOC_Configuration():
    Qcount_Prescalor_factor = bus.read_i2c_block_data(LTC4015, QCOUNT_PRE_FACTOR, 2)
    Qcount_Prescalor_factor = Qcount_Prescalor_factor[1] << 8 | Qcount_Prescalor_factor[0]
    print("Qcount_Prescalor_factor :", Qcount_Prescalor_factor)
    Qcount = bus.read_i2c_block_data(LTC4015, QCOUNT, 2)
    Qcount = Qcount[1] << 8 | Qcount[0]
    print("Qcount :", Qcount)


def SOC_Configuration():
    status = Columb_Counter_Status()
    if status == 1:
        data = 512
        data1 = (data >> 8) & 0xFF
        data0 = data & 0xFF
        data = [data0, data1]
        bus.write_i2c_block_data(LTC4015, QCOUNT_PRE_FACTOR, data)
        Qcount_Prescalor_factor = bus.read_i2c_block_data(LTC4015, QCOUNT_PRE_FACTOR, 2)
        Qcount_Prescalor_factor = Qcount_Prescalor_factor[1] << 8 | Qcount_Prescalor_factor[0]
        if Qcount_Prescalor_factor == 27:
            # print("Qcount_Prescalor_Factor write success")
            result = 1
        else:
            # print("Qcount_Prescalor_Factor write Fail")
            result = 0
    else:
        result = status
    return result


def SOC_Calculate():
    Qcount = bus.read_i2c_block_data(LTC4015, QCOUNT, 2)
    Qcount = Qcount[1] << 8 | Qcount[0]
    value = int(Qcount)
    SOC = ((value - 32768) / 3459) * 100
    return round(SOC, 2)


def Batt_Connection_Status():
    State = bus.read_i2c_block_data(LTC4015, CHARGER_STATE, 2)
    State = State[1] << 8 | State[0]
    if (State & 1 << 1):
        print("Battery Not Connected")
        status = 0
    else:
        status = 1
    return status


def twos_comp(val, bit):
    if val >= 2 ** bit:
        print("Data out of range")
    else:
        return val - int((val << 1) & 2 ** bit)


Columb_Counter_Status()
Columb_Counter_Enable()
SOC_Configuration()
Batt_Charger_Operation_Status()
count = 0
Current_Write_reg(2)
while True:
    System = Mesurement_System_Status()
    if System == 1:
        Input_Voltage = bus.read_i2c_block_data(LTC4015, VIN, 2)
        Input_Voltage = Input_Voltage[1] << 8 | Input_Voltage[0]
        Input_Voltage = Input_Voltage * 0.001648
        print("Measured Input Voltage is :", Input_Voltage, "V")
        Input_Current = bus.read_i2c_block_data(LTC4015, IIN, 2)
        Input_Current = Input_Current[1] << 8 | Input_Current[0]
        Input_Current = ((Input_Current * 1.46487) / RSNSI) / 1000
        print("Measured Input Current is :", Input_Current*1000, "A")
        VSYS_Voltage = bus.read_i2c_block_data(LTC4015, VSYS, 2)
        VSYS_Voltage = VSYS_Voltage[1] << 8 | VSYS_Voltage[0]
        VSYS_Voltage = VSYS_Voltage * 0.001648
        print("Measured System Voltage is :", VSYS_Voltage, "V")
        Die_Temp = bus.read_i2c_block_data(LTC4015, DIE_TEMP, 2)
        Die_Temp = Die_Temp[1] << 8 | Die_Temp[0]
        Die_Temp = (Die_Temp - 12010) / 45.6
        print("Measured Die Temperature is :", Die_Temp, "degC")
    else:
        Mesurement_System_Enable()
        Input_Voltage = "-NA-"
        Input_Current = "-NA-"
        VSYS_Voltage = "-NA-"
        Die_Temp = "-NA-"
    System = Batt_Connection_Status()
    if System == 1:
        Batter_Voltage = bus.read_i2c_block_data(LTC4015, VBAT, 2)
        Batter_Voltage = Batter_Voltage[1] << 8 | Batter_Voltage[0]
        Batter_Voltage = Batter_Voltage * 0.000192264 * CELL
        print("Measured Battery voltage is :", Batter_Voltage, "V")
        Batt_Current = bus.read_i2c_block_data(LTC4015, IBAT, 2)
        Batt_Current = Batt_Current[1] << 8 | Batt_Current[0]
        if (Batt_Current & 1 << 15):
            Batt_Current = twos_comp(Batt_Current, 16)  # 16 -> represent 16 bit value
        Batt_Current = ((Batt_Current * 1.46487) / RSNSB) / 1000
        print("Measured BatteryCurrent is :", Batt_Current*1000, "A")
    else:
        Batter_Voltage = "-NA-"
        print("Measured Battery voltage is :", Batter_Voltage, "V")
        Batt_Current = "-NA-"
        print("Measured BatteryCurrent is :", Batt_Current*1000, "A")
    Battery_Charge = SOC_Calculate()
    print("Calculated Battery Charge  is: ", Battery_Charge, "%")
    Read_SOC_Configuration()
    try:
        CPU_Temp = open("/sys/devices/virtual/thermal/thermal_zone0/temp", "r")
        CPU_Temp = int(CPU_Temp.read()) / 1000
    except:
        CPU_Temp = "-NA-"

    B_Temp = open("/sys/class/hwmon/hwmon0/temp1_input", "r")
    B_Temp = int(B_Temp.read()) / 1000
    print("CPU Temp:",CPU_Temp)
    print("Board Temp:",B_Temp)
    if count == 0:
        if B_Temp < -10:
            Current_Write_reg(10)
            count = count+1
    time.sleep(1)
