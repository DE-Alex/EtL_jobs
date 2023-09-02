from shutil import copyfile
import os
import subprocess

CookieSQL = r'C:\Users\User\AppData\Roaming\Mozilla\Firefox\Profiles\9abm4non.default-release\cookies.sqlite'
CookieJson = r'C:\Users\User\AppData\Roaming\Mozilla\Firefox\Profiles\9abm4non.default-release\sessionstore-backups\recovery.jsonlz4'
SaveSQL = rf'D:\Shapovalov\svoe\Python\PY\Parser5\ReloadBRSR\cookies.sqlite'
SaveJson = rf'D:\Shapovalov\svoe\Python\PY\Parser5\ReloadBRSR\recovery.jsonlz4'
err_log = 'D:\Shapovalov\svoe\Python\PY\Parser5\ReloadBRSR\error.log'

def CopyCookieFiles():
	copyfile(CookieSQL, SaveSQL)
	copyfile(CookieJson, SaveJson)
	
def ReloadBrowser():
	os.system('taskkill /im firefox.exe /f')
	copyfile(SaveSQL, CookieSQL)
	copyfile(SaveJson, CookieJson)	
	
	p = subprocess.Popen([r'C:\Program Files\Mozilla Firefox\firefox.exe'])



if __name__ == '__main__':
	#CopyCookieFiles()
	ReloadBrowser()