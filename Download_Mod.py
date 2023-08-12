import time
import requests
	
def SaveContentToFile(CWD, PageContent, link, wordslist):
	#TODO organize DB for a large ammount of data
	clear_link = link
	for letter in ['://','/','\\',':','*','?','"','>','<','|']:
		if letter in clear_link: clear_link = clear_link.replace(letter,'_')
	filename = CWD + '\\Save\\' + clear_link + '(' + wordslist + ')' + '.log'
	SaveFile = open(filename, 'w')
	SaveFile.write(PageContent)
	SaveFile.close()
	return filename
	
'''
def init_phantomjs_driver(*args, kwargs):
	#=========PhantomJS properties===========
	headers = {
	#'Accept':'text/html, application/xhtml+xml, application/xml; q=0.9, */*; q=0.8',
	#'Accept-Language':'zh-CN, zh; q=0.8, en-US; q=0.5, en; q=0.3',
	'User-Agent':'Mozilla/5.0 (Linux; Android 6.0.1; Redmi 4 Build/MMB29M) AppleWebKit/537.36 Chrome/66.0.3359.126 Mobile Safari/537.36'
	#,
	#'Connection': 'keep-alive'
	}	
	for key, value in headers.iteritems():
		webdriver.DesiredCapabilities.PHANTOMJS['phantomjs.page.customHeaders.{}'.format(key)] = value
	#userAgent is set in phantomjs.page.settings.userAgent (!!)
	webdriver.DesiredCapabilities.PHANTOMJS['phantomjs.page.settings.userAgent'] = 'Mozilla/5.0 (Linux; Android 6.0.1; Redmi 4 Build/MMB29M) AppleWebKit/537.36 Chrome/66.0.3359.126 Mobile Safari/537.36'
	browser = webdriver.PhantomJS(*args, **kwargs)
	#browser.set_window_size(1400,1000)
'''
		
def DownloadBy_Selenium(CWD, flag):
	Requests_file = open(CWD + '\\Requests.txt')
	Downloads_file = open(CWD + '\\Downloads.txt', 'w') #List of sucessful downloads
	
	#TODO import User-Agent from User_Agent_Mod
	print "Try Selenium"
	from selenium import webdriver
	
	webdriver.DesiredCapabilities.PHANTOMJS['phantomjs.page.settings.userAgent'] = 'Mozilla/5.0 (Linux; Android 6.0.1; Redmi 4 Build/MMB29M) AppleWebKit/537.36 Chrome/66.0.3359.126 Mobile Safari/537.36'
	
	#service_args = [
		#'--proxy=127.0.0.1:9999',
		#'--proxy-type=http',
		#'--ignore-ssl-errors=true'
	#	]
	#browser = init_phantomjs_driver(service_args=service_args)
	
	browser = webdriver.PhantomJS(executable_path='?????')
				
	for line in Requests_file:
		print 'Loading...'
		line = line.rstrip()  #kill \n symbol 
		link, wordslist, Request, Login, Password = line.split('\t')
		
		if flag == 'Online':
			if (Login == 'None') or (Password == 'None'):
				#TO_Think - what to do if we have only 1 of pass or login?
				LoadedPage = browser.get(Request) 
			else:
				LoadedPage = browser.get(Request) # auth = (Login, Password))
			time.sleep(3)
			#script to scroll down the page (Firefox)
			#browser.execute_script("window.scrollTo(0,document.body.scrollHeight); var len0fPage=document.body.scrollHeight; return len0fPage;")
			#time.sleep(10)
			
			#print LoadedPage.status_code == requests.codes.ok ??
			PageContent = browser.find_element_by_id("content").text
		else:
			PageContent = 'Page Content'
			
		print 'Saving...\n'
		filename = SaveContentToFile(CWD, PageContent, link, wordslist)
		Downloads_file.write(link +'\t'+ wordslist +'\t'+ filename + '\n')
		
	browser.close()
	Requests_file.close()
	Downloads_file.close()
				

		
		#Chrome
		# print "Try 2"
		# from selenium import webdriver
		# from selenium.webdriver.Chrome.options import Options
		# opts = Options()#??
		# opts.set_headless()#???
		# assert opts.headless #headless mode
		# opts.add_argument('user-agent = Mozilla/5.0 (Linux; Android 6.0.1; Redmi 4 Build/MMB29M) AppleWebKit/537.36 Chrome/66.0.3359.126 Mobile Safari/537.36')
		
		#browser = webdriver.Chrome(chrome_options = opts) #(executable_path = 'Path/to/driver/chromedriver')
		
		#browser.get('http://ya.ru')
		
				#How to get user Agent from Chrome
				#agent = browser.execute_script('return navigator.userAgent')
		#browser.close()
		
		
def DownloadBy_Requests(CWD, flag):
	#TODO import User-Agent from User_Agent_Mod
	Headers = {'User-Agent':'Mozilla/5.0 (Linux; Android 6.0.1; Redmi 4 Build/MMB29M) AppleWebKit/537.36 Chrome/66.0.3359.126 Mobile Safari/537.36'}
	
	Requests_file = open(CWD + '\\Requests.txt')
	Downloads_file = open(CWD + '\\Downloads.txt', 'w') #List of sucessful downloads
		
	for line in Requests_file:
		print 'Loading...'
		line = line.rstrip()  #kill \n symbol 
		link, wordslist, Request, Login, Password = line.split('\t')
		
		if flag == 'Online':
			if (Login == 'None') or (Password == 'None'):
				#TO_Think - what to do if we have only 1 of pass or login?
				LoadedPage = requests.get(Request, headers = Headers)
			else:
				LoadedPage = requests.get(Request, headers = Headers, auth = (Login, Password))
			
			time.sleep(3)
			print LoadedPage.status_code == requests.codes.ok
			PageContent = LoadedPage.content
		else:
			PageContent = 'Page Content'
			
		print 'Saving...\n'
		filename = SaveContentToFile(CWD, PageContent, link, wordslist)
		Downloads_file.write(link +'\t'+ wordslist +'\t'+ filename + '\n')
		
	Requests_file.close()
	Downloads_file.close()

def DownloadBy_API():
	#Making API requests
	#=================
	#Inspect web page to find HTTP request details (find search file in Inspector and Request URL)
	#(take in attention of headers or security tokens need)
	#make GET request using python (or browser or any REST client)
	import json
	url = 'url to request'
	response = urllib.request.urlopen(url)
	jresponse = json.load(response)

	with open('filename.json', 'w') as outfile:
		json.dump(jresponse, outfile, sort_keys = True, intent = 4)
#=========================================================================	

if __name__ == '__main__':
	import Libs.PC_or_Mobile 
	CWD = Libs.PC_or_Mobile.Check_for_CWD() #checking work directory
	flag = Libs.PC_or_Mobile.Check_for_ComputerName()#checking Online or Local	

	
	DownloadBy_Requests(CWD, flag)	
	print 'Done'
	