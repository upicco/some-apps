@echo off
echo 正在启动喝水提醒程序...
start /min pythonw drink_water_reminder.py
echo 程序已在后台运行，可以关闭此窗口。
echo 如需停止程序，请使用任务管理器结束Python进程。
timeout /t 5 