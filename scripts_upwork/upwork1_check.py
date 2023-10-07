import configparser
import sys, os
import traceback
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
err_path = Path(logs_folder, config['upwork']['errors_file'])
journal_path = Path(logs_folder, config['upwork']['journal_file'])


def check_new_jobs():
    #check if file with requests already exists
    req_list, _ = common_functions.read_request_list(temp_folder, requests_filename)
    if req_list:
        print(f'There are requests to download already. Exit.')
        return None
    else:
        pass
        
    #datetime of last successfull ingestion
    try:
        with open(journal_path) as file:
            result = file.read().split('\n')            
    except FileNotFoundError:
        print(f'"{journal_path}" not found.')
        result = ['1970-01-01T00:00:00+03:00']
        
    journal_recs = [i for i in result if i != '']
    try:
        last_check_loc = datetime.fromisoformat(journal_recs[-1])
    except IndexError:
        print(f'"{journal_path}" read data error.')
        last_check_loc = datetime.fromisoformat('1970-01-01T00:00:00+03:00')
    last_check_utc = last_check_loc.astimezone(tzutc) #move to utc timezone
    print('last check (local):', datetime.strftime(last_check_loc, '%Y.%m.%d %H:%M'))
   
    #check if proxy enabled
    ip_adress.check_ip() 
 
    #check for new jobs and form list of requests
    start_url = requests_upwork.requests_pattern(page = 'start')
    errors = 0
    try:
        #request jobs from page 90
        url_p90 = requests_upwork.requests_pattern(page = 90)
        req = requests_upwork.send_request(url_p90, start_url)
        json_data = req.json()  
        start_url = url_p90
        jobs = parse_json.get_jobs(json_data)
        
        #check if there are new jobs on page 90
        checkpoint = last_check_utc - timedelta(minutes = 120) #to check dates of the jobs on page 90
        jobs_id = db_operations.id_from_db()
        actual_jobs = common_functions.select_actual_jobs(jobs, checkpoint, jobs_id)
            
        #download jobs
        time_start = datetime.now(tzlocal)    
        if len(actual_jobs) == 0:
            print(f'Refresh: download jobs from recent 100 pages.')
            req_list = [[requests_upwork.requests_pattern(i) for i in range(1,100)]]
        else:
            print(f'FullUpdate: crawl all jobs with filters')
            N_jobs = parse_json.total_jobs(json_data)
            print(f"Total {N_jobs} jobs found.")
            req_list, _ = requests_upwork.form_requests_list(json_data, start_url) 
        
        #save requests to file
        time_start_str = datetime.strftime(time_start.replace(microsecond = 0), filename_date_format) #datetime to str in filename format 
        req_path = Path(temp_folder, f'{time_start_str}{requests_filename}')
        common_functions.write_request_list(req_list, req_path)
        
        N_req = sum([len(list) for list in req_list])
        print(f'Ready to download: {N_req} requests')
    
    except SystemExit as e:
        print('Exit.')
    except Exception:
        e = traceback.format_exc()
        print(e)
        errors += 1
        time_now = datetime.now(tzlocal).replace(microsecond = 0).isoformat()#datetime to str in isoformat 
        with open(err_path, 'a') as file: 
            file.write(time_now + '\n' + str(e) + '\n')
    finally:
        if errors > 10:
            input('Paused. Press any key.')
            errors = 0
 
if __name__ == '__main__':
    check_new_jobs()

            

