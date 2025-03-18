@echo off
echo 正在启动喝水提醒程序（图形界面版）...
start /min pythonw drink_water_reminder_gui.py
echo 程序已在后台运行，可以关闭此窗口。
echo 喝水提醒程序会在系统托盘区域运行，您可以在那里找到它。
echo 如需停止程序，请在任务栏图标上右键选择退出。
timeout /t 5 