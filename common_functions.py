#import py_object_to_file as pyfile
import configparser
import sys
import psycopg
import os
import glob
from pathlib import Path
from datetime import datetime, timedelta

config = configparser.ConfigParser()
config.read(Path(sys.path[0], 'pipeline.conf'))

dbname = config["postgres_config"]["database"]
user = config["postgres_config"]["username"]
password = config["postgres_config"]["password"]
host = config["postgres_config"]["host"]
port = config["postgres_config"]["port"]
table_name = config['upwork']['upwork_table']

#Change work dir, Scan it (without subdirs!) for file and dirs NAMES, and change work dir back
#MASK: * - any symbols, ? - one symbol, [0-9], [?] or [8] - ? or * 
def DirScanByMask(f_path, mask): 
    temp = os.getcwd()
    os.chdir(f_path)
    file_names = []
    for name in glob.glob(mask):
        if os.path.isfile(os.path.join(f_path, name)):
            file_names.append(name)
        else:
            pass
    os.chdir(temp)
    return file_names

def read_request_list(temp_folder, mask):
    req_list, file_path = False, False
    
    file_names = DirScanByMask(temp_folder, f'*{mask}')
    for filename in file_names:
        file_path = Path(temp_folder, filename)
        with open(file_path) as file:
            groups = file.read().split('***')
        req_list = [i.split('\n') for i in groups if i != '']
        
        if len(req_list) > 0:
            return req_list, file_path
        else:
            os.remove(file_path)
            req_list, file_path = False, False
    return req_list, file_path
    
def write_request_list(req_list, req_path):
    directory = os.path.dirname(req_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    try:    
        with open (req_path, 'w') as file:
            for rec_group in req_list:
                group_to_dump = ('\n').join(rec_group)
                file.write(f'{group_to_dump}\n***\n')
    except:
        with open (req_path, 'w', encoding = 'utf-8') as file:
            for rec in req_list:
                group_to_dump = ('\n').join(rec_group)
                file.write(f'{group_to_dump}\n***\n')


#Upwork orders jobs in Recent List by 'createdOn'.
#So if some job is renewed ('renewedOn') it is not come into the beginning of the List.
#Parser can find such job, add to actualJobs and begin FullUpdate.
def select_actual_jobs(jobs, checkpoint, jobs_id):
    actualJobs = []
    for job in jobs:
        dates = [job['createdOn'], job['publishedOn'], job['renewedOn']]
        dt_dates = [datetime.fromisoformat(item) for item in dates if item != None]
        dt_dates.sort()
        dt_newest = dt_dates[-1]
        id = int(job['uid'])
        if dt_newest < checkpoint and id in jobs_id: 
            pass
        else: 
            actualJobs.append(job)
    return actualJobs
    
if __name__ == '__main__':

    path = 'D:\Shapovalov\svoe\Python\PY\Parser6\Temp'
    mask = 'requests.log'
    a, res = read_request_list(path, f'*{mask}')
    if a:
        print(res)
    print(len(a))
    input()

    jobs_id = id_from_db()
    print('len:', len(jobs_id))
    for id in jobs_id:
        print(id)
        input()
