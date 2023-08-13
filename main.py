import os, sys, time, random
import json
from datetime import datetime, timedelta
import traceback

from MyLibs.my_IP import IP_log
from MyLibs.Link_to_Filename import Clear
from MyLibs.UserAgent_Manager import UA_get
from MyLibs.init_web_driver import FireFox
from MyLibs.SQLite import BackUp
from MyLibs.SQLite import connect
import MyLibs.PyObject_to_PyFile as PyFile
from MyLibs.Time import *
from MyLibs.Dinamic_import_module_by_path import Import_by_path

from Upwork_requests import *
import DB_Manager_Upwork

#======Init BROWSER=======
def Init_browser():
	Count = 0
	while True:
		driver = FireFox(proxy, headless)
		#driver.maximize_window()
		
		start = time.time()
		if Account == False:
			print("getPage in...")
			driver = Site_MGR.getPage(driver, site_domain)
		else:
			print(f"Login in...")
			driver = Site_MGR.Login(driver, login, password)
		if driver == False:
			Count += 1
			print(f"...failed. Retry {Count}")
			continue

		print(f"{round((time.time() - start),1)}s")
		start = time.time()
		driver = Site_MGR.Navigate(driver)
		print(f"Navigate in:{round((time.time() - start),1)}s")
		HomePage = driver.current_url
		return driver, HomePage
	
def Desision(HomePage, driver):
	requests_List = PyFile.Read(requestsList_log)
	if requests_List == None or len(requests_List) == 0:
		print(f'Desision: ', end=' ')
		url = f'https://www.upwork.com/{auth}url?page={99}&per_page=50&sort=recency'
		req = Get(url, HomePage, UserAgent, driver.get_cookies(), proxy)
		i = 0
		while req == False:
			i += 1
			print(f'{i} - Failed ({url})\nRelogin...')
			driver.quit()
			driver, HomePage = Init_browser()
			time.sleep(random.uniform(1,4))
			req = Get(url, HomePage, UserAgent, driver.get_cookies(), proxy)
			
		HomePage = url
		json_data = req.json()
		Jobs = DB_Manager_Upwork.clear_Upwork_data(json_data)
		Jobs = DB_Manager_Upwork.Downgrade(Jobs)
		
		count = 0
		for job in Jobs:
			date_List = [datetime.fromisoformat(rec) for rec in [job['createdOn'], job['publishedOn'], job['renewedOn']] if rec != None]
			for date in date_List:
				if date < checkpoint - check*5: pass #decision to Check or Full_Update
				elif date >= checkpoint - check*5: count += 1 #decision to Check or Full_Update
		if count == 0:
			print(f'CheckRecent.')
			requests_List = [[req_Generator(i, auth) for i in range(1,100)]]
		else:
			print(f'FullUpdate.')
			HomePage, requests_List = List(json_data, auth, HomePage, UserAgent, driver.get_cookies(), proxy) #counts jobs in facets and generate requests
	else: print('Requests_List found.')
	driver, HomePage = Download(HomePage, requests_List, driver)
	return driver, HomePage

def Download(HomePage, requests_List, driver):
	try:
		Len_requestsList = sum([len(list) for list in requests_List])
		print(f'Requests to download: {Len_requestsList}')
		#=====Logs============
		start_check_str = datetime_to_str(now_local(), '%d.%m.%Y %H.%M')
		#with open(logfile, 'a') as file: file.write(f'Update start: {start_check_str}\n')
		PyFile.Write(requests_List, requestsList_log)
		print('requestsList_log')
		#======Download requests=======
		i = 0
		N = 100 #reload cookies frequency
		result = {'insert': 0, 'update': 0}
		start = time.time()
		for requests in requests_List:
			while len(requests) !=0:
				Len_requestsList = sum([len(list) for list in requests_List])
				try:
					url = requests[0]
					time.sleep(random.uniform(1,4))
					i = i+1
				
					try:
						req = Get(url, HomePage, UserAgent, driver.get_cookies(), proxy)
					except Exception as e:
						print('==================5')
						import sys
						_, _, exc_tb = sys.exc_info() #exc_type, exc_obj, exc_tb
						print(f"error in line:{exc_tb.tb_lineno}\n{e}\n")
						input('Press any key')
				
					HomePage = url
					while req == False:
						print(f'{Len_requestsList} - Failed ({url})\nRelogin...')
						driver.quit()
						driver, HomePage = Init_browser()
						time.sleep(random.uniform(1,4))
						req = Get(url, HomePage, UserAgent, driver.get_cookies(), proxy)
					
					del requests[0]
					print(f'{Len_requestsList} - OK', end=' ')
					PyFile.Write(requests_List, requestsList_log)
					
					json_data = req.json()
				
					Jobs = DB_Manager_Upwork.clear_Upwork_data(json_data)
					Jobs = DB_Manager_Upwork.Downgrade(Jobs)
					assert Jobs != None, f'Jobs == None in {file}'
					
					actualJobs = []
					for job in Jobs:
						count = 0
						date_List = [datetime.fromisoformat(item) for item in [job['createdOn'], job['publishedOn'], job['renewedOn']] if item != None]
						for date in date_List:
							if date < UpToDate_time: 
								count += 1
						if count == 0: actualJobs.append(job)
					if len(actualJobs) == 0:
						print(f'Too old jobs. Skip, go to another categoties') #skip jobs, go to another categories
						break						
						
					insert, update = DB_Manager_Upwork.DropToDB(actualJobs, path_to_DB)
					result['insert'] = result['insert'] + insert
					result['update'] = result['update'] + update
					print(f"Result: {result['insert']}(+{insert}) jobs inserted, {result['update']}(+{update}) jobs updated")						
				
				except KeyboardInterrupt:
					PyFile.Write(requests_List, requestsList_log)
					user = input('\nPress key to continue, "restart" or "exit":')
					
					if user == 'exit': 
						driver.quit()
						input()
					elif user == 'restart': 
						driver.quit()
						input()
						assert False, 'Restart'
					else: 
						print('continue')
						time.sleep(2)
	except KeyboardInterrupt as e:
		print('==================6')
		import sys
		exc_type, exc_obj, exc_tb = sys.exc_info()
		print(f"error in line:{exc_tb.tb_lineno}\n{e}\n")
		input('Press any key')
				

	PyFile.Write([], requestsList_log)			

	Total_result = f"Total: {result['insert']} jobs inserted, {result['update']} jobs updated"
	print(Total_result)
	delta = round((time.time() - start))//60
	print(f"Jobs updated in {delta} minutes")
	check_finished = datetime_to_str(now_local(), '%d.%m.%Y %H.%M')
	
	with open(journal, 'a') as file: file.write(check_finished + '\n')
	
	return driver, HomePage

if __name__ == '__main__':
	pass