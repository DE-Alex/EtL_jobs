from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common import exceptions


#UserAgent double??!!

def init(*args, **kwargs):
	
	#CHROME headers
	'''
	headers = {
	'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
	'Accept-Language':'en-US;q=0.9,en;q=0.8',
	'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36',
	#'Accept-Encoding':'gzip,deflate',#!!!!BAD Encoding!!!!!!
	'Connection': 'keep-alive'
	}
	'''
	
	#FireFox Headers
	
	headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0',
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
	'Accept-Language':'en-US;q=0.9,en;q=0.8',
	'Upgrade-Insecure-Requests': '1', #NEW!
	'Connection': 'keep-alive',
	#'Accept-Encoding':'gzip,deflate' #!!!!BAD Encoding!!!!!!
	}
	
	#Google Bot
	'''
	headers = {
	'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
	'Accept-Language':'en-US;q=0.9,en;q=0.8',
	'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.96 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
	#'Accept-Encoding':'gzip,deflate',#!!!!BAD Encoding!!!!!!
	'Connection': 'keep-alive'
	}
	'''


	
	for key, value in headers.iteritems():
		webdriver.DesiredCapabilities.PHANTOMJS['phantomjs.page.customHeaders.{}'.format(key)] = value
	

	#Mobile UserAgent 
	#webdriver.DesiredCapabilities.PHANTOMJS['phantomjs.page.settings.userAgent'] = 'Mozilla/5.0 (Linux; Android 6.0.1; Redmi 4 Build/MMB29M) AppleWebKit/537.36 Chrome/66.0.3359.126 Mobile Safari/537.36'
	
	#PC User Agent
	#webdriver.DesiredCapabilities.PHANTOMJS['phantomjs.page.settings.userAgent'] = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'
	
	print 'driver activated'
	driver =  webdriver.PhantomJS(*args, **kwargs)
	
	#driver.set_window_size(1400,1000) #window size
	
	return driver


if __name__ == '__main__':
	from selenium import webdriver
	from selenium.webdriver.common.keys import Keys
	from selenium.common import exceptions
	import time,sys
	import codecs #to read/write unicode files in Python 2.6
	
	import Libs.PC_or_Mobile 
	CWD = Libs.PC_or_Mobile.Check_for_CWD() #checking work directory
	flag = Libs.PC_or_Mobile.Check_for_ComputerName()#checking Online or Local	
	
	
	path_PJS = CWD + '\\PhantomJS\\bin\\phantomjs.exe' #path to PhantomJS

	service_args = [
		#'--proxy=127.0.0.1:9999',
		#'--proxy-type=http',
		#'--ignore-ssl-errors=true',
		#'--load-images=false', #may be reason to block by server?
		#'--debug=true',
		#'--proxy-type=none'
		]
	
	driver = init(service_args=service_args, executable_path = path_PJS)
	
	print 'Driver activated'
	if flag == 'OnLine':
		driver.get('https://www.whatismybrowser.com/detect/what-http-headers-is-my-browser-sending')
		#driver.get('https://www.ya.ru')
		#driver.get('https://www.upwork.com/o/jobs/browse/')
		for i in range (5):
			print i 
			time.sleep(1)
		
		driver.get_screenshot_as_file(CWD + '\\DataToScrape'+ '\\1.jpg')
		driver.save_screenshot(CWD + '\\DataToScrape'+ '\\2.jpg')
		
		PageSource = driver.page_source
		#print 'PageSource:', type (PageSource)
		logfile = CWD + '\\DataToScrape' +'\\'+ 'PhantomJS_init_driver' + '.html'
		SavePage = codecs.open(logfile, 'w', encoding = 'UTF-8')
		SavePage.write(PageSource)
		SavePage.close()
		driver.close()
		driver.quit()
	