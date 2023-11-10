import re
from dateutil.tz import tzutc, tzlocal
from datetime import datetime

tzutc = tzutc()

def clear_text(text):
	if text == None: return ' '
	replace_delete = {'<li>': '\n-',
						'</li>': '',
						'<br />': '',
						'<em>': '',
						'</em>': '',
						'<ul>': '',
						'</ul>': '',
						'<p>': '',
						'</p>': ''}
	for str, new_str in replace_delete.items():
		text = text.replace(str, new_str)

	pattern = '<strong>(.*?)</strong>'
	match = re.compile(pattern).findall(text)
	for m in match:
		text = text.replace(f'<strong>{m}</strong>', f'\n{m.upper()}')
	return text
	
def parse_vacancy(vacancy):
	#downgrade data to 1 lvl complexity
	job = {}
	try:
        #setting UTC time
        job =   {'last_updated' : datetime.now(tzutc).replace(microsecond = 0).isoformat,
                'id' : int(vacancy['id']),
                'description' : clear_text(vacancy['description']),
                'name' : vacancy['name'],
                'area' : vacancy['area']['name'],
                'salary_from' : vacancy.get('salary').get('from'),
                'salary_to' : vacancy.get('salary').get('to'),
                'currency' : vacancy.get('salary').get('currency'),
                'gross' : vacancy.get('salary').get('gross'),
                'address_lat' : vacancy.get('address').get('lat'),
                'address_lng' : vacancy.get('address').get('lng'),
                'published_at' : vacancy['published_at'],
                'created_at' : vacancy['created_at'],
                'employer' : vacancy['employer']['name'],
                'schedule' : vacancy['schedule']['id'],
                'experience' : vacancy['experience']['id'],
                'employment' : vacancy['employment']['id'],
                'archived' : vacancy['archived']
                }
		
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

	
