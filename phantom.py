import sys, time

if sys.path[0] == '\\storage\\emulated\\0\\qpython':
	CWD = sys.path[0] + '\\projects\\parser'
else:
	CWD = sys.path[0]	

path = CWD + '\\PhantomJS\\bin\\phantomjs.exe'
	
	
print "Try Selenium"

from selenium import webdriver

webdriver.DesiredCapabilities.PHANTOMJS['phantomjs.page.settings.userAgent'] = 'Mozilla/5.0 (Linux; Android 6.0.1; Redmi 4 Build/MMB29M) AppleWebKit/537.36 Chrome/66.0.3359.126 Mobile Safari/537.36'

browser = webdriver.PhantomJS(executable_path = path)

#LoadedPage = browser.get('http://whatsmyuseragent.org')
LoadedPage = browser.get('https://whatsmyua.info')
#LoadedPage = browser.get('http://pythonscraping.com/pages/javascript/ajaxDemo.html')
#LoadedPage = browser.get('https://www.upwork.com/o/jobs/browse/?q=python&sort=renew_time_int%2Bdesc')
time.sleep(3)
PageSource = browser.page_source
print PageSource
#print(browser.find_element_by_id("content").text)

filename = CWD + '\\Save\\' + 'PhantomJS' #+ '.log'
SaveFile = open(filename, 'wb')
SaveFile.write(PageSource)
SaveFile.close()
browser.close