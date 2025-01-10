# SNMP Network Monitor

- zh_CN [简体中文](README.md)
-   EN  [English](README_EN.md)

## Introduction
SNMP Network Monitor is a tool developed in Python that acts as an SNMP manager. It is designed to access and configure network devices within a local area network (LAN). The tool queries respective nodes to retrieve key information, such as the number of network packets received and sent by a host. This information is then visualized using relevant controls, displaying the data on the same coordinate system at a sampling frequency of 10 seconds.

## Features
1. Developed using Python and the SNMP++ library to create an SNMP management endpoint.
2. Queries network devices within a LAN to retrieve key network information.
3. Displays the number of network packets received and sent with a 10-second sampling frequency.
4. Visualizes the data on the same coordinate system with two different curves for received and sent packets.

## Installation
1. Install the required libraries:
    ```sh
    pip install pyasn1==0.4.8   
    pip install pysnmp==4.4.12   
    pip install matplotlib   
    ```
2. Ensure your Python version is below 3.11:
    - Download Python 3.10 from [Python 3.10.10](https://www.python.org/ftp/python/3.10.10/python-3.10.10-amd64.exe)

## Usage
1. Run `get_snmp_interface_descriptions.exe` to find the corresponding OID.
2. Modify the last digit in `network_monitor_input` to the interface you want to monitor,then start and monitoring.
3. Run `network_monitor.py` to start monitoring the network data.

## File Descriptions
- `get_snmp_interface_descriptions.py`: Used to find interface descriptions of network devices.
- `network_monitor.py`: Main script for network monitoring.
- `network_monitor_choose_interface.py`: Script for selecting the network interface to monitor.

## Examples
### get_snmp_interface_descriptions.py
![image](https://github.com/user-attachments/assets/13a683a7-c59a-4c32-832f-16de2a62cf0c)

### network_monitor.py
![image](https://github.com/user-attachments/assets/7abf44a8-64ca-4562-bb16-664b7fbd7889)

### network_monitor_choose_interface.py
![image](https://github.com/user-attachments/assets/fa90ddb1-1ae3-41f8-99a5-4f3b1b549e93)

---

This project currently has basic functionality and may be updated in the future.
