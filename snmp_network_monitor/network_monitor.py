#!/usr/bin/env python

# coding: utf-8
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

        # 设置语言字典
        self.lang_dict = {
            "zh": {
                "title": "SNMP网络监控",
                "host_label": "主机:",
                "start_monitor": "开始监控",
                "pause_monitor": "暂停监控",
                "end_monitor": "结束监控",
                "ended": "监控已结束，无法重新启动",
                "invalid_host": "无效的主机地址",
                "snmp_error": "获取 SNMP 数据失败，停止监控",
                "info_end": "监控已结束",
                "time_label": "时间（秒）",
                "packet_label": "数据包数",
                "chart_title": "网络流量监控",
                "error_title": "错误",
                "received_label": "接收的数据包数",
                "sent_label": "发送的数据包数"
            },
            "en": {
                "title": "SNMP Network Monitor",
                "host_label": "Host:",
                "start_monitor": "Start Monitoring",
                "pause_monitor": "Pause Monitoring",
                "end_monitor": "End Monitoring",
                "ended": "Monitoring ended, cannot restart",
                "invalid_host": "Invalid host address",
                "snmp_error": "SNMP data retrieval failed, monitoring stopped",
                "info_end": "Monitoring ended",
                "time_label": "Time (s)",
                "packet_label": "Packets",
                "chart_title": "Network Traffic Monitor",
                "error_title": "Error",
                "received_label": "Received Packets",
                "sent_label": "Sent Packets"
            }
        }

        # 当前语言，默认为中文
        self.current_lang = "zh"

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
        self.header_logged = False

    def create_gui(self):
        # 语言选择下拉框
        lang_frame = tk.Frame(self.root)
        lang_frame.pack(pady=5)

        tk.Label(lang_frame, text="语言 / Language:").pack(side=tk.LEFT, padx=5)
        self.lang_var = tk.StringVar()
        self.lang_var.set("中文")  # 默认显示“中文”
        lang_options = ["中文", "English"]
        self.lang_menu = tk.OptionMenu(lang_frame, self.lang_var, *lang_options, command=self.switch_language)
        self.lang_menu.pack(side=tk.LEFT, padx=5)

        # 创建控制框架
        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(pady=5)

        # 添加输入框和按钮
        self.host_label = tk.Label(self.control_frame, text=self.lang_dict[self.current_lang]["host_label"])
        self.host_label.pack(side=tk.LEFT, padx=5)
        self.host_entry = tk.Entry(self.control_frame, width=15)
        self.host_entry.insert(0, self.host)
        self.host_entry.pack(side=tk.LEFT, padx=5)

        self.start_button = tk.Button(self.control_frame, text=self.lang_dict[self.current_lang]["start_monitor"],
                                      command=self.toggle_monitoring)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.end_button = tk.Button(self.control_frame, text=self.lang_dict[self.current_lang]["end_monitor"],
                                    command=self.end_monitoring)
        self.end_button.pack(side=tk.LEFT, padx=5)

        # 创建图表
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # 设置中文字体
        self.set_chinese_font()
        # 初始化窗口标题
        self.root.title(self.lang_dict[self.current_lang]["title"])

    def switch_language(self, _):
        # 根据下拉框选择更新 current_lang
        choice = self.lang_var.get()
        if choice == "中文":
            self.current_lang = "zh"
        else:
            self.current_lang = "en"

        # 更新界面文字
        self.root.title(self.lang_dict[self.current_lang]["title"])
        self.host_label.config(text=self.lang_dict[self.current_lang]["host_label"])
        if self.running:
            self.start_button.config(text=self.lang_dict[self.current_lang]["pause_monitor"])
        else:
            self.start_button.config(text=self.lang_dict[self.current_lang]["start_monitor"])
        self.end_button.config(text=self.lang_dict[self.current_lang]["end_monitor"])

        # 立即刷新
        self.root.update_idletasks()

    def set_chinese_font(self):
        # 使用SimHei字体
        font_path = 'C:/Windows/Fonts/simhei.ttf'  # 确保字体路径正确
        if os.path.exists(font_path):
            fm.FontProperties(fname=font_path)
            plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用SimHei字体
        plt.rcParams['axes.unicode_minus'] = False

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
            received = self.get_snmp_data('1.3.6.1.2.1.2.2.1.11.26')
            sent = self.get_snmp_data('1.3.6.1.2.1.2.2.1.17.26')

            print(f"收到: {received}, 发送: {sent}")

            if received is None or sent is None:
                self.running = False
                messagebox.showerror(self.lang_dict[self.current_lang]["error_title"],
                                     self.lang_dict[self.current_lang]["snmp_error"])
                self.start_button.config(text=self.lang_dict[self.current_lang]["start_monitor"])
                return

            if not self.header_logged:
                self.log_file.write("\n以下来自network_monitor\n")
                self.header_logged = True

            self.log_file.write(f"时间: {time.time()}, 接收: {received}, 发送: {sent}\n")

            current_time = time.time()
            if not self.times:
                self.start_time = current_time

            self.times.append(current_time - self.start_time)
            self.received_data.append(received)
            self.sent_data.append(sent)

            self.ax.clear()
            self.ax.plot(list(self.times), list(self.received_data), 'b-',
                         label=self.lang_dict[self.current_lang]["received_label"])
            self.ax.plot(list(self.times), list(self.sent_data), 'r-',
                         label=self.lang_dict[self.current_lang]["sent_label"])

            self.ax.set_xlabel(self.lang_dict[self.current_lang]["time_label"])
            self.ax.set_ylabel(self.lang_dict[self.current_lang]["packet_label"])
            self.ax.set_title(self.lang_dict[self.current_lang]["chart_title"])
            self.ax.grid(True)
            self.ax.legend()

            self.canvas.draw()

            self.root.after(1000, self.update_plot)

        except Exception as e:
            print(f"更新错误: {str(e)}")
            self.running = False
            self.start_button.config(text=self.lang_dict[self.current_lang]["start_monitor"])

    def toggle_monitoring(self):
        if self.ended:
            messagebox.showinfo("", self.lang_dict[self.current_lang]["ended"])
            return

        if not self.running:
            self.host = self.host_entry.get()
            if not self.validate_host(self.host):
                messagebox.showerror(self.lang_dict[self.current_lang]["error_title"],
                                     self.lang_dict[self.current_lang]["invalid_host"])
                return
            self.running = True
            self.start_button.config(text=self.lang_dict[self.current_lang]["pause_monitor"])
            self.times.clear()
            self.received_data.clear()
            self.sent_data.clear()
            self.update_plot()
        else:
            self.running = False
            self.start_button.config(text=self.lang_dict[self.current_lang]["start_monitor"])

    def end_monitoring(self):
        self.running = False
        self.ended = True
        self.start_button.config(state=tk.DISABLED)
        self.log_file.close()
        messagebox.showinfo("", self.lang_dict[self.current_lang]["info_end"])

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
