#Если не работает то проверить:
#0) почистить куки браузера (status code 502)
#1) сверить UserAgent с браузером (мог измениться после обновления браузера)
#2) генерацию запросов (Upwork часто меняет)
#3) сверить Headers в Upwork_requests с Header браузера

import os, sys, time
from datetime import datetime, timedelta
from shutil import copyfile
import traceback
import re

import MyLibs.PyObject_to_PyFile as PyFile
from MyLibs.Time import *
import MyLibs.SQLite
import MyLibs.Scan_DirsFiles

import IP
import DB_Manager_Upwork
import Upwork_requests
#================General settings=========================
check = timedelta(minutes = 10)
UserAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) Gecko/20100101 Firefox/101.0'
proxy = '127.0.0.1:35685'#mitmproxy server
LogDir = sys.path[0] + r'\Log'
err_log = rf'{LogDir}\#UpwErrors.log'
journal_log = rf'{LogDir}\journal.log'
arhive_log = rf'{LogDir}\arhive.log'
ip_log = rf'{LogDir}\IP.log'

table_name = 'Jobs'
DB_Folder = rf'D:\DB_Upwork'
emptyDB = rf'{DB_Folder}\_Empty.sqlite3'

Tmp = r'D:\Temp'
cashPath = rf'{Tmp}\_cash_.sqlite3'
All_ID_path = rf'{Tmp}\Upw_all_ID.sqlite3'

Arhive_path = rf'D:\Shapovalov\svoe\Python\PY\DB_Upwork'

class LoadJobs():
	def __init__(self):
		#===Read Journal=====
		j_read = PyFile.Read(journal_log)
		if j_read == None: self.j_recs = ['01.01.2000 00.00']
		else: self.j_recs = j_read
		self.lastCheck_dt = local_to_utc(str_to_datetime(self.j_recs[-1] , '%d.%m.%Y %H.%M'))
		#===Arhive====
		self.arh_recs = PyFile.Read(arhive_log)
		if self.arh_recs == None: self.arh_recs = ['01.01.2000 00.00']
		self.lastArhive_dt = local_to_utc(str_to_datetime(self.arh_recs[-1] , '%d.%m.%Y %H.%M'))	
		
		import MTM.UserAgent_to_MTM
		MTM.UserAgent_to_MTM.write_in(UserAgent)
		
		self.ScanAll_ID()
		
		if not os.path.exists(cashPath): copyfile(emptyDB, cashPath)
		
	def main(self):
		errors = 0
		try:
			lastCheck_dt_local = utc_to_local(self.lastCheck_dt)
			print('last check (local):',lastCheck_dt_local.date(), lastCheck_dt_local.time())
			IP.IpLog(proxy, ip_log)
			self.HomePage = 'https://www.upwork.com/nx/jobs/search/?sort=recency'
			reqList = self.ReadReqList()
			if reqList:
				print(f'reqList found.')
				self.Download(reqList)
			while True:
				now = now_utc()
				if now > self.lastArhive_dt + timedelta(hours = 24): self.Arhivation()
				if now < self.lastCheck_dt + check:
					delta = self.lastCheck_dt + check - now
					if delta > check/4: 
						print(f'Sleeping for {delta.seconds} seconds')
						time.sleep(check.seconds/4)
					elif delta < check/4: 
						print(f'Sleeping for {delta.seconds} seconds')
						time.sleep(delta.seconds + 1)
				elif now < self.lastCheck_dt + check*2:
					self.Refresh()
				else:
					print(f'Desision: ', end=' ')
					url = f'https://www.upwork.com/ab/jobs/search/url?per_page=50&sort=recency&page=90'
					req = Upwork_requests.reqGet(url, self.HomePage, UserAgent, err_log, proxy)
					json_data = req.json()	
					self.HomePage = url
					
					#DB_Manager_Upwork.CategoriesCheck(json_data, err_log)
					Jobs = DB_Manager_Upwork.clear_Upwork_data(json_data)
					Jobs = DB_Manager_Upwork.Downgrade(Jobs)
					
					checkpoint = self.lastCheck_dt - check*10
					actualJobs = self.DataCheck(Jobs, checkpoint)
					if len(actualJobs) == 0:
						self.Refresh()
					else:
						self.FullUpdate(json_data)
		except Exception:
			e = traceback.format_exc()
			print(e)
			errors += 1
			self.ErrorsLog(e)
		finally:
			if errors > 10:
				input('Paused. Press any key.')
				errors = 0
	
	def ErrorsLog(self, e):
		time = datetime_to_str(now_local(), '%d.%m.%Y %H.%M')
		with open(err_log, 'a') as file: 
			file.write(time + '\n' + str(e) + '\n')
	
	def Refresh(self):
		print(f'Refresh.')
		reqList = [[Upwork_requests.req_Generator(i) for i in range(1,100)]]
		self.SaveReqList(reqList)
		self.Download(reqList)
	
	def FullUpdate(self, json_data):
		print(f'FullUpdate.')
		HomePage, reqList = Upwork_requests.List(json_data, self.HomePage, UserAgent, err_log, proxy) 
		self.HomePage = HomePage
		self.SaveReqList(reqList)
		self.Download(reqList)
	
	def ReadReqList(self):
		files, _ = MyLibs.Scan_DirsFiles.DirScanByMask(Tmp, 'requests*')
		if files == []: 
			self.reqList_log, reqList = None, None
		else: 
			for filename in files:
				path = rf'{Tmp}\{filename}'
				reqList = PyFile.Read(path)
				if reqList == None:
					os.remove(path)
					self.reqList_log = None
				else:
					self.reqList_log = path
		return reqList
	
	def SaveReqList(self, reqList):
		if self.reqList_log == None:
			now = datetime_to_str(now_local(), '%d.%m.%Y %H.%M')
			self.reqList_log = rf'{Tmp}\requests {now}.log'
		PyFile.Write(reqList, self.reqList_log)	
			
	def Download(self, reqList):
		N_reqs = sum([len(list) for list in reqList])
		print(datetime_to_str(now_local(), '%d.%m.%Y %H.%M'))
		print(f'Requests to download: {N_reqs}')
		#======Download requests=======
		result = {'insert': 0, 'update': 0}
		start = time.time()
		for requests in reqList:
			while len(requests) !=0:
				N_reqs = sum([len(list) for list in reqList])
				url = requests[0]
				req = Upwork_requests.reqGet(url, self.HomePage, UserAgent, err_log, proxy)
				json_data = req.json()
				self.HomePage = url
				print(f'{N_reqs} - OK', end=' ')
				
				#save json to hard drive
				#import json
				#with open(f'{sys.path[0]}\Temp\{N_reqs}.json', 'w') as f: json.dump(json_data, f)

				#DB_Manager_Upwork.CategoriesCheck(json_data, err_log)
				Jobs = DB_Manager_Upwork.clear_Upwork_data(json_data)
				Jobs = DB_Manager_Upwork.Downgrade(Jobs)
				assert Jobs != None, f'Jobs == None in {file}'
				checkpoint = self.lastCheck_dt - timedelta(minutes = 5)
				actualJobs = self.DataCheck(Jobs, checkpoint)

				if len(actualJobs) == 0:
					print(f'Too old jobs. Skip the rest')
					del requests[:]
					self.SaveReqList(reqList)
					break
				
				NewID = []
		
				SortedJobs = {}
				for job in actualJobs:
					date = datetime_to_str(datetime.fromisoformat(job['createdOn']), '%Y.%m')
					if date not in SortedJobs:
						SortedJobs[date] = []
					SortedJobs[date].append(job)
					NewID.append(job['ID'])
			
				insert, update = 0, 0
				for date in list(SortedJobs.keys()):
					path = rf'{DB_Folder}\{date}.sqlite3'
					if not os.path.exists(path):
						copyfile(emptyDB, path)
					jobs = SortedJobs[date]	
					ins, upd = DB_Manager_Upwork.DropToDB(jobs, path, cashPath)
					insert += ins
					update += upd
				
				result['insert'] = result['insert'] + insert
				result['update'] = result['update'] + update
				print(f"Result: {result['insert']}(+{insert}) inserted, {result['update']}(+{update}) updated")
				del requests[0]
				self.SaveReqList(reqList)
				self.All_ID.extend(NewID)
		Total_result = f"Total: {result['insert']} inserted, {result['update']} updated"
		print(Total_result)
		delta = round((time.time() - start))//60
		print(f"Downloaded in {delta} minutes")

		FinishDate = re.compile('\d\d.\d\d.\d\d\d\d \d\d.\d\d').search(self.reqList_log).group()
		self.lastCheck_dt = local_to_utc(str_to_datetime(FinishDate , '%d.%m.%Y %H.%M'))
		self.j_recs = self.j_recs[-30:] + [FinishDate]
		PyFile.Write(self.j_recs, journal_log)
		os.remove(self.reqList_log)
		self.reqList_log = None
		self.dropNewIDToFile()
		
	def Arhivation(self):
		print('Arhivation: ')
		#DB_paths = self.DB_paths()
		data1 = datetime_to_str(now_utc(), '%Y.%m')
		data2 = datetime_to_str(now_utc() - timedelta(days = 30), '%Y.%m')
		dates = set([data1, data2])
		DB_paths = []
		for date in dates:
			path = rf'{DB_Folder}\{date}.sqlite3'
			if os.path.exists(path):
				DB_paths.append(path)
				
		for path in DB_paths:
			baseName = os.path.basename(path)
			newPath = f'{Arhive_path}\{baseName}'
			copyfile(path, newPath)
			print(f'{baseName} to: {newPath}')
		print('done')
		self.lastArhive_dt = now_utc()
		arh_finished = datetime_to_str(now_local(), '%d.%m.%Y %H.%M')
		self.arh_recs = self.arh_recs[-30:] + [arh_finished]
		PyFile.Write(self.arh_recs, arhive_log)

	def DataCheck(self, jobs, checkpoint):
		#Upwork order jobs in Recent List by 'createdOn'
		#So if some job is renewed ('renewedOn') it is not come into the beginning of the List
		#Parser can find such job, add to actualJobs and begin FullUpdate
		actualJobs = []
		for job in jobs:
			date_List = [datetime.fromisoformat(item) for item in [job['createdOn'], job['publishedOn'], job['renewedOn']] if item != None]
			date_List.sort()
			newest = date_List[-1]
			id = job['ID']
			if newest < checkpoint and id in self.All_ID: pass
			else: actualJobs.append(job)
			#actualJobs = jobs
		return actualJobs
	
	# def DB_paths(self):
		# data1 = datetime_to_str(now_utc(), '%Y.%m')
		# data2 = datetime_to_str(now_utc() - timedelta(days = 30), '%Y.%m')
		# dates = set([data1, data2])
		# DB_paths = []
		# for date in dates:
			# path = rf'{DB_Folder}\{date}.sqlite3'
			# if os.path.exists(path):
				# DB_paths.append(path)
		# return DB_paths
			
	def ScanAll_ID(self):
		if os.path.exists(All_ID_path):
			db = MyLibs.SQLite.connect(All_ID_path)
			All_ID = MyLibs.SQLite.Select_ID('all_ID', db)
			db.close
			self.All_ID = All_ID
		else:
			start = time.time()
			FilePaths, _ = MyLibs.Scan_DirsFiles.SubdirScanPaths(DB_Folder)
			paths = [i for i in FilePaths if ('20' in i) and ('.sqlite3' in i)]
			All_ID = []
			for path in paths:
				db = MyLibs.SQLite.connect(path)
				ID_list = MyLibs.SQLite.Select_ID(table_name, db)
				db.close()
				All_ID.extend(ID_list)
			print(f"Scanned All ID in all DB files in {time.time() - start} seconds")
			db = MyLibs.SQLite.connect(All_ID_path)
			MyLibs.SQLite.Create_Table('all_ID', 'ID', 'INTEGER', db)
			db.close
			self.All_ID = All_ID
			self.dropNewIDToFile()
		
	def dropNewIDToFile(self):
		db = MyLibs.SQLite.connect(All_ID_path)
		ID_list = MyLibs.SQLite.Select_ID('all_ID', db)	
		NewID = list(set(self.All_ID) - set(ID_list))
		if len(NewID) >0:
			data = [{'ID': ID} for ID in NewID]
			MyLibs.SQLite.InsertMany('all_ID', data, db)
		db.close()
		
if __name__ == '__main__':
	while True:
		try:
			L =  LoadJobs()
			L.main()
		except SystemExit as e:
			time = datetime_to_str(now_local(), '%d.%m.%Y %H.%M')
			with open(err_log, 'a') as file: 
				file.write(time + '\n' + str(e) + '\n')
			

