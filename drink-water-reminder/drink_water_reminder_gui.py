import time
import random
import schedule
import tkinter as tk
from tkinter import messagebox, PhotoImage
from datetime import datetime
from plyer import notification
import sys
import os
import threading
import pystray
from PIL import Image, ImageTk
import tempfile

# 提醒喝水的候选语句
REMINDER_TEXTS = [
    "该喝水啦！保持水分对健康很重要。",
    "请别忘记补充水分哦！",
    "身体需要水分，现在是喝水的好时机。",
    "提醒您：喝杯水，让身体更健康。",
    "工作再忙，也别忘了喝水哦！",
    "每天8杯水，健康没烦恼！现在喝一杯吧。",
    "请您停下来喝点水，保持身体水分很重要。",
    "水是生命之源，现在请您喝一杯水。",
    "hey！到喝水时间啦！",
    "休息一下，喝杯水再继续工作吧！"
]

class DrinkWaterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("喝水提醒助手")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)
        
        # 获取程序路径
        self.script_dir = os.path.dirname(os.path.realpath(__file__))
        
        # 设置图标
        self.icon_path = os.path.join(self.script_dir, "water_icon.png")
        if not os.path.exists(self.icon_path):
            # 如果没有图标文件，创建一个简单的默认图标
            self.icon_path = self.create_default_icon()
            
        try:
            icon = PhotoImage(file=self.icon_path)
            self.root.iconphoto(True, icon)
        except:
            pass
        
        # 设置UI元素
        self.setup_ui()
        
        # 创建系统托盘图标
        self.setup_tray()
        
        # 定时器线程
        self.running = True
        self.thread = threading.Thread(target=self.schedule_checker)
        self.thread.daemon = True
        self.thread.start()
        
        # 启动时检查是否需要发送通知
        self.show_notification()
        
    def create_default_icon(self):
        """创建默认图标文件"""
        try:
            # 创建一个蓝色背景的临时图标
            temp_dir = tempfile.gettempdir()
            icon_path = os.path.join(temp_dir, "water_icon.png")
            
            # 创建一个简单的蓝色水滴图标
            img = Image.new('RGBA', (64, 64), color=(255, 255, 255, 0))
            pixels = img.load()
            
            # 绘制一个简单的水滴形状
            for i in range(img.size[0]):
                for j in range(img.size[1]):
                    x = i - img.size[0] // 2
                    y = j - img.size[1] // 2
                    dist = (x**2 + y**2)**0.5
                    
                    if dist < 25 and y > -10:
                        blue_val = min(255, int(200 + dist))
                        pixels[i, j] = (0, 120, blue_val, 230)
            
            img.save(icon_path)
            return icon_path
        except:
            return None
        
    def setup_ui(self):
        # 标题
        title_label = tk.Label(
            self.root, 
            text="喝水提醒助手", 
            font=("微软雅黑", 18, "bold")
        )
        title_label.pack(pady=20)
        
        # 状态显示
        status_frame = tk.Frame(self.root)
        status_frame.pack(pady=10, fill=tk.X, padx=20)
        
        status_label = tk.Label(
            status_frame, 
            text="状态:", 
            font=("微软雅黑", 12)
        )
        status_label.pack(side=tk.LEFT, padx=5)
        
        self.status_text = tk.Label(
            status_frame, 
            text="正在运行", 
            font=("微软雅黑", 12, "bold"),
            fg="green"
        )
        self.status_text.pack(side=tk.LEFT)
        
        # 提醒时间范围
        time_frame = tk.Frame(self.root)
        time_frame.pack(pady=5, fill=tk.X, padx=20)
        
        time_label = tk.Label(
            time_frame, 
            text="提醒时间:", 
            font=("微软雅黑", 12)
        )
        time_label.pack(side=tk.LEFT, padx=5)
        
        time_value = tk.Label(
            time_frame, 
            text="下午2点至下午7点 (每小时)", 
            font=("微软雅黑", 12)
        )
        time_value.pack(side=tk.LEFT)
        
        # 下一次提醒倒计时
        countdown_frame = tk.Frame(self.root)
        countdown_frame.pack(pady=5, fill=tk.X, padx=20)
        
        countdown_label = tk.Label(
            countdown_frame, 
            text="下次提醒:", 
            font=("微软雅黑", 12)
        )
        countdown_label.pack(side=tk.LEFT, padx=5)
        
        self.countdown_value = tk.Label(
            countdown_frame, 
            text="计算中...", 
            font=("微软雅黑", 12)
        )
        self.countdown_value.pack(side=tk.LEFT)
        
        # 测试按钮
        test_button = tk.Button(
            self.root, 
            text="测试提醒", 
            font=("微软雅黑", 12),
            command=self.test_notification,
            width=15,
            height=1
        )
        test_button.pack(pady=20)
        
        # 更新倒计时
        self.update_countdown()
        
    def setup_tray(self):
        """设置系统托盘图标"""
        # 加载图标
        try:
            image = Image.open(self.icon_path)
        except:
            # 如果无法加载图标，创建一个简单的默认图标
            image = Image.new('RGB', (64, 64), color='blue')
        
        # 创建菜单项
        menu = (
            pystray.MenuItem("显示窗口", self.show_window),
            pystray.MenuItem("测试提醒", self.test_notification),
            pystray.MenuItem("退出", self.quit_app)
        )
        
        # 创建系统托盘图标
        self.tray_icon = pystray.Icon("喝水提醒助手", image, "喝水提醒助手", menu)
        
        # 在另一个线程中运行托盘图标
        threading.Thread(target=self.tray_icon.run, daemon=True).start()
    
    def update_countdown(self):
        """更新下次提醒的倒计时"""
        now = datetime.now()
        current_hour = now.hour
        
        if 14 <= current_hour < 19:
            next_hour = current_hour + 1
            next_time = now.replace(hour=next_hour, minute=0, second=0, microsecond=0)
        elif current_hour < 14:
            next_time = now.replace(hour=14, minute=0, second=0, microsecond=0)
        else:  # current_hour >= 19
            next_time = now.replace(hour=14, minute=0, second=0, microsecond=0)
            next_time = next_time.replace(day=next_time.day + 1)
        
        time_diff = next_time - now
        hours, remainder = divmod(time_diff.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if 14 <= current_hour <= 19:
            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            time_str = "非提醒时段"
            
        self.countdown_value.config(text=time_str)
        self.root.after(1000, self.update_countdown)
        
    def show_notification(self):
        """显示喝水提醒通知"""
        current_time = datetime.now()
        # 只在下午2点到7点之间发送通知
        if 14 <= current_time.hour <= 19:
            # 随机选择一条提醒语
            reminder_text = random.choice(REMINDER_TEXTS)
            
            # 显示系统通知
            notification.notify(
                title="喝水提醒",
                message=reminder_text,
                app_name="喝水助手",
                app_icon=self.icon_path,  # 可选：自定义图标
                timeout=10  # 通知显示10秒
            )
            
            # 同时弹出对话框（更明显的提醒）
            self.root.after(500, lambda: messagebox.showinfo("喝水提醒", reminder_text))
            
            print(f"[{current_time.strftime('%Y-%m-%d %H:%M:%S')}] 已发送喝水提醒")
    
    def test_notification(self):
        """测试通知功能"""
        reminder_text = random.choice(REMINDER_TEXTS)
        notification.notify(
            title="喝水提醒 (测试)",
            message=reminder_text,
            app_name="喝水助手",
            timeout=10
        )
        messagebox.showinfo("喝水提醒 (测试)", reminder_text)
        
    def schedule_checker(self):
        """定时器检查线程"""
        # 设置每小时执行一次
        schedule.every().hour.at(":00").do(self.show_notification)
        
        while self.running:
            schedule.run_pending()
            time.sleep(1)
    
    def hide_window(self):
        """隐藏主窗口"""
        self.root.withdraw()
        if self.tray_icon:
            notification.notify(
                title="喝水提醒助手",
                message="程序已最小化到系统托盘，将继续在后台运行",
                app_name="喝水助手",
                app_icon=self.icon_path,
                timeout=4
            )
    
    def show_window(self):
        """显示主窗口"""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
    
    def quit_app(self):
        """退出应用程序"""
        if messagebox.askokcancel("退出", "确定要退出喝水提醒程序吗？\n提示：程序退出后将不再提醒您喝水。"):
            self.running = False
            if self.tray_icon:
                self.tray_icon.stop()
            self.root.destroy()
            sys.exit(0)
            
    def on_closing(self):
        """窗口关闭时的处理"""
        self.hide_window()

if __name__ == "__main__":
    root = tk.Tk()
    app = DrinkWaterApp(root)
    root.mainloop() 