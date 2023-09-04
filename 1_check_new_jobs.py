#In case of faults:
#0) clear browser's cookies (status code 502)
#1) check user_agent in browser (may be it changes after browser update)
#2) function that generates requests (Upwork changes it frequently)
#3) check Headers in requests_upwork and browsers Header 

import configparser
import sys, os
import traceback
from pathlib import Path
from dateutil.tz import tzutc, tzlocal
from datetime import datetime, timedelta
tzlocal = tzlocal()
tzutc = tzutc()

import common_functions
import db_operations
import ip_check
import requests_upwork

#================General settings=========================
config = configparser.ConfigParser()
config.read(Path(sys.path[0], 'pipeline.conf'))

proxy = config['parser_config']['proxy']
dt_format = config['parser_config']['date_format']

logs_folder = Path(sys.path[0], config['parser_paths']['logs_folder'])
journal_path = Path(logs_folder, config['parser_paths']['journal_file'])
ip_log_path = Path(logs_folder, config['parser_paths']['ip_file'])
err_path = Path(logs_folder, config['parser_paths']['errors_file'])

def check_new_jobs():
    #datetime of last successfull ingestion
    try:
        with open(journal_path) as file:
            result = file.read().split('\n')
        journal_recs = [i for i in result if i != '']
    except FileNotFoundError as e:
        print(f'{journal_path} not found.')
        journal_recs = ['01.01.1970 00.00']
    last_check_dt = datetime.strptime(journal_recs[-1], dt_format) #convert str to datetime obj
    last_check_loc = last_check_dt.astimezone(tzlocal)#add local timezone
    last_check_utc = last_check_dt.astimezone(tzutc) #add utc timezone
    print('last check (local):', datetime.strftime(last_check_loc, dt_format))
    
    #check if proxy enabled
    ip_adress.check() 
    
    #check if file with requests already exists
    req_list, _ = common_functions.read_request_list()
    if req_list:
        print(f'There are requests to download already. Exit.')
        return None
    else:
        pass
 
    #check for new jobs and form list of requests
    start_url = requests_upwork.requests_pattern(page = 'start')
    errors = 0
    try:
        print(f'Desision: ', end=' ')
        url_p90 = requests_upwork.requests_pattern(page = 90)
      
        req = requests_upwork.send_request(url_p90, start_url)
        json_data = req.json()  
        start_url = url_p90

        jobs = json_data['searchResults']['jobs']
        
        time_start = datetime.strftime(datetime.now(tzlocal), dt_format)#datetime obj to str
       
        checkpoint = last_check_utc - timedelta(minutes = 120) #to check dates of the jobs on page 90
        jobs_id = db_operations.id_from_db()
        actual_jobs = common_functions.select_actual_jobs(jobs, checkpoint, jobs_id)
        if len(actual_jobs) == 0:
            print(f'Refresh.')
            req_list = [[requests_upwork.requests_pattern(i) for i in range(1,100)]]
        else:
            print(f'FullUpdate.')
            req_list, _ = requests_upwork.form_requests_list(json_data, start_url) 

        req_path = Path(logs_folder, f'{time_start}_requests.log')
        common_functions.write_request_list(req_list, req_path)
        
        N_req = sum([len(list) for list in req_list])
        print(f'Ready to download: {N_req} requests')
          
    except Exception:
        e = traceback.format_exc()
        print(e)
        errors += 1
        time_now = datetime.strftime(datetime.now(tzlocal), dt_format)#datetime obj to str
        with open(err_path, 'a') as file: 
            file.write(time_now + '\n' + str(e) + '\n')
    finally:
        if errors > 10:
            input('Paused. Press any key.')
            errors = 0
 
if __name__ == '__main__':
    check_new_jobs()
    # while True:
        # try:
            # check_new_jobs()
        # except KeyboardInterrupt:
            # exit(1)
        # except SystemExit as e:
            # time_now = datetime.strftime(datetime.now(tzlocal), dt_format)#datetime obj to str
            # with open(err_path, 'a') as file: 
                # file.write(time_now + '\n' + str(e) + '\n')
            

