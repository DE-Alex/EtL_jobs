# -*- coding: utf-8 -*-
import sys, os
import configparser
import requests
import time
#import json
from pathlib import Path
from datetime import datetime
from dateutil.tz import tzlocal
tzlocal = tzlocal()

# 'all employers' = '/employers'  params = {text: 'text', area: 'area', per_page: 100, page: 0..20}
# 'employer'= '/employers/{employer_id}' 
    
#read configuration file
config = configparser.ConfigParser()
parent_dir = os.path.abspath(os.path.join(sys.path[0], '..'))
config.read(Path(parent_dir, 'pipeline.conf'))

logs_folder = Path(parent_dir, config['general']['logs_folder'])

err_path = Path(logs_folder, config['headhunter']['errors_file'])
api_url = config['headhunter']['api_url']
request_delay = int(config['headhunter']['requests_delay'])

def get_filters():
    dictionaries = send_request(f'{api_url}/dictionaries', {}).json() 
    filters = {}
    filters['employment'] = [item['id'] for item in dictionaries['employment']]
    filters['experience'] = [item['id'] for item in dictionaries['experience']]
    filters['schedule'] = [item['id'] for item in dictionaries['schedule']]
    print('Filters loaded')
    return filters
    
def get_areas():
    areas = send_request(f'{api_url}/areas', {}).json() 
    print('Areas loaded')
    return areas
    
def get_metro():
    metro = send_request(f'{api_url}/metro/1', {}).json() 
    metro_stations = []
    metro_lines = metro['lines']
    for line in metro_lines:
        for station in line['stations']:
            metro_stations.append(station['id'])
    print('Metro stations loaded')
    return metro_stations

def get_professions():
    professional_roles = send_request(f'{api_url}/professional_roles', {}).json() 
    print('Professions loaded')
    tmp = []
    categories = professional_roles['categories']
    for category in categories:
        roles = category['roles']
        for role in roles:
            tmp.append([role['id'], role['name']])
    
    #read blacklist of professions
    path = Path(sys.path[0], 'profs_black_list.txt')
    with open(path) as f:
        dt = f.read().split('\n')
    #id list of professions in blacklist    
    id_black = [t.split(' ')[0] for t in dt]
    
    white_list = [id for id, name in tmp if id not in id_black]
    return white_list
    
def requests_pattern(params = {}, page = 0, id = False):
    if id:
        url = api_url + f'/vacancies/{id}?host=hh.ru'
        params = {}
    else:
        url = api_url + f'/vacancies'
        default = {'per_page': 100, 'clusters': 'true', 'describe_arguments': 'true'}
        params.update(default)
        params.update({'page': page})
    return url, params    
    
def send_request(url, parameters):
    time.sleep(request_delay)
    for i in range(5):
        print(parameters)
        req = requests.get(url, params=parameters)
        req.close()
        if req.status_code == requests.codes.ok: 
            return req
        else:
            t_sleep = 10
            err_msg = f'i={i}: status code {req.status_code}. Paused for {t_sleep} sec.'
            print(err_msg)
            time_now = datetime.now(tzlocal).replace(microsecond = 0).isoformat()
            with open(err_path, 'a') as file: 
                file.write(f'{time_now} {err_msg}\n')
            time.sleep(t_sleep)
    #requests.get failed for i times. Exit.
    exit(1)		

# def SaveJson(jsObj):	
    # JsonDir = r'D:\DB_HH\Json'
    # N = len(os.listdir(JsonDir))
    # nextFileName = rf'{JsonDir}\{N}.json'
    # with open(nextFileName, mode='w', encoding='utf8') as file:
        # file.write(json.dumps(jsObj, ensure_ascii=False))
            
   
if __name__ == '__main__':
    pass
