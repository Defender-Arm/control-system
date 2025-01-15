# Defender Arm

## Description
This project involves a mechanical device controlled to intercept the trajectory of a tracked object. The target form of this project is a multi-joint arm that is able to block swings of a sword. 

This is the main repository for our capstone project. Code for the ESP32 unit required for some test scripts is found in [this archived repo (`gateway`)](https://github.com/Defender-Arm/gateway) instead.

### Project Members
- Daksh Mathur
- Gavin Jameson (`backend` lead)
- Luke Schuurman
- Rebecca Schmelzer (`frontend` lead)
- Wisam Ashique

## Instructions for **demo testing scripts**

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
Run with `python3.8 src/test/test_demo.py`