import os, time
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

if __name__ == '__main__':
	import os, sys
	
	if sys.path[0] == '\\storage\\emulated\\0\\qpython':
		CWD = sys.path[0] + '\\projects\\parser'
	else:
		CWD = sys.path[0]	
	
	if ('ComputerName' in os.environ) and (os.environ['ComputerName'] == 'OPR-5'): flag = 'Local'
	else: flag = 'OnLine'
	print 'FLAG =',flag 
	
	DownloadBy_Requests(CWD, flag)	
	