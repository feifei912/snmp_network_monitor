# Development and Implementation of SNMP Management Software (Network Data Analysis)
-   EN  [English](README_EN.md)
- zh_CN [简体中文](README.md)
## Development of SNMP Management Software:

1.Utilize Python programming software and call the corresponding SNMP++ library to develop and implement an SNMP management software.
The software should access and configure network devices within a local area network (LAN).
Using the lab environment as an example, query the corresponding nodes to obtain key information, including the number of network packets received and sent by the host.
Use relevant visualization controls to display the number of network packets received and sent using different curves on the same coordinate system, with a sampling frequency of 10 seconds.   
2.Display on Webpage or GUI Window:
Display the information on a webpage or a GUI window.
On the same coordinate system, show two different curves clearly labeled to indicate the number of received packets and sent packets.

---

pip install pyasn1==0.4.8   
pip install pysnmp==4.4.12   
pip install matplotlib   
python 3.11以下   
python 3.10 Download https://www.python.org/ftp/python/3.10.10/python-3.10.10-amd64.exe</p>

---

## get_snmp_interface_descriptions.py
![image](https://github.com/user-attachments/assets/13a683a7-c59a-4c32-832f-16de2a62cf0c)

## network_monitor.py   
![image](https://github.com/user-attachments/assets/7abf44a8-64ca-4562-bb16-664b7fbd7889)   

## network_monitor_choose_interface.py   
![image](https://github.com/user-attachments/assets/fa90ddb1-1ae3-41f8-99a5-4f3b1b549e93)   

---
