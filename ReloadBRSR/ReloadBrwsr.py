import os, time, sys
import subprocess
import MyLibs.Time

import MyLibs.AutoGUI
#Mozilla:
#Refresh browser page: F5 / Ctrl + R
#Refresh browser page (without cashe): Ctrl + F5 / Ctrl + Shift + R

err_log = 'D:\Shapovalov\svoe\Python\PY\Parser5\ReloadBRSR\error.log'

if __name__ == '__main__':
	print('start')
	os.system('taskkill /im firefox.exe /f')

	
	print('Press Ctrl-C to quit.')
	p = subprocess.Popen([r'C:\Program Files\Mozilla Firefox\firefox.exe'])#, '-headless'])
	#p = subprocess.Popen([r'C:\Program Files\Mozilla Firefox\firefox.exe'])#, 'https://www.upwork.com/nx/jobs/search/?sort=recency&user_location_match=2']) 
	i = 0
	while True:
		try:
			i += 1
			time.sleep(5)
			x, y = MyLibs.AutoGUI.MousePos()
			MyLibs.AutoGUI.Click(-1892, 1026)
			MyLibs.AutoGUI.HotKeys('ctrl', 'f5')
			MyLibs.AutoGUI.MoveTo(x, y)
			now = MyLibs.Time.now_local()
			now2= MyLibs.Time.datetime_to_str(now, "%H:%M %d-%m-%Y")
			print(f'({i}){now2}: Reload')
			for t in range(600): time.sleep(1) #10 minutes
		except KeyboardInterrupt:
			os.system('taskkill /im firefox.exe /f')
			sys.exit(0)
		except Exception as e:
			time = MyLibs.Time.datetime_to_str(MyLibs.Time.now_local(), '%d.%m.%Y %H.%M')
			with open(err_log, 'a') as file: 
				file.write(time + '\n' + str(e) + '\n')
			
