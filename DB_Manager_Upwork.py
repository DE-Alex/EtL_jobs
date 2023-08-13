import MyLibs.SQLite
import pickle
from datetime import datetime, timezone
#===DATA BASE
DB_UPWORK = r'D:\Shxxxx\xxx\Python\PY\DB_Upwork\Jobs.sqlite3'#Upwork jobs
path = DB_UPWORK
table_name = 'Jobs'

MAIN_TABLE_1rang_structure = {#ID column created with table as PRIMARY KEY
'occupations_category':'TEXT',
'occupations_subcategories':'TEXT',#Check for number of subcategories (usually 1)!
'occupations_oservice':'TEXT',
'type':'INTEGER',					#(JobType) 1-Fixed price, 2 - Hourly
'workType':'TEXT', 					#"Remote", "Permanent", "Occasional"
'description':'TEXT',				#
'duration':'TEXT',					#weeks - "Less than 1 month"/ months - "1 to 3 months"/ semester - "3 to 6 months"/ongoing - "more than 6 months"
'engagement':'TEXT',				#(workload) as needed: "Less than 30hrs/week" / full_time - "More than 10-30hrs/week"
'title':'TEXT',
#=====Money===
'amount_currencyCode':'TEXT',		#USD
'amount_amount':'INTEGER',			#Budget (fixed price)
'hourlyBudget_amount':'TEXT', 		#$/hour payment
'weeklyBudget_currencyCode':'TEXT',
'weeklyBudget_amount':'INTEGER',	#$/week payment
#=====Client===
'skills_number':'INTEGER',
'skills_all':'BLOB', #all skills (over 100 per some jobs and up to 6000 total) stored by pickle
'tier':'TEXT',						#"Entry level", "Intermediate", "Expert"
'enterpriseJob':'INTEGER',			#0 - False/ 1- True
'client_paymentVerificationStatus':'INTEGER', #0-5 ?
'client_location':'TEXT',			#Client's country
'client_totalSpent':'INTEGER',
'client_totalReviews':'INTEGER',
'client_totalFeedback':'INTEGER',
'client_edcUserId':'INTEGER',		#Client Odesk ID
'client_companyOrgUid':'TEXT',		#Client's Company ID
'client_hasFinancialPrivacy': 'INTEGER',# 0 /1 ?
'client_USA_city':'TEXT',			#USA city? 1 value (arount values 190 total)

#=====Trash?===
'premium':'INTEGER',				# 0 /1 WTF????
'freelancersToHire':'INTEGER',
'recno':'INTEGER',
'prefFreelancerLocation_number':'INTEGER',
'prefFreelancerLocation_all':'BLOB', #all locations (over 10 per job and up to 210 total) stored by pickle
'ciphertext':'TEXT',				# may be delete?
'createdOn':'TEXT',
'jobTs':'TEXT',						#1588837356207
'proposalsTier':'TEXT',				#Number of proposals "Less than 5"(0-4), "5 to 10"(5-9), "10 to 15"(10-14), "15 to 20"(15-19), "20 to 50"(20-49), "50+"(*)
'publishedOn':'TEXT',
'renewedOn':'TEXT',
#=====Service===
'last_updated':'TEXT',				#Time in UTC format
'closed':'INTEGER'
}
def Connect_Upwork_DB():
	db = MyLibs.SQLite.connect(path)
	return db
					
def Create(table_name, table_columns, db):
	MyLibs.SQLite.Create_Table(table_name, 'ID', 'INTEGER', db, PrimaryKey = 'PRIMARY KEY')
	MyLibs.SQLite.AddColumnMany(table_name, table_columns, db)

def ReadJob(db, table_columns, ID):
	def Select(tab_name, db, select_col = '*', rule = ''):
	
	action = f'SELECT {select_col} FROM {tab_name} WHERE ID = {ID}'
	
	
	
def DropToDB(Jobs, db):
	assert type(Jobs) == list, 'DropToDB: Invalid type of input "Jobs" (non list)'
	result = MyLibs.SQLite.Select(table_name, db, 'ID')
	ID_list = [item[0] for item in result]
	Jobs_to_insert = [job for job in Jobs if job['ID'] not in ID_list]#collect jobs to insertMany
	Jobs_to_update = [job for job in Jobs if job['ID'] in ID_list] #collect jobs to updateMany
	ID_to_insert = [{'ID':job['ID']} for job in Jobs if job['ID'] not in ID_list]
	
	insert_count = len(Jobs_to_insert)
	update_count = len(Jobs_to_update)
	if insert_count !=0: MyLibs.SQLite.InsertMany(table_name, Jobs_to_insert, db)
	if update_count !=0: MyLibs.SQLite.UpdateManyByID(table_name, Jobs_to_update, db)
	return insert_count, update_count

		
def clear_Upwork_data(json_PyObj):
	assert type(json_PyObj) == dict, 'clear_Upwork_data: Invalid type of input data (non dict)'
	try:
		Jobs = json_PyObj['searchResults']['jobs']
	except KeyError as e:
		print(e)
		return
	assert type(Jobs) == list, 'clear_Upwork_data: Invalid type of input "Jobs" (non list)'
		
	Useless_keys = ['shortDuration',
					'durationLabel',
					'shortEngagement',
					'relevanceEncoded',
					'tierText',				#:'TEXT',
					'tierLabel',			#:'TEXT',
					'sticky',				#:'INTEGER',#0 - False/ 1- True
					'stickyLabel',			#:'TEXT',	#Label "Interesting Job"
					'isSaved',				#:'TEXT',
					'occupation',			#:'TEXT',
					'plusBadge',			#:'TEXT',
					'sandsAttrs',			#:'TEXT',
					'sandsService',			#:'TEXT',
					'sandsSpec',			#:'TEXT',
					'subcategory2',			#:'TEXT',
					'category2',			#:'TEXT',
					'feedback',				#:'TEXT',
					'isApplied',			#:'INTEGER',# 0 WTF????
					'isLocal',				#:'INTEGER',# 0 /1 WTF????
					'prefFreelancerLocationMandatory']	#:'INTEGER', # 0 (False) /1 (True) limit to Freelancer Location

	Useless_subkeys = ['companyRid',		#:'INTEGER'
					'companyName',			#:'TEXT'
					'lastContractPlatform',	#:'TEXT'
					'lastContractRid',		#:'INTEGER'
					'lastContractTitle',	#:'TEXT'
					'feedbackText']			#:'TEXT'
	
	for job in Jobs:
		for key in Useless_keys: job.pop(key)
		for key in Useless_subkeys: job['client'].pop(key)
	return Jobs

	
def Downgrade(Jobs):
	#Downgrade data to 1 lvl complexity
	for job in Jobs:
		try:
			#Setting time in '20.05.2020 16:18' format. 
			time_now = datetime.strftime(datetime.now(timezone.utc),'%d.%m.%Y %H:%M')
			job['last_updated'] = time_now
			#Setting ID
			job['ID'] = int(job['uid'])
			job.pop('uid')
			#Ammount
			job['amount_currencyCode'] = job['amount']['currencyCode']
			job['amount_amount'] = job['amount']['amount']
			job.pop('amount')
			#WeeklyBudget
			if 'weeklyBudget' in job: 
				job['weeklyBudget_currencyCode'] = job['weeklyBudget']['currencyCode']
				job['weeklyBudget_amount'] = job['weeklyBudget']['amount']
				job.pop('weeklyBudget')
			#HourlyBudget	
			if 'hourlyBudgetText' in job: 
				job['hourlyBudget_amount'] = job['hourlyBudgetText']
				job.pop('hourlyBudgetText')
			#Occupations
			job['occupations_category'] = job['occupations']['category']['prefLabel']
			job['occupations_subcategories'] = job['occupations']['subcategories'][0]['prefLabel']#Check for number of subcategories (usually 1)!!!!
			assert len(job['occupations']['subcategories']) < 2, f'file = {file}\n job = {job}\n Number of "subcategories" in "occupations" >2'
			if type(job['occupations']['oservice'])== dict: job['occupations_oservice'] = job['occupations']['oservice']['prefLabel']
			job.pop('occupations')
			#Client
			for key in job['client'].keys():
				new_key = 'client' +'_'+ key
				if key == 'location': job[new_key] = job['client']['location']['country']
				else: job[new_key] = job['client'][key]
			job.pop('client')
			#Locations (1 USA city usually?)
			if len(job['locations']) != 0:
				job['client_USA_city'] = job['locations'][0]['name']#USA city?
			else: job['client_USA_city'] = None
			job.pop('locations')
			#FreelancersLocation
			N = len(job['prefFreelancerLocation'])
			job['prefFreelancerLocation_number'] = N
			if N != 0:
				for i in range (0, N):
					if i == 0: break #limit to 0 main locations
				job['prefFreelancerLocation_all'] = pickle.dumps(job['prefFreelancerLocation']) #all locations (type - list)!
			else: job['prefFreelancerLocation_all'] = None
			job.pop('prefFreelancerLocation')
			#Skills
			Ns = len(job['skills'])
			Na = len(job['attrs'])
			if Ns >= Na:	
				key = 'skills'
				N = Ns
			elif Ns < Na:
				key = 'attrs'
				N = Na
			else: N = 0
			job['skills_number'] = N
			if N != 0:
				for i in range (0, N):
					if i == 0: break #limit to 0 main skills!
				skills_All = []	
				for skill in job[key]: skills_All.append(skill['prettyName'])
				job['skills_all'] = pickle.dumps(skills_All)#all skills(type - list)!
			else: job['skills_all'] = None
			job.pop('skills')
			job.pop('attrs')
						
		except Exception as e:
			import sys
			exc_type, exc_obj, exc_tb = sys.exc_info()
			print(f"Downgrade error in  line:{exc_tb.tb_lineno}\n{e}\n file:{file}\n title:{job['title']})")
			input('Press any key')
		#eqiualizing jobs structure to BD structure
		for key in MAIN_TABLE_1rang_structure:
			if key not in job: job[key] = None
	return Jobs
	
if __name__ == '__main__':
	import json, time
	#Connect	
	db = Connect_Upwork_DB()
	#Delete table
	MyLibs.SQLite.Delete_Table(table_name, db)
	#Create Table for Upwork DB
	Create(table_name, MAIN_TABLE_1rang_structure, db)

	#=======with JSON all files
	import MyLibs.files_in_folder as ScanFolder
	path = r'D:\xxx\xxx\Python\PY\Raw_Jsons\Full_DB'
	File_list = ScanFolder.Abs_filenames(path)

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
			Jobs = clear_Upwork_data(json_PyObj)
			Jobs = Downgrade(Jobs)
			assert Jobs != None, f'Jobs == None in {file}'
		except Exception as e:
			print(f"{file}\n{e}")
			input('Press any key')
		Total_DB.append(Jobs)
	print("DB loaded: %s" % (time.time() - start0))
	
	result = {'insert': 0, 'update': 0}
	start1 = time.time()
	for Jobs in Total_DB:	
		insert, update = DropToDB(Jobs, db)
		result['insert'] = result['insert'] + insert
		result['update'] = result['update'] + update
		print(f"Result: {result['insert']} jobs inserted, {result['update']} jobs updated")
	print(f"Total: {result['insert']} jobs inserted, {result['update']} jobs updated")
		
	print('Done!!')
	print("DB dumped: %s" % (time.time() - start1))
	db.close()
