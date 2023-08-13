import time, random
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import JavascriptException
from selenium.common.exceptions import MoveTargetOutOfBoundsException
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains

import MyLibs.CookieMGR

#Title fragments
start_title_part = 'In-demand talent on demand.'
login_page_title = 'Log In - Upwork'
account_title_part = 'Freelancer Profile'
tech_service_title = 'Upwork - Maintenance'
Jobs_title_part = 	'Freelance Jobs'

#Instruction: !
#JS script: Google select element -> copy JS path -> document.querySelector().click()
#XPATH: Google select element -> copy XPATH path ->$x('//*[@id="jobs-per-page"]/div/ul/li[3]')
#Search (No Login)
search_expand_arrow = 'document.querySelector("#layout > nav > div > div.navbar-collapse.d-none.d-lg-flex.sticky-sublocation > div.navbar-form > form > div > div > button.dropdown-toggle.btn.p-xs-left-right").click()'
search_select_jobs = 'document.querySelector("#layout > nav > div > div.navbar-collapse.d-none.d-lg-flex.sticky-sublocation > div.navbar-form > form > div > div > ul > li:nth-child(2)").click()'
search_click = 'document.querySelector("#layout > nav > div > div.navbar-collapse.d-none.d-lg-flex.sticky-sublocation > div.navbar-form > form > div > div > button.btn.p-0-left-right").click()'
#Search after login
search_expand_arrow_log = 'document.querySelector("#nav-main > div > div > form > div > button:nth-child(3)").click()'
search_select_jobs_log = 'document.querySelector("#nav-main > div > div > form > div > ul > li.active > a").click()'
search_click_log = 'document.querySelector("#nav-main > div > div > form > div > button:nth-child(2)").click()'


#expand 50 jobs per page
jobs_expand_arrow_xpath = '/html/body/div[1]/div[2]/div/div[2]/div[2]/div/job-list-footer/footer/div[1]/div/data-eo-select/div/button'
jobs_expand_arrow = 'document.querySelector("#jobs-per-page > div > button").click()'
Jobs_50_per_page = '//*[@id="jobs-per-page"]/div/ul/li[3]'

def getPage(driver, site_domain):
	for i in range(10):
		driver.get(site_domain)
		assert driver.title != tech_service_title, 'Upwork site under maintenance.'
		if start_title_part in driver.title: return driver 
		#or change to check of visibility by some element
		else: continue
	print(f'Failed to load {site_domain}! Retry...')

def Login(driver, user_name, user_password):
	cookie = MyLibs.CookieMGR.Read()

	for i in range(4):
		try:
			driver.get('https://www.upwork.com')
			driver = MyLibs.CookieMGR.Load(driver, cookie)
			print('Cookies load - OK')
			driver.get('https://www.upwork.com/freelancers/')
			time.sleep(4)
			for i in range(60):
				if account_title_part in driver.title: return driver
				elif start_title_part in driver.title: break
				else: time.sleep(0.5)
		except TimeoutException as e:
			time.sleep(0.5)
			print(f'Error {e} intercepted')
	driver.quit()
	return False
	

def Navigate(driver):
	#===========================Search Jobs==================
	print('Navigating...')
	
	print('6')
	if account_title_part in driver.title: start_objects = [search_expand_arrow_log, search_select_jobs_log, search_click_log]
	else: start_objects = [search_expand_arrow, search_select_jobs, search_click]

	for object in start_objects:
		for i in range(50):
			try:
				driver.execute_script(object)
				time.sleep(2)
				break
			except JavascriptException as e: 
				time.sleep(0.5)
	
	print('Search button passed')
	print('7')
	#===========================50 jobs==================
	actions = ActionChains(driver)
	for i in range(50):
		try:
			time.sleep(2)
			actions.key_down(Keys.END).perform()
			time.sleep(2)
			driver.execute_script(jobs_expand_arrow)
			time.sleep(2)
			jobs_50 = driver.find_element_by_xpath(Jobs_50_per_page)
			actions.move_to_element(jobs_50).click().perform()
			break
		except JavascriptException as e:
			time.sleep(0.5)
		except NoSuchElementException as e:
			time.sleep(0.5)
		except MoveTargetOutOfBoundsException as e:
			time.sleep(0.5)
		except WebDriverException as e:
			break
	print('50 jobs button passed')
	print('8')
	actions = ActionChains(driver)
	for i in range(50):
		try:
			actions.key_down(Keys.HOME).perform()
			driver.execute_script(start_objects[0])
			time.sleep(2)
			break
		except JavascriptException as e: 
			time.sleep(0.5)
			
	path = r'D:\xxx\xxx\xxx\PY\Parser4\Cookies\https_www.upwork.com\cookies.txt'
	MyLibs.CookieMGR.Save(driver.get_cookies(), path)
	print('saved cookies')
	return driver

def F5(driver, i, url):
	print('F5: press a/key to continue')
	try:
		driver.refresh()
		time.sleep(5)
	except Exception as e: print (e)
	time.sleep(3)
	path = r'D:\xxx\xxx\xxx\PY\Parser4\Cookies\https_www.upwork.com\cookies.txt'
	MyLibs.CookieMGR.Save(driver.get_cookies(), path)
	print('saved cookies')
	return driver
	
if __name__ == '__main__':
	pass
	