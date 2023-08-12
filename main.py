import os, sys
import codecs #to read/write unicode files in Python 2.6
#import requests
import Input_Mod
import Request_Mod
import Download_Mod
import phantom
import Proxy.Proxy_DB_MGR
import Parsing
import csv
import Libs.SQLite as SQLite

print '\n','='*20,"Starting!",'='*20,'\n'

#=============Self Testing (TEMP)====================
import Libs.PC_or_Mobile 
CWD = Libs.PC_or_Mobile.Check_for_CWD() #checking work directory
flag = Libs.PC_or_Mobile.Check_for_ComputerName()#checking Online or Local	

#=============Basic Preferences====================
Templ_path = '\\data\\Templates'#Folder to import templates from
print Templ_path
DBpath = CWD + '\\data\\DB.csv' #Data Base - sites and passwords
SQLbase = CWD + '\\data\\SQLbase' #Upwork jobs
ProxyPath = CWD + '\\Proxy\\Proxy.csv'#ProxyList

#=========Input Data and Read DataBase ==============
#connecting DB

#Input URLs and key words
KeyList = Input_Mod.InputKeys(CWD)

#Reading DataBase: logins, passwords, templates
from Libs.CSV_read_and_write import CSV_Read
print 'Reading data from', DBpath 
DBraw = CSV_Read(DBpath)#Data in lists

#transforming data from lists to dictionary
# DB = {Site: {'Login': 'log', 'Password':'pass', 'Link':'https://www', 'Template':'True/False'}}
DB = {}
Titles = DBraw[0][1:]

for line in DBraw[1:]:
	DB[line[0]] = {} #SiteName
	for (title,data) in zip(Titles,line[1:]):
		DB[line[0]][title] = data

for site in DB:
	print site, ':', DB[site]


	
#===Generate requests====
print '\n','.'*20,"Request's Generation",'.'*20,'\n'
Requests_file = open(CWD + '\\Requests.txt', 'w')

for link in KeyList['Links']:
	found = False
	for Site in DB:
		if DB[Site]['Link'] in link:
			found = True
			print 'Site found: %s.' %(Site)
			login, password = DB[Site]['Login'], DB[Site]['Password']
			if DB[Site]['Template'] == 'True': 
				Template_path = Templ_path + '\\' + Site
				print Template_path
			else: 
				Template_path = False
			Answer = Request_Mod.RequestGen(link, login, password, Template_path, KeyList['Words'], Requests_file) 
			print Answer
		else:
			pass
	if found == False: 
		print 'Site not found.'	
		#TODO check words for keywords
		Answer = Request_Mod.RequestGen(link, None, None, None, KeyList['Words'], Requests_file) 
		print Answer
	
Requests_file.close()


# ====== Download Requests ======
print '\n','.'*20,'Downloading','.'*20,'\n'

path_to_proxy_DB = CWD + '\\Proxy\\DB_proxy.txt'
rating = 80 #80% - lowest rating for proxy
Good_Proxy_List = Proxy.Proxy_DB_MGR.Read_good_proxy(rating, path_to_proxy_DB)
print 'Good_Proxy_List', Good_Proxy_List
	
Requests_file = open(CWD + '\\Requests.txt')

for oneline in Requests_file:
	oneline = oneline.rstrip()  #kill \n symbol 
	link, keywords, request = oneline.split()
	
	found = False
	for Site in DB:
		if DB[Site]['Link'] in link:
			found = True
			print 'Site found: %s.' %(Site)
			login, password, DB_Site_Link = DB[Site]['Login'], DB[Site]['Password'], DB[Site]['Link']
		else:
			login, password = None, None
	
	if flag == 'OnLine':
		print "Try Selenium:"
		for proxy_info in Good_Proxy_List:
			ip_port = proxy_info[1] #ip:port
			PageSource = phantom.DownloadBy_Selenium(DB_Site_Link, request, login, password, CWD, ip_port)
	else: PageSource = 'No Source. flag != OnLine'
	
			
	logfile = CWD + '\\DataToScrape' +'\\'+ keywords + '.html'
	SavePage = codecs.open(logfile, 'w', encoding = 'UTF-8')
	try:
		SavePage.write(PageSource)
	except TypeError:
		if PageSource == None:
			PageSource = 'No Data Scraped'
			SavePage.write(PageSource)
	SavePage.close()
	print 'Data Saved'

Requests_file.close()
	
print 'Download by Requests Done'

# ====== Parsing Requests ======
print 'Parse Requests'
SQL = SQLite.connect(SQLbase)#connecting...

from Libs.files_in_folder import Abs_filenames
for filename in Abs_filenames(CWD + '\\DataToScrape'):
	if filename[-4:] == 'html':
		print filename
		#ReadFile = codecs.open(filename, encoding = 'UTF-8')
		ReadFile = codecs.open(filename, encoding = 'cp866')#!!!!!  Change!!!!
		PageSource = ReadFile.read()
		
		Job_str = Parsing.Soup(PageSource)

		#converting string Job_str (format JSON) to Python objects
		import json
		Jobs_obj = json.loads(Job_str, encoding = 'utf-8')
		print 'Jobs list (JSON) to PyObj - Ok'
		#TODO = Saving Python objects to SQLbase (sqlite3)
		
		#Saving Python objects to CSV
		csvFile = open(CWD + '\\data\\data.csv', 'ab')
		for job in Jobs_obj:
			csv_row = [v for k,v in job.items()]
			writer = csv.writer(csvFile, delimiter = ';')
			writer.writerow(csv_row)
		csvFile.close()
		print 'Add OK'
		
		#Saving Python objects to JSON
		# SaveDataToFile = open(CWD + '\\data\\data.json', 'w')
		# json.dump(Jobs_obj, SaveDataToFile)
		# SaveDataToFile.close()

SQL.close	#closing...
	