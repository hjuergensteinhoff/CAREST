'''
Heat_plate_commands_from_config_file 
by Heinz-Juergen Steinhoff, University Osnabrueck, Germany.
Version 7, April 2025
This code is to upload tailored data to an AHP-1200 heat/cold plate 
(teca, Thermo Electric Cooling America Corporation) for temperature ramps 
used in pain rating experiments according to the 
ESCAPE study (Annekatrin Steinhoff, University Bern, Switzerland).

Temperatures and timings for the temperature ramp are read from the config.dat file. 
(Default values for ESCAPE heat / cold experiments are given in brackets and in the comments).
Start_ramp initiates the process from the actual temperature, PV, aiming to reach 
the base_temperature, SV (35 C, 25 C), in ramp_up_time_bt (60 s). The base 
temperature is held constant for hold_time_bt (120 s / 60 s). The peak_temperature 
(47.0 C / 5.0 C) is nearly linearly reached within ramp_up_time_pt (156 s / 280 s). 
The peak_temperature is held constant for hold_time_pt (0 s / 60 s). Within a 
ramp_down_time_bt (300 s) the plate is reset to base_temperature SV. 

For checking the proper function of the plate the temperature ramp 
can be started and the actual temperature values (PV) are printed every 2 seconds.

Copyright (c) 2025 Heinz-Juergen Steinhoff and Annekatrin Steinhoff

Permission is hereby granted, free of charge, to any person obtaining a copy of this 
software and associated documentation files (the "Software"), to deal in the Software 
without restriction, including without limitation the rights to use, copy, modify, merge, 
publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons
to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR 
PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE 
FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, 
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

'''

import time
import serial
import serial.tools.list_ports
import struct
import sys
from dataclasses import dataclass

@dataclass
class ExperimentConfig:
    base_temperature: float
    peak_temperature: float
    ramp_up_time_bt: int
    hold_time_bt: int
    ramp_up_time_pt: int
    hold_time_pt: int
    ramp_down_time_bt: int
    serial_port_HP: str
    serial_port_scales: str

ComTalking = False

def load_config(file_path: str) -> ExperimentConfig:
    config_values = {}
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.split('#')[0].strip()

                try:
                    if '.' in value:
                        config_values[key] = float(value)
                    elif value.isdigit():
                        config_values[key] = int(value)
                    else:
                        config_values[key] = value  # string, e.g., COM3
                except ValueError:
                    raise ValueError(f"Invalid number for key '{key}': '{value}'")


    try:
        # Validate and assign values with bounds checking
        base_temp = config_values['base_temperature']
        peak_temp = config_values['peak_temperature']
        ramp_up_time_pt = config_values['ramp_up_time_pt'] 

        if not (10.0 <= base_temp <= 45.0):
            raise ValueError(f"base_temperature {base_temp} out of range (10.0 - 45.0)")
            sys.exit()
        if not (5.0 <= peak_temp <= 49.0):
            raise ValueError(f"peak_temperature {peak_temp} out of range (5.0 - 49.0)")
            sys.exit()
        if (peak_temp - base_temp) != 0:
           ramp_spC = ramp_up_time_pt/(abs(peak_temp - base_temp)) # peak temperature ramp up time in seconds per degree Celsius
           if not (ramp_spC >= 13.0):
              raise ValueError(f"ramp_up_time_pt/(pt-bt) is {ramp_spC:.1f}C, must be >= 13C")
              sys.exit()
        # Validate ports
        available_ports = list_available_ports()
        if config_values['serial_port_HP'] not in available_ports:
            print(f" Warning: Serial port '{config_values['serial_port_HP']}' not found on system.")
            print(f" Available ports are {available_ports} .")
            sys.exit()
    
        if config_values['serial_port_scales'] not in available_ports:
            print(f" Warning: Serial port '{config_values['serial_port_scales']}' not found on system.")
            print(f" Available ports are {available_ports} .")
            serial_port_scales = None
        else:
            serial_port_scales=config_values['serial_port_scales']

        return ExperimentConfig(
            base_temperature=base_temp,
            peak_temperature=peak_temp,
            ramp_up_time_bt=config_values['ramp_up_time_bt'],
            hold_time_bt=config_values['hold_time_bt'],
            ramp_up_time_pt=config_values['ramp_up_time_pt'],
            hold_time_pt=config_values['hold_time_pt'],
            ramp_down_time_bt=config_values['ramp_down_time_bt'],
            serial_port_HP=config_values['serial_port_HP'],
            serial_port_scales=serial_port_scales,
        )

    except KeyError as e:
        raise KeyError(f"Missing required config key: {e}")

def list_available_ports():
    """Return a list of available COM port names (e.g., ['COM3', 'COM4'])"""
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]
		
def Stop_ramp(ser):
    Stop_ramp_bytes = bytes([0x01, 0x06, 0x00, 0x02, 0x00, 0x00, 0x28, 0x0A])
    ser.write(Stop_ramp_bytes) # Stop ramp in case a previous one is still running
    ser.flush()
    time.sleep(0.05)
    response = ser.read(8)
    if len(response) != 8:
        print("Error: Invalid response length for Stop_ramp_bytes, communication with heat plate failed")
        sys.exit()
    else:
        print("Temperature ramp stopped")
    return

def Set_SV(ser, config: ExperimentConfig):
    global ComTalking        
    
    base_SV_bytes = bytes([0x01, 0x06, 0x00, 0x00])
    SV_value = config.base_temperature
    scaled_SV_value = int(SV_value * 10)  # Multiply by 10

    # Convert to two bytes: high byte first, low byte second (big endian)
    high_byte = (scaled_SV_value >> 8) & 0xFF
    low_byte = scaled_SV_value & 0xFF

    SV_bytes = base_SV_bytes + bytes([high_byte, low_byte])
 
    inbyte = bytearray(8)
        
    while ComTalking:
        time.sleep(0.01)  # Wait 10ms if another routine is using the port

    ComTalking = True  # Mark communication as in progress
    by_rd_cnt = -1
    while by_rd_cnt < 0:
        SV_bytes_with_crc = bytearray(SV_bytes)  # Create a copy of SV_bytes
        crc_buf = modbus_calc_crc(SV_bytes_with_crc, 6)  # Compute CRC
        SV_bytes_with_crc.extend(crc_buf)  # Append CRC to the copy
                
        ser.write(bytearray(SV_bytes_with_crc))  # Send data
        ser.flush()
        time.sleep(0.05)  # Wait 50ms
                
        by_rd_cnt = ser.readinto(inbyte)  # Read 8 bytes from controller
               
        if by_rd_cnt != 8 or inbyte[6] != crc_buf[0] or inbyte[7] != crc_buf[1]:
            print("Error: Invalid or corrupted response for SV")
            ser.reset_output_buffer()
            ser.reset_input_buffer()
            time.sleep(0.1)
            by_rd_cnt = -1
            
    ComTalking = False  # Release communication lock

    print("Temperature SV set to:", SV_value)

def Ctrl_tempON(ser):
    Ctrl_tempON_bytes = bytes([0x01, 0x06, 0x00, 0x02, 0x00, 0x04, 0x29, 0xC9]) # SPON
    ser.write(Ctrl_tempON_bytes)
    ser.flush()
    time.sleep(0.05)
    response = ser.read(8)
    if len(response) != 8:
        print("Error: Invalid response length for Ctrl_tempON_bytes, communication with heat plate failed")
        sys.exit()
    else:
        print("Temperature controlled at SV")
    return
	
def modbus_calc_crc(frame, length):
# Calculation of the modbus crc is performed as suggested 
# by the example code provided by Accuthermo Technology Corp. 
# for controlling the ATEC302 TE Temperature Controller. 
    crc = 0xFFFF
    for cnt_byte in range(length):
        crc ^= frame[cnt_byte]
        for _ in range(8):
            bit_val = crc & 0x0001
            crc >>= 1
            if bit_val == 1:
                crc ^= 0xA001  # MODBUS generator polynomial
        
    crc_buf = [crc & 0x00FF, (crc >> 8)]  # Low byte first
    return crc_buf

def Set_ramp_val(ser, config: ExperimentConfig):
    global ComTalking        

    # Peak temperature
    peak_value = config.peak_temperature
    scaled_peak_value = int(peak_value * 10)  # Multiply by 10

    # Convert to two bytes: high byte first, low byte second (big endian)
    p_high_byte = (scaled_peak_value >> 8) & 0xFF
    p_low_byte = scaled_peak_value & 0xFF

    # Base temperature 
    base_value = config.base_temperature
    scaled_base_value = int(base_value * 10)  # Multiply by 10

    # Convert to two bytes: high byte first, low byte second (big endian)
    b_high_byte = (scaled_base_value >> 8) & 0xFF
    b_low_byte = scaled_base_value & 0xFF

    # Ramp time RT1
    rt1_high_byte = (config.ramp_up_time_bt >> 8) & 0xFF
    rt1_low_byte = config.ramp_up_time_bt & 0xFF

    # Soak time ST1
    st1_high_byte = (config.hold_time_bt >> 8) & 0xFF
    st1_low_byte = config.hold_time_bt & 0xFF
	
    # Ramp time RT2
    rt2_high_byte = (config.ramp_up_time_pt >> 8) & 0xFF
    rt2_low_byte = config.ramp_up_time_pt & 0xFF
	
	# Soak time ST2
    st2_high_byte = (config.hold_time_pt >> 8) & 0xFF
    st2_low_byte = config.hold_time_pt & 0xFF

    # Ramp time RT3
    rt3_high_byte = (config.ramp_down_time_bt >> 8) & 0xFF
    rt3_low_byte = config.ramp_down_time_bt & 0xFF	
	
    # Common first three bytes
    base_combuf = [0x01, 0x06, 0x00]
    # List of command bytes 3, 4 and 5:
    command_bytes = [
        [0x34, 0x00, 0x28], 					# STAT, do not save position
        [0x35, 0x00, 0x2B], 					# STAR, run program start from PV
        [0x36, 0x01, 0x2C], 					# BAND, 30.0 C
        [0x37, rt1_high_byte, rt1_low_byte], 	# RT1, ramp time 60 seconds
        [0x38, b_high_byte, b_low_byte], 		# SP1, 1st set point is base temperature
        [0x39, st1_high_byte, st1_low_byte], 	# ST1, soak time 120 seconds
        [0x3A, 0x00, 0x36], 					# SF1, NEXT
        [0x3B, 0x00, 0x01], 					# LN1, loop
        [0x3C, rt2_high_byte, rt2_low_byte], 	# RT2, 156 seconds
        [0x3D, p_high_byte, p_low_byte], 		# SP2, 2nd set point is peak temperature
        [0x3E, st2_high_byte, st2_low_byte], 	# ST2, soak time 0 seconds
        [0x3F, 0x00, 0x36], 					# SF2, NEXT
        [0x40, 0x00, 0x01], 					# LN2, loop
        [0x41, rt3_high_byte, rt3_low_byte], 	# RT3, (600 seconds) 
        [0x42, b_high_byte, b_low_byte], 		# SP3, 3rd set point is base temperature
        [0x43, 0x00, 0x00], 					# ST3, soak time 0 seconds
        [0x44, 0x00, 0x34], 					# SF3, END
        [0x45, 0x00, 0x01]  					# LN3, loop
    ]  

    for command in command_bytes:
        combuf = base_combuf + command
        inbyte = bytearray(8)
        
        while ComTalking:
            time.sleep(0.01)  # Wait 10ms if another routine is using the port
        
        ComTalking = True  # Mark communication as in progress

        by_rd_cnt = -1
        while by_rd_cnt < 0:
            combuf_with_crc = combuf[:]  # Create a copy of combuf
            crc_buf = modbus_calc_crc(combuf_with_crc, 6)  # Compute CRC
            combuf_with_crc.extend(crc_buf)  # Append CRC to the copy
                
            ser.write(bytearray(combuf_with_crc))  # Send data
            ser.flush()
            time.sleep(0.05)  # Wait 50ms
                
            by_rd_cnt = ser.readinto(inbyte)  # Read 8 bytes from controller
               
            if by_rd_cnt != 8 or inbyte[6] != crc_buf[0] or inbyte[7] != crc_buf[1]:
                print("Error: Invalid or corrupted response for", command)
                ser.reset_output_buffer()
                ser.reset_input_buffer()
                time.sleep(0.1)
                by_rd_cnt = -1
            
        ComTalking = False  # Release communication lock
    print("Temperature ramp data uploaded")    
    return

def Start_ramp(ser):	
    Start_ramp_bytes = bytes([0x01, 0x06, 0x00, 0x02, 0x00, 0x05, 0xE8, 0x09])
    ser.write(Start_ramp_bytes)
    ser.flush()
    time.sleep(0.05)
    response = ser.read(8)
    if len(response) != 8:
        print("Error: Invalid response length for Start_ramp_bytes")
        sys.exit()		
    else:
        print("Temperature ramp started")
    return
 
def Read_temp(ser):
    Read_temp_bytes = bytes([0x01, 0x03, 0x10, 0x00, 0x00, 0x01, 0x80, 0xCA]) # temperature PV
    ser.write(Read_temp_bytes)
    ser.flush()
    time.sleep(0.05)		
    PV_bytes = ser.read(8)
    if len(PV_bytes) == 8:
        byte5 = PV_bytes[4]
        byte6 = PV_bytes[5]
        PV_value = struct.unpack('>H', bytes([byte5, byte6]))[0]
        PV = PV_value / 10
    else:
        PV = -100.
    return PV

if __name__ == "__main__":
  try:

    # Initialize output data
    times = []
    temperatures = []
    config = load_config("config_HP.dat")

    # Setup serial port for heat plate
    ser = serial.Serial(config.serial_port_HP, baudrate=19200, timeout=1)
    ser.reset_input_buffer()
    ser.reset_output_buffer()

    Stop_ramp(ser)
    Set_SV(ser, config)
    Ctrl_tempON(ser)
    time.sleep(0.1)
    Set_ramp_val(ser, config)
    time.sleep(0.1)	
    Start_ramp(ser)
    time.sleep(0.1)	

    start_time = time.time()
    # Repeat every ~2 seconds for 640/760 seconds to check proper controlling of temperatures    
    loopcnt = 100
	
    for i in range(loopcnt):
        PV = Read_temp(ser)
        current_time = time.time() - start_time
        times.append(current_time)
        temperatures.append(PV)
        print(f"Time: {times[-1]:.1f}s, Temperature: {PV:.1f}C")
        time.sleep(1.95)  # Wait for 1.95 seconds

  finally:
    ser.close()
