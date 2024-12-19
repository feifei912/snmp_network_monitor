import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
from pysnmp.hlapi import *
import numpy as np
from collections import deque


class SNMPMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("SNMP Network Monitor")
        self.root.geometry("1000x600")

        # 创建数据存储
        self.max_points = 30  # 存储最近30个数据点
        self.times = deque(maxlen=self.max_points)
        self.received_data = deque(maxlen=self.max_points)
        self.sent_data = deque(maxlen=self.max_points)

        # 创建图形界面
        self.create_gui()

        # SNMP配置
        self.host = '127.0.0.1'  # 默认本地主机
        self.community = 'public'
        self.port = 161

        # 控制标志
        self.running = False

    def create_gui(self):
        # 创建控制框架
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=5)

        # 添加输入框和按钮
        tk.Label(control_frame, text="Host:").pack(side=tk.LEFT, padx=5)
        self.host_entry = tk.Entry(control_frame, width=15)
        self.host_entry.insert(0, "127.0.0.1")
        self.host_entry.pack(side=tk.LEFT, padx=5)

        self.start_button = tk.Button(control_frame, text="Start Monitoring",
                                      command=self.toggle_monitoring)
        self.start_button.pack(side=tk.LEFT, padx=5)

        # 创建图表
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def get_snmp_data(self, oid):
        try:
            errorIndication, errorStatus, errorIndex, varBinds = next(
                getCmd(SnmpEngine(),
                       CommunityData(self.community, mpModel=0),
                       UdpTransportTarget((self.host, self.port)),
                       ContextData(),
                       ObjectType(ObjectIdentity(oid)))
            )

            if errorIndication:
                messagebox.showerror("Error", f"SNMP Error: {errorIndication}")
                return None
            elif errorStatus:
                messagebox.showerror("Error", f"SNMP Error: {errorStatus}")
                return None
            else:
                return int(varBinds[0][1])

        except Exception as e:
            messagebox.showerror("Error", f"Error getting SNMP data: {str(e)}")
            return None

    def update_plot(self):
        if not self.running:
            return

        try:
            # 获取SNMP数据
            received = self.get_snmp_data('1.3.6.1.2.1.2.2.1.11.1')  # ifInUcastPkts
            sent = self.get_snmp_data('1.3.6.1.2.1.2.2.1.17.1')  # ifOutUcastPkts

            if received is None or sent is None:
                self.running = False
                return

            # 更新数据
            current_time = time.time()
            if not self.times:
                self.start_time = current_time

            self.times.append(current_time - self.start_time)
            self.received_data.append(received)
            self.sent_data.append(sent)

            # 清除并重绘图表
            self.ax.clear()
            self.ax.plot(list(self.times), list(self.received_data),
                         'b-', label='Received Packets')
            self.ax.plot(list(self.times), list(self.sent_data),
                         'r-', label='Sent Packets')

            # 设置图表属性
            self.ax.set_xlabel('Time (seconds)')
            self.ax.set_ylabel('Packets Count')
            self.ax.set_title('Network Traffic Monitor')
            self.ax.grid(True)
            self.ax.legend()

            # 更新画布
            self.canvas.draw()

            # 每10秒更新一次
            self.root.after(10000, self.update_plot)

        except Exception as e:
            messagebox.showerror("Error", f"Update error: {str(e)}")
            self.running = False

    def toggle_monitoring(self):
        if not self.running:
            self.host = self.host_entry.get()
            self.running = True
            self.start_button.config(text="Stop Monitoring")
            self.times.clear()
            self.received_data.clear()
            self.sent_data.clear()
            self.update_plot()
        else:
            self.running = False
            self.start_button.config(text="Start Monitoring")


def main():
    root = tk.Tk()
    app = SNMPMonitor(root)
    root.mainloop()


if __name__ == "__main__":
    main()