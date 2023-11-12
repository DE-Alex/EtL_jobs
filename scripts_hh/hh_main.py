import configparser
import sys, os
import time
import traceback
import dateutil.parser
from pathlib import Path
from datetime import datetime
from dateutil.tz import tzutc, tzlocal
#import dateutil.parser
tzlocal = tzlocal()
tzutc = tzutc()

import db_operations
import hh_requests
import parse_json

#read configuration file
config = configparser.ConfigParser()
parent_dir = os.path.abspath(os.path.join(sys.path[0], '..'))
config.read(Path(parent_dir, 'pipeline.conf'))

filename_date_format = config['general']['filename_date_format']
temp_folder = Path(parent_dir, config['general']['temp_folder'])
logs_folder = Path(parent_dir, config['general']['logs_folder'])

err_path = Path(logs_folder, config['headhunter']['errors_file'])
journal_path = Path(logs_folder, config['headhunter']['journal_file'])

#load dictionaries from www.hh.ru
print('Load dictionaries from www.hh.ru')
areas = hh_requests.get_areas()
metro_stations = hh_requests.get_metro()
filters = hh_requests.get_filters()
#prof_roles = hh_requests.get_professions()
jobs_id = db_operations.id_from_db()

#datetime of last successfull ingestion
try:
    with open(journal_path) as file:
        result = file.read().split('\n')            
except FileNotFoundError:
    print(f'"{journal_path}" not found.')
    result = ['2000-01-01T00:00:00+03:00']
    
journal_recs = [i for i in result if i != '']
try:
    last_rec = journal_recs[-1]
    last_etl_loc = datetime.fromisoformat(last_rec)
except IndexError:
    print(f'"{journal_path}" read data error.')
    last_etl_loc = datetime.fromisoformat('2000-01-01T00:00:00+03:00')
last_etl_utc = last_etl_loc.astimezone(tzutc) #move to utc timezone
print('last check (local):', datetime.strftime(last_etl_loc, '%Y.%m.%d %H:%M'))

def main():
    #check for new jobs and form list of requests
    errors = 0
    #vacancy_insert = 0
    #vacancy_update = 0
    while errors <5:
        try:
            start_etl = datetime.now(tzlocal)
            params = {'date_from' : last_rec}
            search_by_filters(0, params)
               
            #print(f"Total: {downl_cnt['insert']} inserted, {downl_cnt['update']} updated")
            delta = round((time.time() - start_etl))//60
            print(f"Downloaded in {delta} minutes") 
            
            etl_date = start_etl.replace(microsecond = 0).isoformat()        
            journal_recs = ('\n').join(journal_recs[-30:] + [etl_date])
            with open(journal_path, 'w') as file: 
                file.write(journal_recs)          
            
        except SystemExit as e:
            print('Exit.')
            exit(0)
        except Exception as e:
            e = traceback.format_exc()
            err_msg = str(e)
            print(err_msg)
            errors_log(err_msg)
            errors = errors + 1
    return None
    
def search_by_filters(i, params):
    name = sorted(list(filters.keys()))[i]
    values = filters[name]
    max_depth = len(filters.keys())-1
    print(i, params, name)
    for value in values:
        params.update({name : value})
        result = get_vacancy_id(params)

        if result == False and i < max_depth:
            search_by_filters(i+1, params)
        elif result == False and i == max_depth:
            search_by_areas(params, areas)
        del params[name]
    return None
    
def search_by_areas(params, parent):
    for area in parent:
        name = area['name']
        value = area['id']
        childs = area['areas']
        
        params.update({'area' : value})
        result = get_vacancy_id(params)
        
        if result == False and name == 'Москва':     
            search_by_metro(params)
        elif result == False and childs == []:
            msg = 'All filters used but too many vacancies. Download first 2000'
            errors_log(msg)
            get_vacancy_id(params, '2000_limit')   
        elif result == False:
            search_by_areas(params, childs)
        del params['area']
    return None
        
def search_by_metro(params):
    for value in metro_stations:
        params.update({'metro' : value})
        result = get_vacancy_id(params)
        if result == False:
            msg = 'All filters used but too many vacancies. Download first 2000'
            errors_log(msg)
            get_vacancy_id(params, '2000_limit')
        del params['metro']
    return None
    
def get_vacancy_id(params, limit = 'no_limit'):
    for page in range(20):
        url, params = hh_requests.requests_pattern(params, page)
        req = hh_requests.send_request(url, params)
        json_data = req.json()
        
        total_vacancies = json_data['found']
        total_pages = json_data['pages']
        if page == 0:
            print(f"Vacancies: {total_vacancies} Pages: {total_pages}")	
            
        if total_vacancies > 1950 and limit == 'no_limit':
            print(f'adding new filter')
            return False
        else:
            pass
            
        new_ids = select_actual_id(json_data['items'])
        L = len(new_ids)
        if L > 0:
            print(f'page: {page+1} New jobs: {L}')
            download(new_ids)
        elif L == 0:
            print(f'Nothing or too old jobs. Skip.')
        
        if page == (total_pages -1):
            break
    return True

def select_actual_id(jobs):
    new_ids = []
    for job in jobs:
        dates = [job['published_at'], job['created_at']]
        #parse non-isoformat dates
        dt_dates = [dateutil.parser.parse(dt) for dt in dates if dt != None]
        dt_dates.sort()
        newest = dt_dates[-1]
        id = int(job['id'])
        if newest < last_etl_utc and id in jobs_id: 
            pass
        else: 
            new_ids.append(id)        
    return new_ids    
 
def download(new_ids):
    N = 0
    vacancy_cash = []    
    print(f'Vacancy: ', end = '')
    for vac_id in new_ids:
        url, params = hh_requests.requests_pattern(id = vac_id)
        json_data = hh_requests.send_request(url, params).json()
        N += 1
        print(f'{N} ', sep=' ', end='', flush=True)
        vacancy = parse_json.parse_vacancy(json_data) #@@@@@
        vacancy_cash.append(vacancy)
    #print(f'\nTotal: {vacancy_count}')

    #load jobs to database
    ins_count, upd_count  = db_operations.drop_to_db(vacancy_cash, jobs_id)
    vacancy_insert = vacancy_insert + ins_count
    vacancy_update = vacancy_update + upd_count

def errors_log(err_msg):
    time_now = datetime.now(tzlocal).replace(microsecond = 0).isoformat()
    with open(err_path, 'a') as file: 
        file.write(f'{time_now} {err_msg}\n')
            
if __name__ == '__main__':
    main()
			

