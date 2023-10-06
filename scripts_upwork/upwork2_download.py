#In case of faults:
#0) clear browser's cookies (status code 502)
#1) check user_agent in browser (may be it changes after browser update)
#2) function that generates requests (Upwork changes it frequently)
#3) check Headers in requests_upwork and browsers Header 

import configparser
import sys, os
import traceback
import time
from pathlib import Path
from datetime import datetime, timedelta
from dateutil.tz import tzutc, tzlocal
tzlocal = tzlocal()
tzutc = tzutc()

import common_functions
import db_operations
import ip_adress
import requests_upwork
import parse_json

parent_dir = os.path.abspath(os.path.join(sys.path[0], '..'))
config = configparser.ConfigParser() 
config.read(Path(parent_dir, 'pipeline.conf'))

filename_date_format = config['general']['filename_date_format']
temp_folder = Path(parent_dir, config['general']['temp_folder'])
logs_folder = Path(parent_dir, config['general']['logs_folder'])

proxy = config['upwork']['proxy']
requests_filename = config['upwork']['requests_file']
journal_path = Path(logs_folder, config['upwork']['journal_file'])
err_path = Path(logs_folder, config['upwork']['errors_file']) 

dbname = config.get('postgres_config', 'database')
user = config.get('postgres_config', 'username')
password = config.get('postgres_config', 'password')
host = config.get('postgres_config', 'host')
port = config.get('postgres_config', 'port')
table_name = config.get('db_scheme', 'upwork_table')
  
def download_jobs():
    #search for file with requests (urls to download)
    req_list, req_path = common_functions.read_request_list(temp_folder, requests_filename)
    if req_list:
        N_reqs = sum([len(list) for list in req_list])
        req_list_date = datetime.strptime(req_path.name, filename_date_format + requests_filename)
        print(f'Request list from: {req_list_date}')
    else:
        print(f'There is no requests to download. Exit.')
        return None
        
    #check if proxy enabled
    ip_adress.check_ip()         
    
    #datetime of last successfull ingestion
    try:
        with open(journal_path) as file:
            result = file.read().split('\n')
        journal_recs = [i for i in result if i != '']
    except FileNotFoundError as e:
        print(f'{journal_path} not found')
        journal_recs = ['01.01.1970 00.00']
        
    last_check_loc = datetime.fromisoformat(journal_recs[-1])
    last_check_utc = last_check_loc.astimezone(tzutc) #move to utc timezone    
        
    previous_url = requests_upwork.requests_pattern(page = 'start')
    
    #download jobs by requests
    print(f'Requests to download: {N_reqs}')
    try:
        downl_cnt = {'insert': 0, 'update': 0}
        start = time.time()
        for requests in req_list:
            while len(requests) !=0:
                N_reqs = sum([len(list) for list in req_list])
                url = requests[0]
                req = requests_upwork.send_request(url, previous_url)
                json_data = req.json()
                #save json to hard drive @@@@@@@@@@@@@@@
                # import json
                # with open(f'{sys.path[0]}\Temp\{N_reqs}.json', 'w') as f: 
                    # json.dump(json_data, f)
                
                previous_url = url
                print(f'{N_reqs} - OK', end=' ')
                
                checkpoint = last_check_utc - timedelta(minutes = 5)
                jobs_id = db_operations.id_from_db()
                jobs_raw = parse_json.get_jobs(json_data)
                actual_jobs = common_functions.select_actual_jobs(jobs_raw, checkpoint, jobs_id)

                if len(actual_jobs) == 0:
                    print(f'Too old jobs. Skip the rest')
                    del requests[:]
                else:
                    jobs_cleared = parse_json.delete_useless_keys(jobs_raw)
                    db_columns = db_operations.col_names_from_db()
                    jobs = parse_json.downgrade_structure(jobs_cleared, db_columns)
               
                    #sorting jobs to insert or update
                    ins_count, upd_count, new_id = db_operations.drop_to_db(jobs, jobs_id)
                    downl_cnt['insert'] = downl_cnt['insert'] + ins_count
                    downl_cnt['update'] = downl_cnt['update'] + upd_count
                    print(f"Result: {downl_cnt['insert']}(+{ins_count}) inserted, {downl_cnt['update']}(+{upd_count}) updated")
                    jobs_id.extend(new_id)
                    del requests[0]
            common_functions.write_request_list(req_list, req_path)
        
        etl_date = req_list_date.replace(microsecond = 0).isoformat()#datetime to str in isoformat 
        journal_recs = ('\n').join([etl_date] + journal_recs[:300])
        with open(journal_path, 'w') as file: 
            file.write(journal_recs)        
        os.remove(req_path)
        print(f"Total: {downl_cnt['insert']} inserted, {downl_cnt['update']} updated")
        delta = round((time.time() - start))//60
        print(f"Downloaded in {delta} minutes")
    except Exception:
        e = traceback.format_exc()
        print(e)
        time_now = datetime.now(tzlocal).replace(microsecond = 0).isoformat()#datetime to str in isoformat 
        with open(err_path, 'a') as file: 
            file.write(time_now + '\n' + str(e) + '\n')

if __name__ == '__main__':
        download_jobs()
            

