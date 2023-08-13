
def Login(driver, cookie_path):
	import time, random
	from selenium.webdriver.common.keys import Keys
	from selenium.common.exceptions import NoSuchElementException
		
	user_name = 'xxxx'
	user_password = 'xxxxx'
	loginpage = 'https://www.upwork.com/ab/account-security/login'
	Login_input = '//*[@id="username_username"]'
	Password_input = '//*[@id="password_password"]'
	exclamation = 'Due to technical difficulties we are unable to process your request. Please try again later'
	
	
	print('Go to login page.')
	for i in range(100):
		driver.get(loginpage)
		for i in range(100):
			try:
				Login = driver.find_element_by_xpath(Login_input)
				break
			except NoSuchElementException as e: time.sleep(0.5)
		Login.clear()
		Login.send_keys(user_name)
		time.sleep(random.uniform(1,2))
		Login.send_keys(Keys.RETURN)
		time.sleep(random.uniform(4,5))
		for i in range(100):
			try:
				Password = driver.find_element_by_xpath(Password_input)
				break
			except NoSuchElementException as e:
				time.sleep(0.5)
		Password.clear()
		Password.send_keys(user_password)
		time.sleep(random.uniform(1,2))
		Password.send_keys(Keys.RETURN)
		time.sleep(random.uniform(4,5))
		for i in range(100):
			if 'Upwork Freelancer' in driver.title:
				print('Log in successful!')
				return driver
			else:
				time.sleep(0.5)
	
	print('Log failed!')	
	input('pause')





def Load(driver, site, cookie_path):
	import os, datetime, time
	import MyLibs.PyObject_to_PyFile as PyFile
	
	driver = Login(driver, cookie_path)

	Save(driver.get_cookies(), cookie_path)
	#check for file with cookies and if it it older than 1 hour
	try:
		t = os.path.getmtime(cookie_path)
		delta = datetime.datetime.now() - datetime.datetime.fromtimestamp(t)
		if (delta.seconds // 3600) > 0: #cookies more than 60 minutes old
			cookies = False
		else: cookies = True
	except:
		print(f'Cookies not found!({cookie_path}) Try to get and save cookie')
		cookies = False
	
	if cookies == False:
		
		#Download new cookies
		try:
			driver.get(site)
			print('Download new cookies. Waiting ...')
			#time.sleep(7)
		except:
			print('Error in function Download_new_cookies!!!!')
		cookies = driver.get_cookies()
		print('Loaded %d cookies' %(len(cookies)))
		if len(cookies) != 0: Save(cookies, cookie_path)
	else:
		cookies = PyFile.Read(cookie_path)
		print('Read from file %d cookies' %(len(cookies)), cookie_path)
		
		#add cookies from file to driver
		driver.get(site)
		driver.delete_all_cookies()
		for cookie in cookies:
			try: driver.add_cookie(cookie)
			except Exception as e: print(e)
	
		added_cookies = driver.get_cookies()
		print('Added %d cookies' %(len(added_cookies)))
	
		#check for not loaded cookies
		if len(cookies) - len(added_cookies) != 0:
			result = []
			for cookie in cookies:
				result.append(cookie['name'])
			for cookie in added_cookies:
				if cookie['name'] in result:
					result.remove(cookie['name'])
			print('Not loaded %d cookies:' %(len(result)), result)
	
	return driver
		
def Save(cookies, cookie_path):
	import MyLibs.PyObject_to_PyFile as PyFile
	
	for cookie in cookies:
		#check for invalid name 'expiry'. It should be 'expires'
		if cookie.get('expiry', None) is not None:
			cookie['expires'] = cookie.pop('expiry')
	PyFile.Write(cookies, cookie_path)
	print('Saved %d cookies' %(len(cookies)))
	
					
			


if __name__ == '__main__':
	import time
	import MyLibs.PC_or_Mobile
	CWD = MyLibs.PC_or_Mobile.Check_for_CWD() #checking work directory
	CWD = MyLibs.PC_or_Mobile.Check_for_CWD() #checking work directory
	from MyLibs.filename_from_link import Clear
	
	from MyLibs.init_web_driver import Chrome
	
	executable_path = CWD + '\\WebDriver\\Chrome\\chromedriver.exe' #path to webdriver
	
	UserAgent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0'
	headless = False
	ip_port = '148.217.94.54:3128'
	proxy = False
	driver = Chrome(UserAgent, proxy, headless)
	
	site = 'https://www.upwork.com'
	request = site
	cookie_path = CWD + '\\Cookies' + '\\' + Clear(site) + '\\' +  ip_port.split(':')[0] + '.log'
	
	driver_with_cookies = Load(driver, site, cookie_path)
	

	driver_with_cookies.get(request)
	time.sleep(5)
	driver_with_cookies.get_screenshot_as_file(CWD + '\\DataToScrape' + '\\' + 'Finish.png')
	driver_with_cookies.close()
	driver_with_cookies.quit()
	print('Complete')

	
	