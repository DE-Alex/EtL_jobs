import MyLibs.SQLite
import pickle
from MyLibs.Time import *
import re

#===DATA BASE
table_name = 'Jobs'

MAIN_TABLE = {#'ID' column created with table as PRIMARY KEY
#'N_professional_roles': 'INTEGER',
'professional_roles': 'TEXT', #['professional_roles'][0...n]['name']
'name': 'TEXT', 
'description': 'TEXT', 
'key_skills': 'TEXT', #['key_skills'][0...n]['name']
'N_key_skills': 'INTEGER',
'salary_from': 'INTEGER', #['salary']['from']
'salary_to': 'INTEGER', #['salary']['to']
'currency': 'TEXT', #['salary']['currency']
'gross': 'TEXT', #['salary']['gross']
'schedule': 'TEXT', #['schedule']['id']
'area': 'TEXT', #['area']['name']
'experience': 'TEXT', #['experience']['id']
'employment': 'TEXT', #['employment']['id']
'employer': 'TEXT', #['employer']['name']
'published_at': 'TEXT',
'created_at': 'TEXT',
'archived': 'TEXT',
#=====My info
'last_updated':'TEXT',
'tags':'TEXT'}
	
def Create(table_name, table_columns, db):
	#MyLibs.SQLite.Create_Table(table_name, 'ID', 'INTEGER', db, PrimaryKey = 'PRIMARY KEY')
	MyLibs.SQLite.Create_Table(table_name, 'ID', 'INTEGER', db)
	MyLibs.SQLite.AddColumnMany(table_name, table_columns, db)
	
def DropToDB(Jobs, DBpath):#, cashPath):
	assert type(Jobs) == list, 'DropToDB: Invalid type of input "Jobs" (non list)'
	db = MyLibs.SQLite.connect(DBpath)
	ID_list = MyLibs.SQLite.Select_ID(table_name, db)
	db.close()


	ins_Jobs = [job for job in Jobs if job['ID'] not in ID_list]#collect jobs to insertMany
	upd_Jobs = [job for job in Jobs if job['ID'] in ID_list] #collect jobs to updateMany
	
	ins_count = len(ins_Jobs)
	upd_count = len(upd_Jobs)

	db = MyLibs.SQLite.connect(DBpath)
	if ins_count !=0: MyLibs.SQLite.InsertMany(table_name, ins_Jobs, db)
	if upd_count !=0: MyLibs.SQLite.UpdateManyByID(table_name, upd_Jobs, db)
	db.close()
	# db = MyLibs.SQLite.connect(cashPath)
	# cID_list = MyLibs.SQLite.Select_ID(table_name, db)
	# db.close()
	# ins_Cash = [job for job in Jobs if job['ID'] not in cID_list]
	# upd_Cash = [job for job in Jobs if job['ID'] in cID_list]
	# db = MyLibs.SQLite.connect(cashPath)
	# if len(ins_Cash) !=0: MyLibs.SQLite.InsertMany(table_name, ins_Cash, db)
	# if len(upd_Cash) !=0: MyLibs.SQLite.UpdateManyByID(table_name, upd_Cash, db)
	# db.close()
	return ins_count, upd_count

def ClearText(text):
	if text == None: return 'No description'
	ReplaceAndDelete = {'<li>': '\n-',
						'</li>': '',
						'<br />': '',
						'<em>': '',
						'</em>': '',
						'<ul>': '',
						'</ul>': '',
						'<p>': '',
						'</p>': ''}
	for str, newStr in ReplaceAndDelete.items():
		text = text.replace(str,newStr)

	pattern = '<strong>(.*?)</strong>'
	match = re.compile(pattern).findall(text)
	for m in match:
		text = text.replace(f'<strong>{m}</strong>', f'\n{m.upper()}')
	return text
	
def Downgrade(vacancy):
	#assert type(vacancy) == dict, 'Downgrade: Invalid type of input data (non dict)'
	if type(vacancy) == str: print(vacancy)
	#Downgrade data to 1 lvl complexity
	job = {}
	try:
		#Setting time in '20.05.2020 16:18' format
		now = now_local()
		job['last_updated'] = datetime_to_str(now, "%Y-%m-%dT%H:%M:%S%z")
		#Setting ID
		#job['ID'] = int(vacancy['id']) #@@@@
		job['ID'] = vacancy['id']
		
		#Clear Description
		job['description'] = ClearText(vacancy['description'])
		job['name'] = vacancy['name']
		job['area'] = vacancy['area']['name']
		if vacancy['salary'] == None: 
			job['salary_from'], job['salary_to'], job['currency'], job['gross'] = None, None, None, None
		else:
			if vacancy['salary']['from'] == None: job['salary_from'] = None
			else: job['salary_from'] = int(vacancy['salary']['from'])
		
			if vacancy['salary']['to'] == None: job['salary_to'] = None
			else: job['salary_to'] = int(vacancy['salary']['to'])
			
			job['currency'] = vacancy['salary']['currency']
			if vacancy['salary']['gross'] == '0': job['gross'] = 'True'
			elif vacancy['salary']['gross'] == '1': job['gross'] = 'False'
			else: job['gross'] = vacancy['salary']['gross']
		
		job['published_at'] = vacancy['published_at']
		job['created_at'] = vacancy['created_at']
		job['employer'] = vacancy['employer']['name']
		job['schedule'] = vacancy['schedule']['id']
		job['experience'] = vacancy['experience']['id']		
		job['employment'] = vacancy['employment']['id']
		job['archived'] = vacancy['archived']
		
		skills_list = [skill['name'] for skill in vacancy['key_skills']]
		skills_list.sort()
		job['N_key_skills'] = len(skills_list)
		job['key_skills'] = '|'.join(skills_list)	

		roles_list = [role['name'] for role in vacancy['professional_roles']]
		roles_list.sort()
		job['professional_roles'] = '|'.join(roles_list)	
					
	except Exception as e:
		import sys
		exc_type, exc_obj, exc_tb = sys.exc_info()
		print(f"Downgrade error in line:{exc_tb.tb_lineno}\n{e}\n)")
		print(vacancy)
		input('Press any key')
	return job
	
if __name__ == '__main__':
	#pass
	path = r'D:\DB_HH\_Empty_.sqlite3'
	db = MyLibs.SQLite.connect(path)
	Create(table_name, MAIN_TABLE, db)
	db.close()

	
