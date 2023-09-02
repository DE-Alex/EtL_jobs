import py_object_to_file as pyfile

def jobs_id_from_db():
    conn = psycopg2.connect(
        "dbname=" + dbname
        + " user=" + user
        + " password=" + password
        + " host=" + host,
        port = port)
        
    id_query = f"SELECT id FROM {table_name};"
    cursor = conn.cursor()
    cursor.execute(id_query)
    results = cursor.fetchall()

    cursor.close()
    conn.close()
    
    jobs_id = [item[0] for item in result]
    return jobs_id

def select_actual_jobs(jobs, checkpoint, jobs_id):
    jobs_id = jobs_id_from_db()
    actualJobs = []
    for job in jobs:
        dates = [job['createdOn'], job['publishedOn'], job['renewedOn']]
        dt_dates = [datetime.fromisoformat(item) for item in dates if item != None]
        dt_dates.sort()
        dt_newest = dt_dates[-1]
        id = job['id']
        if dt_newest < checkpoint and id in jobs_id: 
            pass
        else: 
            actualJobs.append(job)
    return actualJobs



#упростить и отказаться?  
def SaveReqList(reqList): #Добавить path
    if reqList_log == None:
        now = datetime_to_str(now_local(), dt_format)
        reqList_log = rf'{tmp_fold}\{now}_requests.log'  #перенести в main?
    pyfile.Write(reqList, reqList_log) 
    
def ReadReqList():
    files, _ = MyLibs.Scan_DirsFiles.DirScanByMask(tmp_fold, '*_requests.log')
    if files == []: 
        reqList_log, reqList = None, None
    else: 
        for filename in files:
            path = rf'{tmp_fold}\{filename}'
            reqList = pyfile.Read(path)
            if reqList == None:
                os.remove(path)
                reqList_log = None
            else:
                reqList_log = path
    return reqList