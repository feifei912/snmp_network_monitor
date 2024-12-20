import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
from pysnmp.hlapi import *
from collections import deque
import socket
import matplotlib.font_manager as fm
import os

class SNMPMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("SNMP网络监控")
        self.root.geometry("1000x600")

        # 初始化SNMP配置
        self.host = '127.0.0.1'  # 使用你的IP地址
        self.community = 'public'
        self.port = 161

        # 创建数据存储
        self.max_points = 30  # 存储最近30个数据点
        self.times = deque(maxlen=self.max_points)
        self.received_data = deque(maxlen=self.max_points)
        self.sent_data = deque(maxlen=self.max_points)

        # 创建图形界面
        self.create_gui()

        # 控制标志
        self.running = False
        self.ended = False

        # 打开文件记录数据变化
        self.log_file = open("network_data_log.txt", "a", encoding="utf-8")
        self.header_logged = False  # 添加标志，记录是否已输出头信息

    def create_gui(self):
        # 创建控制框架
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=5)

        # 添加输入框和按钮
        tk.Label(control_frame, text="主机:").pack(side=tk.LEFT, padx=5)
        self.host_entry = tk.Entry(control_frame, width=15)
        self.host_entry.insert(0, self.host)
        self.host_entry.pack(side=tk.LEFT, padx=5)

        self.start_button = tk.Button(control_frame, text="开始监控",
                                      command=self.toggle_monitoring)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.end_button = tk.Button(control_frame, text="结束监控",
                                    command=self.end_monitoring)
        self.end_button.pack(side=tk.LEFT, padx=5)

        # 创建图表
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # 设置中文字体
        self.set_chinese_font()

    def set_chinese_font(self):
        # 使用SimHei字体
        font_path = 'C:/Windows/Fonts/simhei.ttf'  # 确保字体路径正确
        font_prop = fm.FontProperties(fname=font_path)
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用SimHei字体
        plt.rcParams['axes.unicode_minus'] = False    # 解决负号显示问题

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
                print(f"SNMP 错误: {errorIndication}")
                return None
            elif errorStatus:
                print(f"SNMP 错误: {errorStatus.prettyPrint()}")
                return None
            else:
                for varBind in varBinds:
                    return int(varBind[1])

        except Exception as e:
            print(f"获取 SNMP 数据错误: {str(e)}")
            return None

    def update_plot(self):
        if not self.running or self.ended:
            return

        try:
            # 获取 SNMP 数据
            received = self.get_snmp_data('1.3.6.1.2.1.2.2.1.11.26')  # Intel(R) Wi-Fi 6 AX201 160MHz 的接收单播包数
            sent = self.get_snmp_data('1.3.6.1.2.1.2.2.1.17.26')  # Intel(R) Wi-Fi 6 AX201 160MHz 的发送单播包数

            # 打印调试信息
            print(f"收到: {received}, 发送: {sent}")

            if received is None or sent is None:
                self.running = False
                messagebox.showerror("错误", "获取 SNMP 数据失败，停止监控")
                self.start_button.config(text="开始监控")
                return

            # 记录数据变化
            if not self.header_logged:
                self.log_file.write("\n以下来自network_monitor\n")
                self.header_logged = True  # 设置标志为True

            self.log_file.write(f"时间: {time.time()}, 接收: {received}, 发送: {sent}\n")

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
                         'b-', label='接收的数据包数')
            self.ax.plot(list(self.times), list(self.sent_data),
                         'r-', label='发送的数据包数')

            # 设置图表属性
            self.ax.set_xlabel('时间（秒）')
            self.ax.set_ylabel('数据包数')
            self.ax.set_title('网络流量监控')
            self.ax.grid(True)
            self.ax.legend()

            # 更新画布
            self.canvas.draw()

            # 缩短更新间隔为1秒
            self.root.after(1000, self.update_plot)

        except Exception as e:
            print(f"更新错误: {str(e)}")
            self.running = False
            self.start_button.config(text="开始监控")

    def toggle_monitoring(self):
        if self.ended:
            messagebox.showinfo("信息", "监控已结束，无法重新启动")
            return

        if not self.running:
            self.host = self.host_entry.get()
            if not self.validate_host(self.host):
                messagebox.showerror("错误", "无效的主机地址")
                return
            self.running = True
            self.start_button.config(text="暂停监控")
            self.times.clear()
            self.received_data.clear()
            self.sent_data.clear()
            self.update_plot()
        else:
            self.running = False
            self.start_button.config(text="开始监控")

    def end_monitoring(self):
        self.running = False
        self.ended = True
        self.start_button.config(state=tk.DISABLED)
        self.log_file.close()
        messagebox.showinfo("信息", "监控已结束")

    def validate_host(self, host):
        try:
            socket.gethostbyname(host)
            return True
        except socket.error:
            return False

def main():
    root = tk.Tk()
    app = SNMPMonitor(root)
    root.mainloop()

if __name__ == "__main__":
    main()