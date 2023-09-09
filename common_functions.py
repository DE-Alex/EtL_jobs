import sys
import os
import glob
from pathlib import Path
from datetime import datetime

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
            groups = file.read().split('\n***\n')
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
    result = ('\n***\n').join([('\n').join(req_group) for req_group in req_list])
    try:    
        with open (req_path, 'w') as file:
            file.write(result)
    except:
        with open (req_path, 'w', encoding = 'utf-8') as file:
            file.write(result)

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
    pass