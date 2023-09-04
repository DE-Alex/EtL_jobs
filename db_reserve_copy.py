from pathlib import Path
import configparser
import sys

import py_object_to_file as pyfile

# import os
# from datetime import timedelta
# from shutil import copyfile

# import py_object_to_file as pyfile
# from MyLibs.Time import *

#================General settings=========================
arhive_log = Path(script_fold, 'Log', 'arhive.log')
arhive_fold = Path('Db_dump') #сделать папку

config = configparser.ConfigParser()
#pipe_conf = Path(Path.cwd(), 'pipeline.conf')
config.read('pipeline.conf')

#===Arhive====
arh_recs = pyfile.Read(arhive_log)
if arh_recs == None: 
	arh_recs = ['01.01.1970 00.00']
lastArhive_dt = local_to_utc(str_to_datetime(arh_recs[-1] , '%d.%m.%Y %H.%M'))	

now = now_utc()
if now > lastArhive_dt + timedelta(hours = 24): Arhivation()		


def Arhivation():
		print('Arhivation: ')
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
		lastArhive_dt = now_utc()
		arh_finished = datetime_to_str(now_local(), '%d.%m.%Y %H.%M')
		arh_recs = arh_recs[-30:] + [arh_finished]
		pyfile.Write(arh_recs, arhive_log)
		
if __name__ == '__main__':
	pass			

