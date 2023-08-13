import sys, time
import os
import datetime
import MyLibs.PyObject_to_PyFile as PyFile
import requests
import pickle
import json
import Requests_Gen_Upwork
import DB_Manager_Upwork
from MyLibs.init_web_driver import FireFox

def DownloadBy_Selenium(site, request, login, password, CWD, proxy_port, UserAgent):	
	from MyLibs.init_web_driver import FireFox
	from MyLibs.Link_to_Filename import Clear
	import CookieMGR
	import time
	from MyLibs.my_IP import IP_check
	from MyLibs.requests_by_URL import Get_request
	from selenium.common.exceptions import NoSuchElementException
	
	# SELF IP CHECK
	my_IP = IP_check(proxy_port)
	my_IP_log = PyFile.Read(sys.path[0] + '\\Proxy\\my_IP.log')
	if my_IP in my_IP_log.keys(): my_IP_log[my_IP] = my_IP_log[my_IP] + 1
	else: my_IP_log[my_IP] = 1
	PyFile.Write(my_IP_log, sys.path[0] + '\\Proxy\\my_IP.log')
	
	print('================')
	print(f'Try:{my_IP}. It will be used {my_IP_log[my_IP]} time(s).')
	
	cookie_path = sys.path[0] + '\\Cookies' + '\\' + Clear(site) + '\\' +  my_IP + '.log'
		
	headless = False
	
	import MyLibs.Change_UserAgent as UA
	UA.write_in(UserAgent)
	print('User-Agent updated')
	driver = FireFox(proxy_port, headless)
	
	
	
	#driver with cookies
	driver = CookieMGR.Load(driver, site, cookie_path)
	try:
		driver.get(request)
		driver.maximize_window()
		time.sleep(5)
		driver.get_screenshot_as_file(CWD + '\\DataToScrape' + '\\' + proxy_port.split(':')[0] + '.png')
		print('Request. Loaded!!!')
	except:
		print('Could not load Request. timeout?')
	
	print(f'Cookies after request:{len(driver.get_cookies())}')
	
	if 'upwork' in driver.current_url:
		from selenium.webdriver.common.action_chains import ActionChains
		from selenium.webdriver.support.ui import WebDriverWait
		from selenium.webdriver.common.keys import Keys
		from selenium.webdriver.support import expected_conditions as EC
		from selenium.webdriver.common.by import By
		from selenium.webdriver.support.ui import Select
		from selenium.webdriver.support import expected_conditions as EC
	
		#Instruction: !
		#JS script: Google select element -> copy JS path -> document.querySelector().click()
		#XPATH: Google select element -> copy XPATH path ->$x('//*[@id="jobs-per-page"]/div/ul/li[3]')
		#Search
		search_expand_arrow = 'document.querySelector("#layout > nav > div > div.navbar-collapse.d-none.d-lg-flex.sticky-sublocation > div.navbar-form > form > div > div > button.dropdown-toggle.btn.p-xs-left-right").click()'
		search_select_jobs = 'document.querySelector("#layout > nav > div > div.navbar-collapse.d-none.d-lg-flex.sticky-sublocation > div.navbar-form > form > div > div > ul > li:nth-child(2)").click()'
		search_click = 'document.querySelector("#layout > nav > div > div.navbar-collapse.d-none.d-lg-flex.sticky-sublocation > div.navbar-form > form > div > div > button.btn.p-0-left-right").click()'
		#Search after login
		search_after_login = 'document.querySelector("#nav-main > div > div > form > div > button:nth-child(1)").click()'
				
		#expand 50 jobs per page
		jobs_expand_arrow = 'document.querySelector("#jobs-per-page > div > button").click()'
		Jobs_50_per_page = '//*[@id="jobs-per-page"]/div/ul/li[3]'
		
			
		if 'Upwork Freelancer' in driver.title:
			print('login success, start to search')
			Auth = 'ab/jobs/search/'#correct to request links after login
			
			start_objects = [search_after_login]
		else:
			print('No login,  start to search')
			Auth = 'search/jobs/'
			start_objects = [search_expand_arrow, search_select_jobs, search_click]
		
		try:
			for object in start_objects:
				driver.execute_script(object)
				print('Ok')
				time.sleep(2)
		except Exception as e: 
			print('Error')
			print (e)
		
		#===========================50 jobs==================
		actions = ActionChains(driver)
		for i in range(100):
			try:
				actions.key_down(Keys.END).perform()
				footer = driver.find_element_by_xpath(Jobs_50_per_page)
				print('Jobs')
				break
			except NoSuchElementException as e:
				time.sleep(2)
				
		try:
			jobs_50 = driver.find_element_by_xpath(Jobs_50_per_page)
		except NoSuchElementException as e:
			print('No "50jobs" element. PageUp')
			actions.key_down(Keys.PAGE_UP).perform()
			time.sleep(1)
		
		try:
			driver.execute_script(jobs_expand_arrow)
			time.sleep(1)
			jobs_50 = driver.find_element_by_xpath(Jobs_50_per_page)
			actions.move_to_element(jobs_50).perform()
			actions.click(jobs_50).perform()
		except Exception as e: 
			print('Error')
			print (e)
		
		time.sleep(5)
		driver.get_screenshot_as_file(CWD + '\\DataToScrape' + '\\' + 'jobs_50.png')
		
		CookieMGR.Save(driver.get_cookies(), cookie_path)
		
		input('Press any key')
		
		cookies = driver.get_cookies()
		print('len cookies', len(cookies))
					
		HomePage = f'https://www.upwork.com/{Auth}'
		First_request = f'https://www.upwork.com/{Auth}url?page=3&per_page=10&sort=recency'
		print(HomePage)
		print(First_request)
		req = Get_request(First_request, HomePage, UserAgent, cookies, proxy_port)
		json_PyObj = req.json()#request decode Json_data to Python obj with build in .json() method
		HomePage = First_request
		HomePage, requests_List = Requests_Gen_Upwork.Jobs(json_PyObj, Auth, HomePage, UserAgent, cookies, proxy_port) #counts jobs in facets and generate requests
		
		db = DB_Manager_Upwork.Connect_Upwork_DB()
		
		i = 0
		N = 50 #reload cookies frequency
		for url in requests_List:   #while len(requests_List) != 0?
			time.sleep(3)
			req = Get_request(url, HomePage, UserAgent, cookies, proxy_port)
			i = i+1
			Status = req.status_code
			if Status == requests.codes.ok: print(f'{i} - OK ({url})')			
			if i%N == 0 or Status == 403:
				#====F5=========
				try:
					actions = ActionChains(driver)
					actions.key_down(Keys.F5).perform()
					actions.pause(5).perform()
					driver.get_screenshot_as_file(CWD + f'\\DataToScrape\\F5_{i}.png')
				except Exception as e: 
					print('Error')
					print (e)
				#====Driver.GET(url)=========
				url_without_Per_Page = url.replace('per_page=50','')
				driver.get(url_without_Per_Page)
				time.sleep(3)
				driver.get_screenshot_as_file(CWD + f'\\DataToScrape\\request_{i}.png')
				
				cookies = driver.get_cookies()
				CookieMGR.Save(cookies, cookie_path)
				
				req = Get_request(url, HomePage, UserAgent, cookies, proxy_port)
			
			HomePage = url

			json_data = req.json()
			today = datetime.datetime.strftime(datetime.datetime.now(),'%d_%m_%Y')
			filename = f'D:\\xxx\\xxx\\xxx\\PY\\Raw_Jsons\\{today}\\{i}.json'
			directory = os.path.dirname(filename)
			if not os.path.exists(directory): os.makedirs(directory)		
			with open(filename, 'w') as f: json.dump(json_data, f)
			
		db.close()
		driver.get_screenshot_as_file(CWD + '\\DataToScrape' + '\\' + 'json.png')
	input('Press any key')
	
	print(driver.title)
	CookieMGR.Save(driver.get_cookies(), cookie_path)
	return driver

		
if __name__ == '__main__':
	import MyLibs.PC_or_Mobile 
	import time
	import codecs #to read/write unicode files in Python 2.6
	import random
	
	CWD = MyLibs.PC_or_Mobile.Check_for_CWD() #checking work directory
	flag = MyLibs.PC_or_Mobile.Check_for_ComputerName()#checking Online or Local
	login = None
	password = None
	site = 'https://www.upwork.com'
	request = site
	
	path_to_UserAgent_DB = r'D:\xxx\xxx\xxx\PY\MyLibs\UserAgents\UserAgents.txt'
	UserAgent_List = []
	file = open(path_to_UserAgent_DB)
	for line in file:
		line = line.rstrip()  #kill \n symbol 
		UserAgent_List.append(line)
		
	print(f'Total UserAgent loaded:{len(UserAgent_List)}')

	proxy_port = '127.0.0.1:35685'#mitmproxy(local network)
	UserAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0'

	driver = DownloadBy_Selenium(site, request, login, password, CWD, proxy_port, UserAgent)
		
	driver.quit()

	print('Data Saved')
	print('exit')	