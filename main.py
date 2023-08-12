import os, sys
#import requests
import PC_or_Mobile
import Input_Mod
import Folders_List_Mod
import Templates_Mod
import Download_Mod

#TODO Join Templates_Mod and Folders_List_Mod
#decrease number of objects:
#KeyList = {'Links' : Sorter[1], 'Words' : Sorter[2]}
#Folders_List = {site: folder}
#Templates_scan = {folder : (Login, Password, template_path)}


print '\n','='*20,"Starting to parse!",'='*20,'\n'
#=============Self Testing (TEMP)====================
#checking for desktop or mobile
#because of different work directory when start on PC or Mobile
CWD = PC_or_Mobile.Check_for_CWD()

#checking Online or Local	
flag = PC_or_Mobile.Check_for_ComputerName()

#checking for BIG filenames
PC_or_Mobile.Check_for_BIGNAMES(CWD)
	
#=========Input Data and Scan Folders==============
#Input URLs and key words
KeyList = Input_Mod.InputKeys(CWD)
print KeyList

#Actualization List of URL to sites and names of their folders
Folders_List = Folders_List_Mod.Folders_List(CWD)

#Reading logins, passwords, path to template for each site in Folders_List
Templates_scan = Templates_Mod.Scan(CWD, Folders_List)

#===Generate requests====
print '\n','.'*20,"Request's Generation",'.'*20,'\n'
Requests_file = open(CWD + '\\Requests.txt', 'w')

for link in KeyList['Links']:
	found = False
	for site in Folders_List:
		if site in link:
			found = True
			folder = Folders_List[site]
			print 'Site found: %s.' %(site)
			Answer = Templates_Mod.RequestFunc(folder, link, Templates_scan[folder], KeyList['Words'], Requests_file) 
			print Answer
		else:
			pass
	if found == False: 
		print 'Site not found.'	
		#TODO check words for keywords
		Answer = Templates_Mod.RequestFunc(None, link, None, KeyList['Words'], Requests_file) 
		print Answer
	
Requests_file.close()



# ====== Download Requests ======
print '\n','.'*20,'Downloading','.'*20,'\n'
Download_Mod.DownloadBy_Requests(CWD, flag)
print 'Done'

# ====== Parsing Requests ======
#print 'Parse Requests'





'''
#Downloading page by link 
SavedPages = []
for url in ULSP:
	site, login, password = ULSP[url]
	Headers = {'User-Agent':'Mozilla/5.0 (Linux; Android 6.0.1; Redmi 4 Build/MMB29M) AppleWebKit/537.36 Chrome/66.0.3359.126 Mobile Safari/537.36'}
	LoadedPage = requests.get(url, headers = Headers, auth = (login, password))
	print LoadedPage.status_code == requests.codes.ok
	print '-'*60
	print 'Save Request to file...'
	S = Save_Mod.SaveRequest(LoadedPage.content, url, CWD)
	SavedPages.append(S)
	print 'Done.'
	print '='*60	
'''



	

	

	
	



	
	
