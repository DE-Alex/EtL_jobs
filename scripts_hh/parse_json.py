import os, sys
import configparser
import re
from pathlib import Path
from dateutil.tz import tzutc, tzlocal
from datetime import datetime

tzutc = tzutc()

parent_dir = os.path.abspath(os.path.join(sys.path[0], '..'))
config = configparser.ConfigParser()
config.read(Path(parent_dir, 'pipeline.conf'))

logs_folder = Path(parent_dir, config['general']['logs_folder'])

folder = Path(config['upwork']['scripts_folder'])
err_path = Path(logs_folder, config['upwork']['errors_file'])

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
                #'salary_from' : vacancy.get('salary').get('from'),
                #'salary_to' : vacancy.get('salary').get('to'),
                #'currency' : vacancy.get('salary').get('currency'),
                #'gross' : vacancy.get('salary').get('gross'),
                #'address_lat' : vacancy.get('address').get('lat'),
                #'address_lng' : vacancy.get('address').get('lng'),
                
                'published_at' : vacancy['published_at'],
                'created_at' : vacancy['created_at'],
                'employer' : vacancy['employer']['name'],
                'schedule' : vacancy['schedule']['id'],
                'experience' : vacancy['experience']['id'],
                'employment' : vacancy['employment']['id'],
                'archived' : vacancy['archived']
                }
        
        
        sal = [('salary_from', 'from'), ('salary_to', 'to'), ('currency', 'currency'), ('gross', 'gross')]
        for a, b in sal:
            if vacancy.get('salary'):
                job[a] = vacancy['salary'].get(b)
            else:
                job[a] = None
                
        adr = [('address_lat', 'lat'), ('address_lng', 'lng')]   

        for a, b in adr:
            if vacancy.get('address'):        
                job[a] = vacancy['address'].get(b)
        else:
            job[a] = None         
                        
#        'salary_from' : vacancy['salary'].get('from')
#        'salary_to' : vacancy['salary'].get('to')
#        'currency' : vacancy['salary'].get('currency')
#        'gross' : vacancy['salary'].get('gross')
#        'address_lat' : vacancy['address'].get('lat')
#        'address_lng' : vacancy['address'].get('lng')        

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
        print(f"Downgrade error in line:{exc_tb.tb_lineno}\n{e}\n vac id:{vacancy['id']})")
        dump_json(job)
    return job

def dump_json(job):
    import json
    time = datetime.strftime(datetime.now(tzlocal), filename_date_format)#datetime obj to str
    dump_path = Path(logs_folder, f'{time}.json')
    with open(dump_path, 'w') as f:
        json.dump(job, f)
    print(f'Saved json to: {dump_path}')

if __name__ == '__main__':
    #pass
    path = r'D:\DB_HH\_Empty_.sqlite3'
    db = MyLibs.SQLite.connect(path)
    Create(table_name, MAIN_TABLE, db)
    db.close()


