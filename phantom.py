import sys, time
import Libs.PyObject_to_PyFile as PyFile



def DownloadBy_Selenium(site, request, login, password, CWD, ip_port):	#site = DB_Site_Link
	from init_phantom_driver import init 
	from Libs.filename_from_link import Clear
	import CookieMGR
	import time
	
	path_PJS = CWD + '\\PhantomJS\\bin\\phantomjs.exe' #path to PhantomJS

	service_args = [
		'--proxy=' + ip_port,	#	'--proxy=127.0.0.1:9999',
		#'--proxy-type=' + proxy_Type,				#	'--proxy-type=http',
		#'--ignore-ssl-errors=true'
		]
	print 'service_args =', service_args
	
	driver = init(service_args=service_args,
					#service_log_path = CWD + '\\DataToScrape' + '\\phantom.log',
					executable_path = path_PJS
					)
	
	#driver.set_page_load_timeout(7)#???????
	
	
	
	cookie_path = CWD + '\\Cookies' + '\\' + Clear(site) + '\\' +  ip_port.split(':')[0] + '.log'
	
	#driver with cookies
	driver = CookieMGR.Load(driver, site, cookie_path)
	
	#??????
	if len(driver.get_cookies()) == 0:
		print 'No cookies'
		driver.close()
		driver.quit()
		return
	
	try:
		driver.get(request)
		time.sleep(5)
		driver.get_screenshot_as_file(CWD + '\\DataToScrape' + '\\' + ip_port.split(':')[0] + '.jpg')
		print 'Request. Loaded!!!'
	except:
		print 'Could not load Request. timeout?'
	
	
			
	# find_element_by_id
	# find_element_by_name
	# find_element_by_xpath
	# find_element_by_link_text
	# find_element_by_partial_link_text
	# find_element_by_tag_name
	# find_element_by_class_name
	# find_element_by_css_selector
	
	from selenium.webdriver.common.action_chains import ActionChains
	
	# #Captcha
	# try:
		# Captcha = driver.find_element_by_class_name("recaptcha-checkbox-border")
	# except:
		# print 'not found'
	
	# #ActionChains(driver).click(Captcha).perform()
	# #time.sleep(5)
	# driver.get_screenshot_as_file(CWD + '\\DataToScrape' + '\\' + 'captcha' + '.jpg')
	# #<div class="recaptcha-checkbox-border" role="presentation"></div>
	
	'''
	from selenium.webdriver.common.action_chains import ActionChains
	
	_10_jobs = driver.find_element_by_xpath("//data-eo-select[@id='jobs-per-page']/div[@class='btn-group dropdown']/button[@class='btn btn-default dropdown-toggle']")
	ActionChains(driver).click(_10_jobs).perform()
	time.sleep(1)	
	'''	
	'''
	_50_jobs = driver.find_element_by_xpath(
	"//data-eo-select[@id='jobs-per-page']/div[@class='btn-group dropdown open']/ul[@class='eo-dropdown-menu']/li[@class='ng-scope'][3]/a[@class='ng-binding']")
	ActionChains(driver).click(_50_jobs).perform()
	time.sleep(1)
	'''	
		
	
	PageSource = driver.page_source #Unicode type (english text)
	
	
	driver.close()
	driver.quit()
	print 'exit'
	return PageSource

	



		
if __name__ == '__main__':
	import Libs.PC_or_Mobile 
	import time
	import codecs #to read/write unicode files in Python 2.6
	import Proxy.Proxy_DB_MGR
	
	CWD = Libs.PC_or_Mobile.Check_for_CWD() #checking work directory
	flag = Libs.PC_or_Mobile.Check_for_ComputerName()#checking Online or Local
	login = None
	password = None
	#site = 'https://www.google.com'
	#request = 'https://www.google.com'
	#site = 'https://www.upwork.com/o/jobs/browse/'
	#request = 'https://www.upwork.com/search/jobs/?sort=recency'
	#request = 'https://www.upwork.com/o/jobs/browse/?q=python&sort=renew_time_int%2Bdesc'
	#site = 'https://www.whatismybrowser.com/detect/what-http-headers-is-my-browser-sending'
	#request = 'https://www.whatismybrowser.com/detect/what-http-headers-is-my-browser-sending'
	#site = 'https://www.whatismybrowser.com/detect/what-is-my-ip-address'
	#request = 'https://www.whatismybrowser.com/detect/what-is-my-ip-address'
	#site = 'http://www.ya.ru'
	#request = 'http://www.ya.ru'
	
	#site = 'https://www.upwork.com'
	#request = site
	#request = 'https://www.upwork.com/freelance-jobs/'


	path_to_proxy_DB = CWD + '\\Proxy\\DB_proxy.txt'
	rating = 20 #X% - lowest rating for proxy
	Good_Proxy_List = Proxy.Proxy_DB_MGR.Read_good_proxy(rating, path_to_proxy_DB)
	print 'Good_Proxy_List: %d proxy' %(len(Good_Proxy_List))
	
	for proxy_info in Good_Proxy_List:
		#PageSource = None
		#while PageSource == None:
		ip_port = proxy_info[1] #ip:port
		print '================'
		print 'Try:', ip_port
		PageSource = DownloadBy_Selenium(site, request, login, password, CWD, ip_port)
		print 'PageSource:', type (PageSource)
		#if PageSource != None: break
		
		
	
	# logfile = CWD + '\\DataToScrape' +'\\'+ 'PhantomJS_1' + '.html'
	# SavePage = codecs.open(logfile, 'w', encoding = 'UTF-8')
	# SavePage.write(PageSource)
	# SavePage.close()
	print 'Data Saved'
		
