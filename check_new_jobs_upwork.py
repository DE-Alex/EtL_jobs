#Если не работает то проверить:
#0) почистить куки браузера (status code 502)
#1) сверить user_agent с браузером (мог измениться после обновления браузера)
#2) генерацию запросов (Upwork часто меняет)
#3) сверить Headers в upw_requests с Header браузера

from pathlib import Path
import configparser
import sys
import pyscopg2 #pip install pyscopg2

import py_object_to_file as pyfile
import common_functions
import ip_check
import upw_requests
import traceback

import DB_Manager_Upwork

#================General settings=========================
#check = timedelta(minutes = 10) ->> Airflow


config = configparser.ConfigParser()
#pipe_conf = Path(Path.cwd(), 'pipeline.conf')
config.read('pipeline.conf')

user_agent = config.get('parser_config', 'user_agent')
proxy = config.get('parser_config', 'proxy')
dt_format = config.get('parser_config', 'date_format')
import MTM.change_mtm_headers #перенести в папку со скриптом?
MTM.change_mtm_headers.write_in(user_agent)

#можно ли утйти в относительный путь?
logs_folder = Path(sys.path[0], config.get('parser_config', 'logs_folder'))
errors = Path(logs_folder, config.get('parser_config', 'errors_file'))
journal_fl = Path(logs_folder, config.get('parser_config', 'journal_file'))
ip_fl = Path(logs_folder, config.get('parser_config', 'ip_file'))

tmp_folder = Path(sys.path[0], config.get('parser_config', 'tmp_folder'))

dbname = config.get("postgres_config", "database")
user = config.get("postgres_config", "username")
password = config.get("postgres_config", "password")
host = config.get("postgres_config", "host")
port = config.get("postgres_config", "port")
table_name = config.get('postgres_config', 'upwork_table')

def LoadJobs():
    #datetime of last successfull ingestion
    j_read = pyfile.Read(journal_log)
    if j_read == None: 
        journal_recs = ['01.01.1970 00.00']
    else: 
        journal_recs = j_read
    last_check_dt = local_to_utc(str_to_datetime(journal_recs[-1] , dt_format))
   
    #start_url = 'https://www.upwork.com/nx/jobs/search/?sort=recency'
    start_url = upw_requests.requests_pattern() #& на конце после recency

    errors = 0
    try:
        #lastCheck_dt_local = utc_to_local(last_check_dt)
        #print('last check (local):',lastCheck_dt_local.date(), lastCheck_dt_local.time())
        ip_check.test_ip(proxy, ip_log)

        print(f'Desision: ', end=' ')
        #url = f'https://www.upwork.com/ab/jobs/search/url?per_page=50&sort=recency&page=90'
        url = upw_requests.requests_pattern(page = 90)
        req = upw_requests.send_request(url, start_url, user_agent, err_log, proxy)
        json_data = req.json()  
        start_url = url
        
        #DB_Manager_Upwork.CategoriesCheck(json_data, err_log)
        Jobs = DB_Manager_Upwork.clear_Upwork_data(json_data)
        Jobs = DB_Manager_Upwork.Downgrade(Jobs)
        
        checkpoint = last_check_dt - check*10
        actualJobs = common_functions.select_actual_jobs(Jobs, checkpoint)
        if len(actualJobs) == 0:
            print(f'Refresh.')
            req_list = [[upw_requests.requests_pattern(i) for i in range(1,100)]]
        else:
            print(f'FullUpdate.')
            previous_url, req_list = upw_requests.form_requests_list(json_data, start_url, user_agent, err_log, proxy) 
            #start_url = previous_url
        now = datetime_to_str(now_local(), dt_format)
        req_path = Path(tmp_folder, f'{now}_requests.log')
        pyfile.Write(req_list, req_path)             
    except Exception:
        e = traceback.format_exc()
        print(e)
        errors += 1
        time_now = datetime_to_str(now_local(), dt_format)
        with open(err_log, 'a') as file: 
            file.write(time_now + '\n' + str(e) + '\n')
    finally:
        if errors > 10:
            input('Paused. Press any key.')
            errors = 0
 
if __name__ == '__main__':
    while True:
        try:
            L =  LoadJobs()
        except SystemExit as e:
            time_now = datetime_to_str(now_local(), dt_format)
            with open(err_log, 'a') as file: 
                file.write(time_now + '\n' + str(e) + '\n')
            

