import os, sys, time
from datetime import datetime, timedelta
import dateutil.parser
from shutil import copyfile
import traceback
import re

import MyLibs.PyObject_to_PyFile as PyFile
from MyLibs.Time import *
import MyLibs.SQLite
import MyLibs.Scan_DirsFiles

import HH_requests
#================General settings=========================
Request_Delay = 3 #seconds between requests
check = timedelta(minutes = 2)
T_arh = 24 #hours
LogDir = sys.path[0] + r'\Log'
err_log = rf'{LogDir}\#HH_Errors.log'
journal_log = rf'{LogDir}\journal.log'
arhive_log = rf'{LogDir}\arhive.log'

table_name = 'Jobs'
DB_Folder = rf'D:\DB_HH'
emptyDB = rf'{DB_Folder}\_Empty_.sqlite3'

Arhive_path = rf'D:\Shapovalov\svoe\Python\PY\DB_HH'

class LoadJobs():
	def __init__(self):
		#===Read Journal=====
		j_read = PyFile.Read(journal_log)
		if j_read == None: self.j_recs = ['01.01.2000 00.00']
		else: self.j_recs = j_read
		#self.lastCheck_dt = local_to_utc(str_to_datetime(self.j_recs[-1] , '%d.%m.%Y %H.%M'))
		self.lastCheck_dt = naive_local_to_aware(str_to_datetime(self.j_recs[-1] , '%d.%m.%Y %H.%M'))
		#===Arhive====
		self.arh_recs = PyFile.Read(arhive_log)
		if self.arh_recs == None: self.arh_recs = ['01.01.2000 00.00']
		#self.lastArhive_dt = local_to_utc(str_to_datetime(self.arh_recs[-1] , '%d.%m.%Y %H.%M'))	
		self.lastArhive_dt = naive_local_to_aware(str_to_datetime(self.arh_recs[-1] , '%d.%m.%Y %H.%M'))
		
		self.ScanAll_ID()
		self.Generator = HH_requests.UrlsGenerator(DB_Folder, emptyDB, err_log, Request_Delay)
		
	def main(self):
		errors = 0
		try:
			print('last check:',self.lastCheck_dt.date(), self.lastCheck_dt.time())
			while True:
				now = now_local()
				if now > self.lastArhive_dt + timedelta(hours = T_arh): 
					self.Arhivation()
				if now < self.lastCheck_dt + check:
					print('Nothing to do!')
					pass
					# delta = self.lastCheck_dt + check - now
					# if delta > check/4: 
						# print(f'Sleeping for {delta.seconds} seconds')
						# time.sleep(check.seconds/4)
					# elif delta < check/4: 
						# print(f'Sleeping for {delta.seconds} seconds')
						# time.sleep(delta.seconds + 1)
				else:
					start = now_local()
					print(f'Update...',)
					self.All_ID = self.Generator.main(self.All_ID)
					FinishDate = datetime_to_str(start, '%d.%m.%Y %H.%M')
					self.j_recs = self.j_recs[-30:] + [FinishDate]
					PyFile.Write(self.j_recs, journal_log)
					self.lastCheck_dt = start
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
	
	def Arhivation(self):
		print('Arhivation: ')
		DB_paths = self.DB_paths()
		for path in DB_paths:
			baseName = os.path.basename(path)
			newPath = f'{Arhive_path}\{baseName}'
			copyfile(path, newPath)
			print(f'{baseName} to: {newPath}')
		print('done')
		self.lastArhive_dt = now_local()
		arh_finished = datetime_to_str(now_local(), '%d.%m.%Y %H.%M')
		self.arh_recs += [arh_finished]
		PyFile.Write(self.arh_recs, arhive_log)
	
	def DB_paths(self):
		T1 = now_utc()
		data1 = datetime_to_str(local_to_utc(T1), '%Y.%m')
		T2 = T1 - timedelta(days = 30)
		data2 = datetime_to_str(local_to_utc(T2), '%Y.%m')
		dates = set([data1, data2])
		DB_paths = []
		for date in dates:
			path = rf'{DB_Folder}\{date}.sqlite3'
			if os.path.exists(path):
				DB_paths.append(path)
		return DB_paths
			
	def ScanAll_ID(self):
		print('Scanning DB files for IDs...')
		start = time.time()
		FilePaths, _ = MyLibs.Scan_DirsFiles.SubdirScanPaths(DB_Folder)
		paths = [i for i in FilePaths if '.sqlite3' in i]
		All_ID = {}
		for path in paths:
			db = MyLibs.SQLite.connect(path)
			data = MyLibs.SQLite.Select(table_name, db, ['ID', 'last_updated'])
			db.close()
			for id, updated in data:
				All_ID[id] = updated
		print(f"Scanned All ID in all DB files in {round(time.time() - start)} seconds. Total {len(All_ID)} found")
		self.All_ID = All_ID
		
if __name__ == '__main__':
	try:
		L =  LoadJobs()
		L.main()
	except SystemExit as e:
		time = datetime_to_str(now_local(), '%d.%m.%Y %H.%M')
		with open(err_log, 'a') as file:
			file.write(time + '\n' + str(e) + '\n')
		input()
	except KeyboardInterrupt:
		print('Paused')
		input()
		
	except Exception:
		e = traceback.format_exc()
		print(e)
		time = datetime_to_str(now_local(), '%d.%m.%Y %H.%M')
		with open(err_log, 'a') as file:
			file.write(time + '\n' + str(e) + '\n')
			

