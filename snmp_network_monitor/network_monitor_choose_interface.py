import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
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
        self.root.title("SNMP网络监控 - 可选接口")
        self.root.geometry("1000x650")

        # 初始化 SNMP 配置
        self.host = '127.0.0.1'  # 修改为目标设备的 IP 地址
        self.community = 'public'
        self.port = 161

        # 数据存储队列（用于绘图）
        self.max_points = 30  # 仅存储最近 30 个数据点
        self.times = deque(maxlen=self.max_points)
        self.received_data = deque(maxlen=self.max_points)
        self.sent_data = deque(maxlen=self.max_points)

        # 定义一个接口映射表（可按需扩充），其中键为可读的接口名称，值为 (接收OID, 发送OID) 的元组
        self.interface_options = {
            "Intel(R) Wi-Fi 6 AX201 160MHz": (
                "1.3.6.1.2.1.2.2.1.11.26",
                "1.3.6.1.2.1.2.2.1.17.26"
            ),
            "Realtek Gaming 2.5GbE Family Controller": (
                "1.3.6.1.2.1.2.2.1.11.2",  # 接收数据包数 OID
                "1.3.6.1.2.1.2.2.1.17.2"  # 发送数据包数 OID
            ),
            "VMware Virtual Ethernet (VMnet8)": (
                "1.3.6.1.2.1.2.2.1.11.9",
                "1.3.6.1.2.1.2.2.1.17.9"
            ),
            # 如果还需要更多接口，可在此处继续添加
        }

        # 记录当前选择的接口名称，初始默认选第一个
        self.selected_interface = list(self.interface_options.keys())[0]

        # 创建 GUI
        self.create_gui()

        # 监控标志
        self.running = False
        self.ended = False

        # 打开日志文件以记录数据
        self.log_file = open("network_data_log.txt", "a", encoding="utf-8")
        self.header_logged = False  # 添加标志，记录是否已输出头信息

    def create_gui(self):

        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=5)

        # 主机地址
        tk.Label(control_frame, text="主机:").pack(side=tk.LEFT, padx=5)
        self.host_entry = tk.Entry(control_frame, width=15)
        self.host_entry.insert(0, self.host)
        self.host_entry.pack(side=tk.LEFT, padx=5)

        # 接口选择下拉菜单
        tk.Label(control_frame, text="接口选择:").pack(side=tk.LEFT, padx=5)
        self.interface_combo = ttk.Combobox(
            control_frame,
            values=list(self.interface_options.keys()),
            width=35
        )
        self.interface_combo.current(0)  # 默认显示第一个接口
        self.interface_combo.pack(side=tk.LEFT, padx=5)

        # 开始 / 暂停监控按钮
        self.start_button = tk.Button(control_frame, text="开始监控",
                                      command=self.toggle_monitoring)
        self.start_button.pack(side=tk.LEFT, padx=5)

        # 结束监控按钮
        self.end_button = tk.Button(control_frame, text="结束监控",
                                    command=self.end_monitoring)
        self.end_button.pack(side=tk.LEFT, padx=5)

        # Matplotlib 图表
        self.fig, self.ax = plt.subplots(figsize=(10, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # 设置中文字体（Windows 示例）
        self.set_chinese_font()

    def set_chinese_font(self):
        font_path = 'C:/Windows/Fonts/simhei.ttf'
        if os.path.exists(font_path):
            fm.FontProperties(fname=font_path)
            plt.rcParams['font.sans-serif'] = ['SimHei']
        # 避免中文显示的负号问题
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
                    # varBind[1] 即为数值
                    return int(varBind[1])
        except Exception as e:
            print(f"获取 SNMP 数据错误: {str(e)}")
            return None

    def update_plot(self):
        if not self.running or self.ended:
            return

        try:
            # 获取当前在下拉菜单里选中的接口名称
            current_interface = self.interface_combo.get()

            # 如果用户在监控过程中切换了接口，需要清除旧数据
            if current_interface != self.selected_interface:
                self.selected_interface = current_interface
                self.times.clear()
                self.received_data.clear()
                self.sent_data.clear()
                self.start_time = time.time()

            # 从接口映射表中取出该接口对应的 (received_oid, sent_oid)
            received_oid, sent_oid = self.interface_options[self.selected_interface]

            # 通过 SNMP 获取当前的接收和发送数据包数
            received = self.get_snmp_data(received_oid)
            sent = self.get_snmp_data(sent_oid)

            print(f"当前接口: {self.selected_interface}, 接收: {received}, 发送: {sent}")

            # 如果获取不到数据，则停止监控并提醒
            if received is None or sent is None:
                self.running = False
                messagebox.showerror("错误", "获取 SNMP 数据失败，停止监控")
                self.start_button.config(text="开始监控")
                return

            # 记录到日志文件
            if not self.header_logged:
                self.log_file.write("\n以下来自network_monitor_choose_OID\n")
                self.header_logged = True  # 设置标志为 True

            now = time.time()
            self.log_file.write(f"时间: {now}, 接口: {self.selected_interface}, 接收: {received}, 发送: {sent}\n")

            # 更新数据队列
            if not self.times:
                self.start_time = now
            self.times.append(now - self.start_time)
            self.received_data.append(received)
            self.sent_data.append(sent)

            # 清空并重绘图表
            self.ax.clear()
            self.ax.plot(self.times, self.received_data, 'b-', label='接收的数据包数')
            self.ax.plot(self.times, self.sent_data, 'r-', label='发送的数据包数')

            # 设置图表样式
            self.ax.set_xlabel('时间 (秒)')
            self.ax.set_ylabel('数据包数')
            self.ax.set_title('网络流量监控 - 可选接口')
            self.ax.grid(True)
            self.ax.legend()

            # 重绘图表
            self.canvas.draw()

            # 1 秒后再次调用 update_plot
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
            # 尝试获取主机地址并验证
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
            # 暂停监控
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
