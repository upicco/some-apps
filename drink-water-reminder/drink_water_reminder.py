import time
import random
import schedule
from datetime import datetime
from plyer import notification
import sys
import os

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

def show_notification():
    """显示喝水提醒通知"""
    current_time = datetime.now()
    # 只在下午2点到7点之间发送通知
    if 14 <= current_time.hour <= 19:
        # 随机选择一条提醒语
        reminder_text = random.choice(REMINDER_TEXTS)
        
        # 获取脚本所在路径
        script_dir = os.path.dirname(os.path.realpath(__file__))
        icon_path = os.path.join(script_dir, "water_icon.png")
        
        # 若图标不存在，则使用None
        if not os.path.exists(icon_path):
            icon_path = None
        
        # 显示通知
        notification.notify(
            title="喝水提醒",
            message=reminder_text,
            app_name="喝水助手",
            app_icon=icon_path,  # 可选：自定义图标
            timeout=10  # 通知显示10秒
        )
        print(f"[{current_time.strftime('%Y-%m-%d %H:%M:%S')}] 已发送喝水提醒")

def main():
    print("喝水提醒程序已启动...")
    print("将在下午2点到7点之间每小时提醒您喝水")
    
    # 设置每小时执行一次
    schedule.every().hour.at(":00").do(show_notification)
    
    # 程序启动时立即检查是否需要显示通知
    show_notification()
    
    # 无限循环，保持程序运行
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n程序已停止")
        sys.exit(0)

if __name__ == "__main__":
    main() 