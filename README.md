# SNMP Network Monitor

-   EN  [English](README_EN.md)
- zh_CN [简体中文](README.md)

## 简介
SNMP Network Monitor 是一个使用 Python 开发的 SNMP 管理端工具，旨在对局域网内的网络设备进行访问和配置。主要功能包括查询网络设备的相应节点，获取关键的网络信息（如主机的网络接收数据包数量和发送数据包数量），并以图表形式展示这些信息。

## 功能
1. 通过调用相应的 SNMP++ 库开发和实现一个 SNMP 管理端。
2. 查询局域网内的网络设备节点，获取关键的网络信息。
3. 以 10 秒为采样频率，显示网络接收数据包数量和发送数据包数量。
4. 在网页或 GUI 窗口中以曲线图的形式展示接收数据包和发送数据包。

## 安装
1. 安装依赖库：
    ```sh
    pip install pyasn1==0.4.8   
    pip install pysnmp==4.4.12   
    pip install matplotlib   
    ```
2. 请确保您的 Python 版本低于 3.11：
    - Python 3.10 下载链接：[Python 3.10.10](https://www.python.org/ftp/python/3.10.10/python-3.10.10-amd64.exe)

## 使用
1. 运行 `get_snmp_interface_descriptions.exe` 查找对应的 OID。
2. 修改 `network_monitor_input` 中的最后一位数为要监控的接口，点击运行开始监控。
3. 运行 `network_monitor.py` 开始监控网络数据。

## 文件说明
- `get_snmp_interface_descriptions.py`：用于查找网络设备的接口描述。
- `network_monitor.py`：主要的网络监控脚本。
- `network_monitor_choose_interface.py`：用于选择要监控的网络接口。

## 示例
### get_snmp_interface_descriptions.py
![image](https://github.com/user-attachments/assets/13a683a7-c59a-4c32-832f-16de2a62cf0c)

### network_monitor.py
![image](https://github.com/user-attachments/assets/7abf44a8-64ca-4562-bb16-664b7fbd7889)

### network_monitor_choose_interface.py
![image](https://github.com/user-attachments/assets/fa90ddb1-1ae3-41f8-99a5-4f3b1b549e93)

---

该项目目前功能较为简陋，未来可能会进行更新。

