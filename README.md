# CAREST
## CAREST: Controlling and Recording Experiments in Sensitivity to Temperature



**CAREST** is a PsychoPy-based tool for the assessment of temperature and pain sensitivity via thermal induction. CAREST controls and communicates with a cold/hot plate (AHP 1200, Thermoelectric Cooling America Corporation, Chicago, USA) and provides a touchscreen slider to assess pain sensation on a Visual Analogue Scale (VAS). The plate is placed on a platform with load cells (M5Stack Technology Co., Ltd., China) to measure hand-plate contact force. CAREST continuously records timestamped values of plate surface temperature, participants’ VAS rating and hand-plate contact force facilitating measures of temperature and pain sensitivity. 
The software package consists of CAREST.psyexp, HP_commands.py, config.dat, VAS.jpg, scale.ino and Plot_CAREST.py. The first four files have to be in the same folder. CAREST was developed using PsychoPy v2024.1.4., scale.ino was compiled with Arduino IDE 2.3.3. All tests were performed on a Windows 11 platform.

## Hardware:

The experimental setup consists of an AHP-1200 cold/heat plate (Thermoelectric Cooling America Corporation, Chicago, USA) placed on a scale platform with four load cells (M5Stack Technology Co., Ltd., China). The analogue signals from the load cells are digitized by an HX711 24-bit A/D converter chip (M5Stack) and transmitted to a touchscreen laptop (Windows 11) via an ESP32 Basic Core IoT Development Kit V2.7 (M5Stack). The internal temperature controller (ATEC302) of the AHP-1200 cold/heat plate is connected to the second USB port of the laptop.

## Software:

### scale.ino
The ESP32-based scale interface runs the program 'scale.ino'. This program reads the signals from the four load cells via an HX711 A/D converter at a rate of ten samples per second. After applying the calibration factor, the calculated force values are stored, displayed on the M5Stack LCD, and transmitted on request from CAREST via the serial connection. Additionally, a color-coded background on the display visually indicates whether the measured force is below (red) or above (green) a defined threshold. The scale is tared by sending “0” to its serial port. Upon installation the load cells should be calibrated with known weights ranging between 10 and 50 N. 
### CAREST
CAREST.psyexp was developed using the Psychopy software package (Peirce et al., 2019) using Code components for interaction with the plate and scale. The “library” “HP_commands_config.py” codes for the commands controlling and communicating with the ATEC302 temperature controller (commands were coded according to commands byte tables published in the ATEC302 TE Temperature Controller Reference Manual Rev 1.10, Mar, 2018, received from Thermoelectric Cooling America Corporation). It enables reading the user editable input file “config.dat” which contains the temperature and timing values for cold or heat pain experiments. Upon upload of the temperature and timing values to the ATEC temperature controller the plate is controlled to the baseline temperature. After an adaptation phase the temperature ramp is started. VAS pain ratings, hand-plate contact force and actual plate temperatures are recorded every two seconds during the adaptation and ramping phases. Relevant data are saved in a .csv output file. 

The add-on program, plot_CAREST, where output files can be inserted via a drag-and-drop feature, plots contact force and VAS pain ratings vs temperature as well as ratings for hypothetical vignettes, thus facilitating a quick check of data recorded during an individual experiment. 

 ### References
 Peirce J, Gray JR, Simpson S, MacAskill M, Höchenberger R, Sogo H, Kastman E, Lindeløv JK. (2019), 
 PsychoPy2: Experiments in behavior made easy Behav Res 51: 195. 
 https://doi.org/10.3758/s13428-018-01193-y
