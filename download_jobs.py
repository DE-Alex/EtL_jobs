#Если не работает то проверить:
#0) почистить куки браузера (status code 502)
#1) сверить user_agent с браузером (мог измениться после обновления браузера)
#2) генерацию запросов (Upwork часто меняет)
#3) сверить Headers в Upwork_requests с Header браузера

# from pathlib import Path
# import configparser
# import sys
# import pyscopg2	#pip install pyscopg2

# import py_object_to_file as pyfile

# import os, time
# from datetime import datetime, timedelta
# from shutil import copyfile
# import traceback
# import re

# import MyLibs.PyObject_to_PyFile as PyFile
# from MyLibs.Time import *
# import MyLibs.SQLite
# import MyLibs.Scan_DirsFiles

# import IP
# import DB_Manager_Upwork
# import Upwork_requests
#================General settings=========================

#check = timedelta(minutes = 10) ->> Airflow
user_agent = config.get('parser_config', 'user_agent')
proxy = config.get('parser_config', 'proxy')
dt_format = config.get('parser_config', 'date_format')  



script_fold = sys.path[0]
err_log = Path(script_fold, 'Log', '#UpwErrors.log')
journal_log = Path(script_fold, 'Log', 'journal.log')
tmp_fold = Path(script_fold, 'Temp')

config = configparser.ConfigParser()
#pipe_conf = Path(Path.cwd(), 'pipeline.conf')
config.read('pipeline.conf')

user_agent = config.get('parser_config', 'user_agent')
proxy = config.get('parser_config', 'proxy')
dt_format = config.get('parser_config', 'date_format')  

dbname = config.get("postgres_config", "database")
user = config.get("postgres_config", "username")
password = config.get("postgres_config", "password")
host = config.get("postgres_config", "host")
port = config.get("postgres_config", "port")
table_name = config.get('postgres_config', 'upwork_table')

#table_name = 'Jobs'
#DB_Folder = rf'D:\DB_Upwork'
#emptyDB = rf'{DB_Folder}\_Empty.sqlite3'
#Tmp = r'D:\Temp'
#cashPath = rf'{Tmp}\_cash_.sqlite3'
#All_ID_path = rf'{Tmp}\Upw_all_ID.sqlite3'

class LoadJobs():
	def __init__(self):
		#datetime of last successfull ingestion
		j_read = pyfile.Read(journal_log)
		if j_read == None: 
			self.journal_recs = ['01.01.1970 00.00']
		else: 
			self.journal_recs = j_read
		self.lastCheck_dt = local_to_utc(str_to_datetime(self.journal_recs[-1] , dt_format))
		
		import MTM.UserAgent_to_MTM #перенести в папку со скриптом?
		MTM.UserAgent_to_MTM.write_in(user_agent)
		
		self.jobs_id = jobs_id_from_db()
		
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
					req = Upwork_requests.reqGet(url, self.HomePage, user_agent, err_log, proxy)
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
		time = datetime_to_str(now_local(), dt_format)
		with open(err_log, 'a') as file: 
			file.write(time + '\n' + str(e) + '\n')
	
	def Refresh(self):
		print(f'Refresh.')
		reqList = [[Upwork_requests.req_Generator(i) for i in range(1,100)]]
		self.SaveReqList(reqList)
		self.Download(reqList)
	
	def FullUpdate(self, json_data):
		print(f'FullUpdate.')
		HomePage, reqList = Upwork_requests.List(json_data, self.HomePage, user_agent, err_log, proxy) 
		self.HomePage = HomePage
		self.SaveReqList(reqList)
		self.Download(reqList)
	
	def ReadReqList(self):
		files, _ = MyLibs.Scan_DirsFiles.DirScanByMask(tmp_fold, 'requests*')
		if files == []: 
			self.reqList_log, reqList = None, None
		else: 
			for filename in files:
				path = rf'{tmp_fold}\{filename}'
				reqList = pyfile.Read(path)
				if reqList == None:
					os.remove(path)
					self.reqList_log = None
				else:
					self.reqList_log = path
		return reqList
	
	def SaveReqList(self, reqList):
		if self.reqList_log == None:
			now = datetime_to_str(now_local(), dt_format)
			self.reqList_log = rf'{tmp_fold}\requests {now}.log'
		pyfile.Write(reqList, self.reqList_log)	
			
	def Download(self, reqList):
		N_reqs = sum([len(list) for list in reqList])
		print(datetime_to_str(now_local(), dt_format))
		print(f'Requests to download: {N_reqs}')
		#======Download requests=======
		result = {'insert': 0, 'update': 0}
		start = time.time()
		for requests in reqList:
			while len(requests) !=0:
				N_reqs = sum([len(list) for list in reqList])
				url = requests[0]
				req = Upwork_requests.reqGet(url, self.HomePage, user_agent, err_log, proxy)
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
				self.jobs_id.extend(NewID)
		Total_result = f"Total: {result['insert']} inserted, {result['update']} updated"
		print(Total_result)
		delta = round((time.time() - start))//60
		print(f"Downloaded in {delta} minutes")

		FinishDate = re.compile('\d\d.\d\d.\d\d\d\d \d\d.\d\d').search(self.reqList_log).group()
		self.lastCheck_dt = local_to_utc(str_to_datetime(FinishDate , dt_format))
		self.journal_recs = self.journal_recs[-30:] + [FinishDate]
		pyfile.Write(self.journal_recs, journal_log)
		os.remove(self.reqList_log)
		self.reqList_log = None
		
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
			if newest < checkpoint and id in self.jobs_id: pass
			else: actualJobs.append(job)
			#actualJobs = jobs
		return actualJobs
			
	def jobs_id_from_db(self):
		conn = psycopg2.connect(
			"dbname=" + dbname
			+ " user=" + user
			+ " password=" + password
			+ " host=" + host,
			port = port)
			
		id_query = f"SELECT id FROM {table_name};"
		cursor = conn.cursor()
		cursor.execute(id_query)
		results = cursor.fetchall()
	
		cursor.close()
		conn.close()
		
		jobs_id = [item[0] for item in result]
		return jobs_id
		
if __name__ == '__main__':
	while True:
		try:
			L =  LoadJobs()
			L.main()
		except SystemExit as e:
			time = datetime_to_str(now_local(), dt_format)
			with open(err_log, 'a') as file: 
				file.write(time + '\n' + str(e) + '\n')
			

