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
filename_date_format = config['parser_config']['filename_date_format']
logs_folder = Path(sys.path[0], config['parser_paths']['logs_folder'])
err_path = Path(logs_folder, config['parser_paths']['errors_file']) 

#read useless keys to delete
conf_keys = configparser.ConfigParser()
conf_keys.read(Path(sys.path[0], 'useless_keys.conf'))
main_keys = conf_keys.get('main_keys', 'keys').split()
client_keys = conf_keys.get('subkeys', 'client').split()

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
def downgrade_structure(jobs, db_columns):
    for job in jobs:
        try:
            #Setting UTC time
            job['last_updated'] = datetime.now(tzutc).replace(microsecond = 0).isoformat()#datetime to str in isoformat 
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
            #job['subcategory2_uid'] = ('+').join([subcat['uid'] for subcat in job['occupations']['subcategories']])
            job['subcategory2_uid'] = [subcat['uid'] for subcat in job['occupations']['subcategories']][0]
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
        for key in db_columns:
            if key not in job: 
                job[key] = None
                
        #Checking for new keys that can be added by Upwork
        NewKeys = (set(job.keys()) - set(db_columns))     
        if len(NewKeys) != 0:
            print(f'Attention! New keys in job (id = {job["id"]}):')
            for key in  NewKeys:
                print(f'- {key} : {type(job[key])}')
            dump_json(job)
            
        #converting boolean to integer 
        #due to previous SDB SQLight doesn't support boolean.
        for key, value in job.items():
            if value == True:
                job[key] = 1
            elif value == False:
                job[key] = 0
            else:
                pass
    return jobs
    
def dump_json(job):
    import json
    time = datetime.strftime(datetime.now(tzlocal), filename_date_format)#datetime obj to str
    dump_path = Path(logs_folder, f'{time}.json')
    with open(dump_path, 'w') as f:
        json.dump(job, f)
    print(f'Saved json to: {dump_path}')
    
if __name__ == '__main__':
    pass

    
    
