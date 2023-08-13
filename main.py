import os, sys
import codecs #to read/write unicode files in Python 2.6
import Input_Mod
import WebDriver
import Proxy.Proxy_DB_MGR

import csv
import MyLibs.SQLite as SQLite

print('\n','='*20,"Starting!",'='*20,'\n')

#=============Self Testing (TEMP)====================
import MyLibs.PC_or_Mobile 
CWD = MyLibs.PC_or_Mobile.Check_for_CWD() #checking work directory
flag = MyLibs.PC_or_Mobile.Check_for_ComputerName()#checking Online or Local	

#=============Basic Preferences====================
Templ_path = '\\data\\Templates'#Folder to import templates from
print('Templ_path:', Templ_path)
DBpath = CWD + '\\data\\DB.csv' #Data Base - sites and passwords
SQLbase = CWD + '\\data\\SQLbase' #Upwork jobs
ProxyPath = CWD + '\\Proxy\\Proxy.csv'#ProxyList

#=========Input Data and Read DataBase ==============
#connecting DB

#Input URLs and key words
KeyList = Input_Mod.InputKeys(CWD)

#Reading DataBase: logins, passwords, templates
from MyLibs.CSV_read_and_write import CSV_Read
print('Reading data from', DBpath)
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
	print(site, ':', DB[site])
	
# ====== Download Requests ======
print('\n','.'*20,'Downloading','.'*20,'\n')

path_to_proxy_DB = CWD + '\\Proxy\\DB_proxy.txt'
rating = 80 #80% - lowest rating for proxy
Good_Proxy_List = Proxy.Proxy_DB_MGR.Read_good_proxy(rating, path_to_proxy_DB)
print('Good_Proxy_List', Good_Proxy_List)
	
Requests_file = open(CWD + '\\Requests.txt')

for oneline in Requests_file:
	oneline = oneline.rstrip()  #kill \n symbol 
	link, keywords, request = oneline.split()
	
	found = False
	for Site in DB:
		if DB[Site]['Link'] in link:
			found = True
			print('Site found: %s.' %(Site))
			login, password, DB_Site_Link = DB[Site]['Login'], DB[Site]['Password'], DB[Site]['Link']
		else:
			login, password = None, None
	
	if flag == 'OnLine':
		print("Try Selenium:")
		for proxy_info in Good_Proxy_List:
			ip_port = proxy_info[1] #ip:port
			PageSource = WebDriver.DownloadBy_Selenium(DB_Site_Link, request, login, password, CWD, ip_port)
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
	print('Data Saved')

Requests_file.close()
	
print('Download by Requests Done')


	