
def Download_new_cookies(driver, site):
	import time
	try:
		driver.get(site)
		print 'Download new cookies. Waiting 7 sec...'
		time.sleep(7)
	except:
		print 'Error in function Download_new_cookies!!!!'
	
	
	import Libs.PC_or_Mobile
	CWD = Libs.PC_or_Mobile.Check_for_CWD() #checking work directory
	driver.get_screenshot_as_file(CWD + '\\DataToScrape\\111.jpg')
	#print CWD + 'Cookies_NEW.jpg'
	cookies = driver.get_cookies()

	for cookie in cookies:
		if (cookie['domain'].startswith('www')) == True:
			#print cookie['name'], ' Bad Domain name found:', cookie['domain']
			cookie['domain'] = cookie['domain'].replace('www.', '.', 1)
			#print 'Repair domain name:', cookie['domain']
			
		#if ('expiry' in cookie and cookie['expiry'] < time.time()) == True:
				#print 'Old cookie found, missing:', cookie['name'], cookie['expires']
	return driver, cookies

def Load(driver, site, cookie_path):
	
	import selenium
	#from selenium.common import exceptions
	import os, datetime
	import Libs.PyObject_to_PyFile as PyFile
	
	#check for file with cookies and if it it older than 1 hour
	try:
		t = os.path.getmtime(cookie_path)
		delta = datetime.datetime.now() - datetime.datetime.fromtimestamp(t)
		if (delta.seconds // 3600) > 0: #cookies more than 60 minutes old
			#print 'Refresh old cookies'
			cookies = False
		else: cookies = True
	except:
		#print 'Cookies not found!', cookie_path
		#print 'Try to get and save cookie'	
		cookies = False
	
	#download or read cookies from file	
	if cookies == False:
		driver, cookies = Download_new_cookies(driver, site)
		if len(cookies) != 0: PyFile.Write(cookies, cookie_path)
		print 'Downloaded %d cookies' %(len(cookies))	
	else:
		cookies = PyFile.Read(cookie_path)
		print 'Read from file %d cookies' %(len(cookies)), cookie_path	
		#add cookies from file to driver
		for cookie in cookies:
			try:
				driver.add_cookie(cookie)
			except:
				print 'Cookie Error:'
				print 'Name:', cookie['name']
				print 'Domain:', cookie['domain']
	
	print 'Total %d cookies' %(len(cookies))
	
	added_cookies = driver.get_cookies()
	print 'Added %d cookies' %(len(added_cookies))
	
	#check for not loaded cookies
	if len(cookies) - len(added_cookies) != 0:
		result = []
		for cookie in cookies:
			result.append(cookie['name'])
		for cookie in added_cookies:
			if cookie['name'] in result:
				result.remove(cookie['name'])
		print 'Not loaded %d cookies:' %(len(result)), result
	
	return driver
		

def Save(driver, site, cookie_path):
	import Libs.PyObject_to_PyFile as PyFile
	cookies = driver.get_cookies()
	for cookie in cookies:
		if (cookie['domain'].startswith('www')) == True:
			cookie['domain'] = cookie['domain'].replace('www.', '.', 1)
			print 'Repair domain name:', cookie['domain']
	PyFile.Write(cookies, cookie_path)
	print 'Saved %d cookies' %(len(cookies))
	
					
			


if __name__ == '__main__':
	import time
	import Libs.PC_or_Mobile
	CWD = Libs.PC_or_Mobile.Check_for_CWD() #checking work directory
	from Libs.filename_from_link import Clear
	
	from init_phantom_driver import init
	path_PJS = CWD + '\\PhantomJS\\bin\\phantomjs.exe' #path to PhantomJS
	driver = init(executable_path = path_PJS)
	
	site = 'https://www.upwork.com'
	#site = 'https://www.yandex.ru'
	
	cookie_path = CWD + '\\Cookies' + '\\' + Clear(site) + '.log'
	
	driver_with_cookies = Load(driver, site, cookie_path)
	
	request = 'https://www.upwork.com/search/jobs/'
	driver_with_cookies.get(request)
	time.sleep(5)
	driver_with_cookies.get_screenshot_as_file(CWD + '\\DataToScrape' + '\\' + 'Finish.jpg')
	driver_with_cookies.close()
	driver_with_cookies.quit()
	print 'Complete'
	#Save(driver, site, cookie_path)
	
	