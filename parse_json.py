import sys
import configparser
import pickle
from pathlib import Path
from dateutil.tz import tzutc, tzlocal
from datetime import datetime

tzlocal = tzlocal()
tzutc = tzutc()

#read parser configs
config = configparser.ConfigParser()
config.read(Path(sys.path[0], 'pipeline.conf'))
dt_format = config['parser_config']['date_format']
date_filename_format = config['parser_config']['date_filename_format']
logs_folder = Path(sys.path[0], config['parser_paths']['logs_folder'])
err_path = Path(logs_folder, config['parser_paths']['errors_file']) 

#read useless keys to delete
conf_keys = configparser.ConfigParser()
conf_keys.read(Path(sys.path[0], 'useless_keys.conf'))
main_keys = conf_keys.get('main_keys', 'keys').split()
client_keys = conf_keys.get('subkeys', 'client').split()

#===DATA BASE
#table_name = 'jobs'

MAIN_TABLE_1rang_structure = {#'id' column created with table as PRIMARY KEY
'occupations_category':'TEXT',
'occupations_subcategories':'TEXT',#Check for number of subcategories (usually 1)!!!!
'occupations_oservice':'TEXT',
'title':'TEXT',
'description':'TEXT',               
'Label':'TEXT',                     # My Label for classifier
'type':'INTEGER',                   #(JobType) 1-Fixed price, 2 - Hourly, 3 - Weekly Retainer (weekly pay to be
                                    #ready to get job in future)
'workType':'TEXT',                  #"Remote", "Permanent", "Occasional"
'duration':'TEXT',                  #weeks - "Less than 1 month"/ months - "1 to 3 months"/ semester - "3 to 6 months"/ongoing - "more than 6 months"
'engagement':'TEXT',                #(workload) as needed: "Less than 30hrs/week" / full_time - "More than 10-30hrs/week"
'totalFreelancersToHire':'INTEGER', #Number of FL to hire
#=====Money===
'amount_currencyCode':'TEXT',       #USD
'amount_amount':'INTEGER',          #Budget (fixed price)
'hourlyBudget_amount':'TEXT',       #$/hour payment
'weeklyBudget_currencyCode':'TEXT',
'weeklyBudget_amount':'INTEGER',    #$/week payment
#=====Client===
'skills_number':'INTEGER',
'skills_all':'BLOB',                #all skills (over 100 per some jobs and up to 6000 total) stored by pickle
'tier':'TEXT',                      #"Entry level", "Intermediate", "Expert"
'enterpriseJob':'INTEGER',          #0 - False/ 1- True
'client_paymentVerificationStatus':'INTEGER', #0-5 WTF????
'client_location':'TEXT',           #Client's country
'client_totalSpent':'INTEGER',
'client_totalReviews':'INTEGER',
'client_totalFeedback':'INTEGER',
'client_edcUserId':'INTEGER',       #Client Odesk id
'client_companyOrgUid':'TEXT',      #Client's Company id
'client_hasFinancialPrivacy': 'INTEGER',# 0 /1 WTF????
'client_USA_city':'TEXT',           #USA city? 1 value (arount values 190 total)
'category2_uid': 'INTEGER',
'subcategory2_uid': 'INTEGER',

#=====Trash?===
'teamUid':'INTEGER',
'premium':'INTEGER',                # 0 /1 WTF????
'freelancersToHire':'INTEGER',
'recno':'INTEGER',
'prefFreelancerLocation_number':'INTEGER',
'prefFreelancerLocation_all':'BLOB', #all locations (over 10 per job and up to 210 total) stored by pickle
'ciphertext':'TEXT',                # WTF???? may be delete?
'createdOn':'TEXT',
'jobTs':'TEXT',                     #1588837356207
'proposalsTier':'TEXT',             #Number of proposals "Less than 5"(0-4), "5 to 10"(5-9), "10 to 15"(10-14), "15 to 20"(15-19), "20 to 50"(20-49), "50+"(*)
'publishedOn':'TEXT',
'renewedOn':'TEXT',
#=====Service===
'last_updated':'TEXT',
'tags':'TEXT',
'closed':'INTEGER'
}

#Category id, SubCategory id, Name
OldUIDsNames = [('531770282580668416', 0, 'Admin Support'),
 ('531770282580668416', '531770282584862724', 'Data Entry & Transcription Services'),
 ('531770282580668416', '531770282584862725', 'Virtual Assistance'),
 ('531770282580668416', '531770282584862726', 'Market Research & Product Reviews'),
 ('531770282580668416', '531770282584862728', 'Project Management'),
 ('531770282580668417', 0, 'Customer Service'),
 ('531770282580668417', '1484275072572772352', 'Community Management & Tagging'),
 ('531770282580668417', '531770282584862730', 'Customer Experience & Tech Support'),
 ('531770282580668418', 0, 'Web, Mobile & Software Dev'),
 ('531770282580668418', '1517518458442309632', 'Blockchain, NFT & Cryptocurrency'),
 ('531770282580668418', '531770282584862733', 'Web Development'),
 ('531770282580668418', '531770282589057024', 'Mobile Development'),
 ('531770282580668418', '531770282589057025', 'Desktop Application Development'),
 ('531770282580668418', '531770282589057026', 'Ecommerce Development'),
 ('531770282580668418', '531770282589057027', 'Game Design & Development'),
 ('531770282580668418', '531770282589057028', 'Scripts & Utilities'),
 ('531770282580668418', '531770282589057029', 'Web & Mobile Design'),
 ('531770282580668418', '531770282589057030', 'Product Management'),
 ('531770282580668418', '531770282589057031', 'QA & Testing'),
 ('531770282580668418', '531770282589057032', 'Other - Software Development'),
 ('531770282580668419', 0, 'IT & Networking'),
 ('531770282580668419', '531770282589057033', 'Database Management & Administration'),
 ('531770282580668419', '531770282589057034', 'ERP/CRM Software'),
 ('531770282580668419', '531770282589057035', 'Network & System Administration'),
 ('531770282580668419', '531770282589057036', 'Information Security & Compliance'),
 ('531770282580668419', '531770282589057037', 'DevOps & Solutions Architecture'),
 ('531770282580668420', 0, 'Data Science & Analytics'),
 ('531770282580668420', '531770282589057038', 'Data Mining & Management'),
 ('531770282580668420', '531770282589057039', 'Data Design & Visualization'),
 ('531770282580668420', '531770282593251329', 'AI & Machine Learning'),
 ('531770282580668420', '531770282593251330', 'Data Analysis & Testing'),
 ('531770282580668420', '531770282593251331', 'Data Extraction/ETL'),
 ('531770282580668421', 0, 'Design & Creative'),
 ('531770282580668421', '1044578476142100480', 'Branding & Logo Design'),
 ('531770282580668421', '1356688560628174848', 'NFT, AR/VR & Game Art'),
 ('531770282580668421', '1356688565288046592', 'Performing Arts'),
 ('531770282580668421', '1356688570056970240', 'Video & Animation'),
 ('531770282580668421', '531770282593251334', 'Graphic, Editorial & Presentation Design'),
 ('531770282580668421', '531770282593251335', 'Art & Illustration'),
 ('531770282580668421', '531770282593251340', 'Photography'),
 ('531770282580668421', '531770282593251341', 'Audio & Music Production'),
 ('531770282580668421', '531770282601639953', 'Product Design'),
 ('531770282580668422', 0, 'Sales & Marketing'),
 ('531770282580668422', '531770282593251343', 'Marketing & Brand Strategy'),
 ('531770282580668422', '531770282597445632', 'Email & Marketing Automation'),
 ('531770282580668422', '531770282597445634', 'Lead Generation & Telemarketing'),
 ('531770282580668422', '531770282597445636', 'Display Advertising'),
 ('531770282580668422', '531770282597445638', 'SEO & SEM Services'),
 ('531770282580668422', '531770282597445639', 'Social Media & PR Services'),
 ('531770282580668423', 0, 'Writing'),
 ('531770282580668423', '1301900640421842944', 'Content & Copywriting'),
 ('531770282580668423', '531770282597445644', 'Editing & Proofreading Services'),
 ('531770282580668423', '531770282597445645', 'Creative Writing Services'),
 ('531770282580668423', '531770282597445646', 'Technical Writing'),
 ('531770282580668423', '531770282601639936', 'Grant & Proposal Writing'),
 ('531770282580668423', '531770282601639937', 'Resumes & Cover Letters'),
 ('531770282580668423', '531770282601639938', 'Other - Writing'),
 ('531770282584862720', 0, 'Translation'),
 ('531770282584862720', '531770282601639939', 'Translation & Localization'),
 ('531770282584862720', '531770282601639940', 'Legal, Medical & Technical Translation'),
 ('531770282584862721', 0, 'Accounting & Consulting'),
 ('531770282584862721', '531770282601639943', 'Accounting & Bookkeeping'),
 ('531770282584862721', '531770282601639944', 'Management Consulting & Analysis'),
 ('531770282584862721', '531770282601639945', 'Financial Planning'),
 ('531770282584862721', '531770282601639946', 'Human Resources'),
 ('531770282584862721', '531770282601639947', 'Other - Accounting & Consulting'),
 ('531770282584862722', 0, 'Engineering & Architecture'),
 ('531770282584862722', '1301900647896092672', 'Physical Sciences'),
 ('531770282584862722', '531770282601639948', '3D Modeling & CAD'),
 ('531770282584862722', '531770282601639949', 'Buildings & Landscape Architecture'),
 ('531770282584862722', '531770282601639950', 'Civil & Structural Engineering'),
 ('531770282584862722', '531770282601639951', 'Electrical & Electronic Engineering'),
 ('531770282584862722', '531770282601639952', 'Energy & Mechanical Engineering'),
 ('531770282584862722', '531770282605834240', 'Chemical Engineering'),
 ('531770282584862722', '531770282605834241', 'Contract Manufacturing'),
 ('531770282584862722', '531770282605834242', 'Interior & Trade Show Design'),
 ('531770282584862723', 0, 'Legal'),
 ('531770282584862723', '1484275156546932736', 'International & Immigration Law'),
 ('531770282584862723', '1484275408410693632', 'Public Law'),
 ('531770282584862723', '531770282605834246', 'Corporate & Contract Law'),
 ('531770282584862723', '531770283696353280', 'Finance & Tax Law')]             

def CategoriesCheck(json_PyObj, err_log):
    occupations = json_PyObj['searchResults']['facets']['occupations']
    NewUIDsNames = []
    for cat in occupations:
        catUid = cat["uid"]
        NewUIDsNames.append((catUid, 0, cat["label"]))
        subCats = cat["occupations"]
        for subCat in subCats:
            NewUIDsNames.append((catUid, subCat["uid"], subCat["label"]))

    A = set(OldUIDsNames)
    B = set(NewUIDsNames)
    #File to copy and update structure:
    #with open(sys.path[0] + '\\tmp.txt', 'a') as file: 
    #   for row in A: file.write(str(row) + ',' + '\n')
    
    DiffA = A - B #some OLD cats Deleted
    DiffB = B - A #some NEW cats Added
    if len(DiffA) == 0 and len(DiffB) == 0: pass
    else: 
        result1 = []
        for i in DiffA:
            Uid_O, subUid_O, Label_O = i
            Uid_tmp, subUid_tmp, Label_tmp = '-', '-', '-'
            for j in B:
                Uid_N, subUid_N, Label_N = j
                found = False
                if Uid_O == Uid_N and subUid_O == subUid_N: found = True #change Label
                elif Uid_O == Uid_N and Label_O == Label_N: found = True #change subUid
                elif subUid_O == subUid_N and Label_O == Label_N: found = True #change  Uid
                elif subUid_O == subUid_N: found = True #change Uid and Label
                if found == True:
                    Uid_tmp, subUid_tmp, Label_tmp = Uid_N, subUid_N, Label_N
            result1.append((Uid_O, subUid_O, Label_O, Uid_tmp, subUid_tmp, Label_tmp)) #(OLD, OLD, OLD, NEW, NEW, NEW)
        result2 = []
        for i in DiffB:
            Uid_N, subUid_N, Label_N = i
            Uid_tmp, subUid_tmp, Label_tmp = '-', '-', '-'
            for j in A:
                Uid_O, subUid_O, Label_O = j
                found = False
                if Uid_O == Uid_N and subUid_O == subUid_N: found = True #change Label
                elif Uid_O == Uid_N and Label_O == Label_N: found = True #change subUid
                elif subUid_O == subUid_N and Label_O == Label_N: found = True #change  Uid
                elif subUid_O == subUid_N: found = True #change Uid and Label
                if found == True:
                    Uid_tmp, subUid_tmp, Label_tmp = Uid_O, subUid_O, Label_O
            result2.append((Uid_tmp, subUid_tmp, Label_tmp, Uid_N, subUid_N, Label_N)) #(OLD, OLD, OLD, NEW, NEW, NEW)
        result = set(result1 + result2)

        time = datetime_to_str(now_local(), '%d.%m.%Y %H.%M')
        with open(err_log, 'a') as file: 
            file.write(time + '\n' + '(!) Uids and Labels changed:\n')
            for row in result: file.write(str(row) + ',' + '\n')
        #save json to hard drive
        import json, sys
        with open(f'{sys.path[0]}\Log\{time}.json', 'w') as f: json.dump(json_PyObj, f)
    
def get_jobs(json_data):
    jobs = json_data['searchResults']['jobs']
    return jobs
    
def total_jobs(json_data):
    total = json_data['searchResults']['paging']['total']
    return total
    
def jobs_by_occupations(json_data):
    occupations = json_data['searchResults']['facets']['occupations']
    return occupations
    
def delete_useless_keys(jobs):
    for job in jobs:
        for key in main_keys: job.pop(key)
        for key in client_keys: job['client'].pop(key)
    return jobs

#Downgrade json to 1 lvl complexity    
def downgrade_structure(jobs):
    for job in jobs:
        try:
            #Setting UTC time
            job['last_updated'] = datetime.strftime(datetime.now(tzutc), "%Y-%m-%dT%H:%M:%S%z")
            #Setting id
            job['id'] = int(job['uid'])
            job.pop('uid')
            #Ammount
            job['amount_currencyCode'] = job['amount']['currencyCode']
            job['amount_amount'] = job['amount']['amount']
            job.pop('amount')
            #WeeklyBudget
            if 'weeklyBudget' in job:
                if type(job['weeklyBudget']) == dict: 
                    job['weeklyBudget_currencyCode'] = job['weeklyBudget'].get('currencyCode', None)
                    job['weeklyBudget_amount'] = job['weeklyBudget'].get('amount', None)
                job.pop('weeklyBudget')
            #HourlyBudget   
            if 'hourlyBudgetText' in job: 
                job['hourlyBudget_amount'] = job['hourlyBudgetText']
                job.pop('hourlyBudgetText')
            #Occupations category
            job['occupations_category'] = job['occupations']['category']['prefLabel']
            job['category2_uid'] = job['occupations']['category']['uid']
            #Occupations subcategories
            if len(job['occupations']['subcategories']) > 1:
                print(f'Attention!!\njob id = {job["id"]}\n Number of "subcategories" in "occupations" >1')
            job['occupations_subcategories'] = ('+').join([subcat['prefLabel'] for subcat in job['occupations']['subcategories']])
            job['subcategory2_uid'] = ('+').join([subcat['uid'] for subcat in job['occupations']['subcategories']])
            #Occupations oservice
            if type(job['occupations']['oservice'])== dict: 
                job['occupations_oservice'] = job['occupations']['oservice']['prefLabel']
            job.pop('occupations')
            #Client
            for key in job['client'].keys():
                new_key = 'client' +'_'+ key
                if key == 'location': 
                    job[new_key] = job['client']['location']['country']
                else: 
                    job[new_key] = job['client'][key]
            job.pop('client')
            #EnterpriceJob
            if job['enterpriseJob'] == False:
               job['enterpriseJob'] = 0
            elif job['enterpriseJob'] == True:
                job['enterpriseJob'] = 1
            #Locations
            if len(job['locations']) != 0:
                job['client_USA_city'] = job['locations'][0]['name']
            else: 
                job['client_USA_city'] = None
            job.pop('locations')
            #FreelancersLocation
            N = len(job['prefFreelancerLocation'])
            job['prefFreelancerLocation_number'] = N
            if N > 0:
                job['prefFreelancerLocation_all'] = pickle.dumps(job['prefFreelancerLocation'])
            else: 
                job['prefFreelancerLocation_all'] = None
            job.pop('prefFreelancerLocation')
            #Skills
            Na = len(job['attrs'])
            job['skills_number'] = Na
            if Na >0:
                skills_All = [] 
                for skill in job['attrs']: 
                    skills_All.append(skill['prettyName'])
                job['skills_all'] = pickle.dumps(skills_All)
                #print(pickle.loads(job['skills_all'])) #command to Load skills 
            else: 
                job['skills_all'] = None
            job.pop('attrs')
            #Tags
            if 'tags' in job:
                if job['tags'] == []: 
                    job['tags'] = None
                else:
                    job['tags'] = ','.join(job['tags'])
                    
        except Exception as e:
            import sys
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(f"Downgrade error in line:{exc_tb.tb_lineno}\n{e}\n title:{job['title']})")
            dump_json(job) 

        #eqiualizing jobs structure to BD structure
        for key in MAIN_TABLE_1rang_structure:
            if key not in job: 
                job[key] = None
                
        #converting boolean to integer 
        #due to previpus SDB SQLight doesn't support boolean.
        for key, value in job.items():
            if value == True:
                job[key] = 1
            elif value == False:
                job[key] = 0
            else:

                pass
                
        #Checking for new keys that can be added by Upwork
        NewKeys = (set(job.keys()) - set(MAIN_TABLE_1rang_structure.keys())) - {'id'}         
        if len(NewKeys) != 0:
            print(f'Attention! New keys in job (id = {job["id"]}):')
            for key in  NewKeys:
                print(f'- {key} : {type(job[key])}')
            dump_json(job)
    return jobs
    
def dump_json(job):
    # import json
    # time = datetime.strftime(datetime.now(tzlocal), date_filename_format)#datetime obj to str
    # dump_path = Path(logs_folder, f'{time}.json')
    # with open(dump_path, 'w') as f:
        # json.dump(job, f)
    # print(f'Saved json to: {dump_path}')
    input('Press any key to continue.')  
    
if __name__ == '__main__':
    #pass
    import json, time
    path_from = r'D:\Shapovalov\svoe\Python\PY\Raw_Jsons\01.11.2021 06.42'
    
    path_to = r'D:\Shapovalov\svoe\Python\PY\DB_Upwork\jobs.sqlite3'#Upwork jobs
    #path_to = r'D:\Shapovalov\svoe\Python\PY\Parser3\MyLibs\Test\test_SQLbase.sqlite3'
    #path_to = r'D:\Shapovalov\svoe\Python\PY\DB_Upwork\24_05.sqlite3'#Upwork jobs
    
    #Connect    
    db = MyLibs.SQLite.connect(path_to)
    #MyLibs.SQLite.BackUp(db, BackUp_path = r'D:\Shapovalov\svoe\Python\PY\DB_Upwork\back_up.sqlite3')
    #print("DB backup done: %s")
    
    ##Delete table
    #MyLibs.SQLite.Delete_Table(table_name, db)
    #Create Table for Upwork DB
    #Create(table_name, MAIN_TABLE_1rang_structure, db)

    #=======with 1 JSON file
    # file = r'D:\Shapovalov\svoe\Python\PY\Raw_Jsons\old_jobs\1.json'
    # File_list = [file]
        
    #=======with JSON all files
    import MyLibs.Scan_DirsFiles
    File_list, _ = MyLibs.Scan_DirsFiles.DirScanPaths(path_from)
    print('File_List', len(File_list))
    input('Press any key')
    
    Total_DB = []
    start0 = time.time()
    for file in File_list:
        try:
            js = open(file)
            json_data = js.read()
            js.close()
            json_PyObj = json.loads(json_data)
            jobs = delete_useless_keys(json_PyObj)
            jobs = Downgrade(jobs)
            assert jobs != None, f'jobs == None in {file}'
        except Exception as e:
            print(f"{file}\n{e}")
            input('Press any key')
        Total_DB.append(jobs)
    print("All jobs readed from files: %s" % (time.time() - start0))
    
    result = {'insert': 0, 'update': 0}
    start1 = time.time()
    for jobs in Total_DB:   
        insert, update = DropToDB(jobs, db)
        result['insert'] = result['insert'] + insert
        result['update'] = result['update'] + update
        print(f"Result: {result['insert']} jobs inserted, {result['update']} jobs updated")
    print(f"Total {result['insert'] + result['update']} jobs: {result['insert']} jobs inserted, {result['update']} jobs updated")
    db.close()  
    print('Done!!')
    delta = round((time.time() - start1))//60
    print(f"DB dumped in {delta} minutes")
    
    
