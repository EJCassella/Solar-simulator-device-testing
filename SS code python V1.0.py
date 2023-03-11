# -*- coding: utf-8 -*-
"""
Created on Wed Oct 13 11:03:00 2021

@author: Elena Josephine Cassella
"""
##%

import numpy as np
import nidaqmx
import time
import pyvisa as visa
import matplotlib.pyplot as plt
import pandas as pd
import math
from pyvisa import constants
from nidaqmx.constants import (LineGrouping)
from datetime import datetime as dt

#%%
""" User inputs section """

batch = 'first pancake'
device = 'test'
directory = r'C:\Users\php18ejc\Desktop\D&I device run'

start_pixel = 1
end_pixel = 1



device_area =   0.02506 #6-pixel
                # 0.02365 #8-pixel
                # 0.154   #1-pixel
                # 0.03996 #25mm^2 subs each pixel

start_voltage = -0.1
stop_voltage = 1.2
voltage_step = 0.02

num_cycles = 1

delay = 50

K237_GPIB_address = 16

use_pause = 1
initial_settle_time = 0.25
GPIB_timeout = 100

""" end of user inputs sections """

#%%

def performance_metrics(voltage, current_density, device_area):
    curr = current_density*device_area/1000
    number_of_readings = len(curr)
    power = abs(voltage*curr)
    max_power = 0
    max_power_data_point = 1
    Jsc = 0
    Voc = 0
    
    for i in range(0, number_of_readings):
        if voltage[i] == 0:
            Jsc = current_density[i]
        if voltage[i] > 0 and curr[i] < 0 and i < number_of_readings:
            if power[i] >= max_power:
                max_power_data_point = i
                max_power = power[i]
        if voltage[i] > 0 and curr[i] <= 0 and i < number_of_readings:
            Voc = voltage[i] + (0-curr[i]) * (voltage[i+1]-voltage[i])  / (curr[i+1]-curr[i])
    
    Vmpp = voltage[max_power_data_point]
    Jmpp = current_density[max_power_data_point]
    
    Efficiency = 100*max_power/(device_area*0.1)
    FF = 100*Vmpp*Jmpp/(Voc*Jsc)
    
    return [Efficiency, FF, Voc, Jsc, Vmpp, Jmpp]
    
    
    
    

#%%

""" set up file name and directory for saving data """

number_of_readings = 1+(stop_voltage-start_voltage)/voltage_step
number_of_readings = math.ceil(number_of_readings)

now = dt.now()
dt_string = now.strftime("%d.%m.%Y %H.%M.%S")
file_name = (dt_string + ' ' + batch + '-' + device)
file_path = (directory + '\\' + file_name + '.csv')




#%%
""" Fine the testboard and initialise all 8 lines for all 3 ports into Digital Output channels and set up the booleans to write """

task = nidaqmx.Task()
all_ports = ("Testboard/port0/line0:7, Testboard/port1/line0:7, Testboard/port2/line0:7")
task.do_channels.add_do_chan(all_ports,"all ports", line_grouping=LineGrouping.CHAN_PER_LINE)
task.start()

#%%

#port    =                                       [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2,]
#line    =                                       [0, 1, 2, 3, 4, 5, 6, 7, 0, 1, 2, 3, 4, 5, 6, 7, 0, 1, 2, 3, 4, 5, 6, 7,]
initialise =                            np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,], dtype=bool)
shutterOFF_everythingelseOFF =          np.array([0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,], dtype=bool)
shutterON_everythingelseOFF =           np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,], dtype=bool)

shutterON_pixelON =             [ [] for i in range(0,9)]
shutterOFF_pixelON =           [ [] for i in range(0,9)]

shutterON_pixelON[1].append(            np.array([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,], dtype=bool))
shutterON_pixelON[2].append(            np.array([0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,], dtype=bool))
shutterON_pixelON[3].append(            np.array([0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,], dtype=bool))
shutterON_pixelON[4].append(            np.array([0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,], dtype=bool))
shutterON_pixelON[5].append(            np.array([0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,], dtype=bool))
shutterON_pixelON[6].append(            np.array([0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,], dtype=bool))
shutterON_pixelON[7].append(            np.array([0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,], dtype=bool))
shutterON_pixelON[8].append(            np.array([0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,], dtype=bool))

shutterOFF_pixelON[1].append(           np.array([1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,], dtype=bool))
shutterOFF_pixelON[2].append(           np.array([0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,], dtype=bool))
shutterOFF_pixelON[3].append(           np.array([0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,], dtype=bool))
shutterOFF_pixelON[4].append(           np.array([0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,], dtype=bool))
shutterOFF_pixelON[5].append(           np.array([0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,], dtype=bool))
shutterOFF_pixelON[6].append(           np.array([0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,], dtype=bool))
shutterOFF_pixelON[7].append(           np.array([0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,], dtype=bool))
shutterOFF_pixelON[8].append(           np.array([0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,], dtype=bool))

shutterON_allpixelsON =         np.array([1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,], dtype=bool)

#%%


task.write(initialise)
time.sleep(1)
task.write(shutterOFF_everythingelseOFF) #remeber to stop() and close() at end of code. Restart kernel to switch between Python and MatLab

#%% 

""" Turn on the shutter """
task.write(shutterON_everythingelseOFF)

#%%

""" Get the Keithley communicating to the PC 

Note that our crusty old Keithley doesn't accept Standard Commands for Programmable Instruments (SCPI) so if we need to update
the keithley we're going to need to update this code into SCPI commands.

"""

#Get PC talking to Keithley and confirm everything OK

rm = visa.ResourceManager()
print(rm.list_resources())
K237 = rm.open_resource('GPIB0::16::INSTR')


#%%

K237.timeout = GPIB_timeout*1000
K237.query('*IDN?') #K237 may not support this command
print(K237.read())

#%%


""" Set the Keithley up ready for measurements """

K237.write("F0,1X")

K237.write("L0.01, 8X")

K237.write("S3X")

K237.write("P0X")

K237.write("Z0X")

K237.write("B0,0,X")

K237.write("M2,1")
#
forward_sweep = ('Q1,' + str(start_voltage) + ',' + str(stop_voltage) + ',' + str(voltage_step) + ',0,' + str(delay) + 'X')
reverse_sweep = ('Q7,' + str(stop_voltage) + ',' + str(start_voltage) + ',' + str(-1*voltage_step) + ',0,' + str(delay) + 'X')
K237.write(forward_sweep)
K237.write(reverse_sweep)

K237.write("D0X")

K237.write("R1X")

K237.write("N1X")

#%% 

""" Initialise data arrays and fill in with data """

Efficiency = np.zeros((8, num_cycles*2))
FF = np.zeros((8, num_cycles*2))
Jsc = np.zeros((8, num_cycles*2))
Voc = np.zeros((8, num_cycles*2))
max_power = np.zeros((8, num_cycles*2))
Vmpp = np.zeros((8, num_cycles*2))
Jmpp = np.zeros((8, num_cycles*2))
current_density = np.zeros((number_of_readings*2, 8, num_cycles))
current = np.zeros((number_of_readings*2, 8))



#%%

""" Read voltages from Keithley and parse returned string"""


K237.write('G1,2,2X')

raw_data = K237.read()

#%%
data = raw_data.split(',')
data[-1] = data[-1].split('\r')[0]
#%%
voltage_forward = data[0:number_of_readings]
voltage_forward = [float(x) for x in voltage_forward]
voltage_backward = voltage_forward[::-1]
voltage_backward = [float(x) for x in voltage_forward]


#%%

""" Loop through pixels """


for pixel in range(start_pixel, end_pixel+1):
    print('*******************************************')
    print(('Pixel ' + str(pixel) + ' on'))
    
    if use_pause == 1:
        input('Pausing... Press enter to continue')

    task.write(shutterON_pixelON[pixel][0])
    value = task.read() 
    
    # if value == shutterON_pixelON[pixel][0]:
    #     print('Output good, continuing sweep')
    # else:
    #     print('USB6501 output error')
    #     exit
        
    time.sleep(initial_settle_time)
    
    sweep = 0
    for cycle in range(0, num_cycles):
        sweep += 1
    
    print('Triggering readings')
    
    K237.write('H0X')
    
    print('Reading currents')
    
    K237.write('G4,2,2X')
    
    raw_current_data = K237.read()
    
    current_data = raw_current_data.split(',')
    current_data[-1] = current_data[-1].split('\n')[0]
                        
    current[:number_of_readings*2,pixel-1] = current_data
    
    print('Calculating key parameters and plotting')
     #%%   
    """ Forwards sweep """
    

    current_density[:number_of_readings, pixel-1, cycle] = 1000 * current[:number_of_readings, pixel-1]/device_area
    plt.plot(voltage_forward, current_density[:number_of_readings, pixel-1])
    metric_array_fwd = []
    metric_array_fwd = performance_metrics(voltage_forward, current_density[:number_of_readings, pixel-1, cycle], device_area)
    Efficiency[pixel-1, sweep-1] =       metric_array_fwd[0]
    FF[pixel-1,sweep-1]     =            metric_array_fwd[1]
    Voc[pixel-1,sweep-1]    =            metric_array_fwd[2] 
    Jsc[pixel-1,sweep-1]    =            metric_array_fwd[3]
    Vmpp[pixel-1,sweep-1]   =            metric_array_fwd[4]
    Jmpp[pixel-1,sweep-1]   =            metric_array_fwd[5]
    
    print('PCE = ' + str(Efficiency[pixel-1,sweep-1]),
          ' Jsc = ' + str(Jsc[pixel-1,sweep-1]),
          ' Voc = ' + str(Voc[pixel-1,sweep-1]),
          ' FF = ' + str(FF[pixel-1,sweep-1]))
    
    
    """ Backwards sweep """
    
    sweep += 1
    current_density[number_of_readings:, pixel-1, cycle] = 1000 * current[number_of_readings:, pixel-1]/device_area
    plt.plot(voltage_forward, current_density[:number_of_readings, pixel-1])
    metric_array_bcwd = []
    metric_array_bcwd = performance_metrics(voltage_backward, np.flipud(current_density[number_of_readings:, pixel-1, cycle]), device_area)
    Efficiency[pixel-1, sweep-1] =  metric_array_bcwd[0]
    FF[pixel-1, sweep-1]    =       metric_array_bcwd[1]
    Voc[pixel-1, sweep-1]   =       metric_array_bcwd[2]
    Jsc[pixel-1, sweep-1]   =       metric_array_bcwd[3]
    Vmpp[pixel-1, sweep-1]  =       metric_array_bcwd[4]
    Jmpp[pixel-1, sweep-1]  =       metric_array_bcwd[5]

    print('PCE = ' + str(Efficiency[pixel-1,sweep-1]),
          ' Jsc = ' + str(Jsc[pixel-1,sweep-1]),
          ' Voc = ' + str(Voc[pixel-1,sweep-1]),
          ' FF = ' + str(FF[pixel-1,sweep-1]))    

#%%   
  
""" Turn everything off """

task.write(shutterOFF_everythingelseOFF)
task.stop()
task.close()

K237.write("N0X")  # Operate OFF
K237.close()


#%%

""" Write data to files in same format as MATLAB code """












