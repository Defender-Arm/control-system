# Defender Arm

## Description
This project involves a mechanical device controlled to intercept the trajectory of a tracked object. We are currently using an IMU to measure acceleration of the object, which communicates the measurements to a Raspberry Pi onboard the mechanical component to generate control signals. The target form of this project is a multi-joint arm that is able to block swings of a sword. 

This is the main repository for our capstone project. It contains code that is run on the Raspberry Pi. Code for the ESP32 unit is found in [this repo (`gateway`)](https://github.com/Defender-Arm/gateway) instead.

### Project Members
- Daksh Mathur
- Gavin Jameson (`control-system` lead)
- Luke Schuurman
- Rebecca Schmelzer
- Wisam Ashique (`gateway` lead)

## Instructions

### Prerequisites

#### Software
- Python 3.8.X
    - Other distributions may work, however some libraries may not be compatible

#### Hardware
- Computer with Bluetooth Classic capabilities (we are using Raspberry Pi 4 Model B)

### Install
1. clone repository 
   - via SSH, with `git clone git@github.com:Defender-Arm/control-system.git`
2. in root directory of local clone, install system dependencies with `python3.8 -m pip install -r requirements.txt`

### Execute
On Pi, run with `python3.8 main_pi.py`

On Windows, run with `python3.8 main_windows.py`

### Test
Run test suite with `...`