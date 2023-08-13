import MyLibs.SQLite
import pickle, datetime

#===DATA BASE
table_name = 'Jobs'



MAIN_TABLE_1rang_structure = {#'ID' column created with table as PRIMARY KEY
'occupations_category':'TEXT',
'occupations_subcategories':'TEXT',#Check for number of subcategories (usually 1)!!!!
'occupations_oservice':'TEXT',
'title':'TEXT',
'description':'TEXT',				
'Label':'TEXT',						# My Label for classifier
'type':'INTEGER',					#(JobType) 1-Fixed price, 2 - Hourly, 3 - Weekly Retainer (weekly pay to be
									#ready to get job in future)
'workType':'TEXT', 					#"Remote", "Permanent", "Occasional"
'duration':'TEXT',					#weeks - "Less than 1 month"/ months - "1 to 3 months"/ semester - "3 to 6 months"/ongoing - "more than 6 months"
'engagement':'TEXT',				#(workload) as needed: "Less than 30hrs/week" / full_time - "More than 10-30hrs/week"
'totalFreelancersToHire':'INTEGER',	#Number of FL to hire
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
'client_paymentVerificationStatus':'INTEGER', #0-5 WTF????
'client_location':'TEXT',			#Client's country
'client_totalSpent':'INTEGER',
'client_totalReviews':'INTEGER',
'client_totalFeedback':'INTEGER',
'client_edcUserId':'INTEGER',		#Client Odesk ID
'client_companyOrgUid':'TEXT',		#Client's Company ID
'client_hasFinancialPrivacy': 'INTEGER',# 0 /1 WTF????
'client_USA_city':'TEXT',			#USA city? 1 value (arount values 190 total)

#=====Trash?===
'teamUid':'INTEGER',
'premium':'INTEGER',				# 0 /1 WTF????
'freelancersToHire':'INTEGER',
'recno':'INTEGER',
'prefFreelancerLocation_number':'INTEGER',
'prefFreelancerLocation_all':'BLOB', #all locations (over 10 per job and up to 210 total) stored by pickle
'ciphertext':'TEXT',				# WTF???? may be delete?
'createdOn':'TEXT',
'jobTs':'TEXT',						#1588837356207
'proposalsTier':'TEXT',				#Number of proposals "Less than 5"(0-4), "5 to 10"(5-9), "10 to 15"(10-14), "15 to 20"(15-19), "20 to 50"(20-49), "50+"(*)
'publishedOn':'TEXT',
'renewedOn':'TEXT',
#=====Service===
'last_updated':'TEXT',
'tags':'TEXT',
'closed':'INTEGER'
}

					
def Create(table_name, table_columns, db):
	MyLibs.SQLite.Create_Table(table_name, 'ID', 'INTEGER', db, PrimaryKey = 'PRIMARY KEY')
	MyLibs.SQLite.AddColumnMany(table_name, table_columns, db)
	
	
def DropToDB(Jobs, path_to_DB):
	assert type(Jobs) == list, 'DropToDB: Invalid type of input "Jobs" (non list)'
	db = MyLibs.SQLite.connect(path_to_DB)
	result = MyLibs.SQLite.Select(table_name, db, ['ID'])
	db.close()
	ID_list = [item[0] for item in result]
	Jobs_to_insert = [job for job in Jobs if job['ID'] not in ID_list]#collect jobs to insertMany
	Jobs_to_update = [job for job in Jobs if job['ID'] in ID_list] #collect jobs to updateMany
	
	insert_count = len(Jobs_to_insert)
	update_count = len(Jobs_to_update)
	if insert_count !=0: 
		db_cash = MyLibs.SQLite.connect(rf'D:\Shapovalov\svoe\Python\PY\DB_Upwork\_cash_.sqlite3')#@@@@@@
		for job in Jobs_to_insert: MyLibs.SQLite.Insert(table_name, job, db_cash)#@@@@@@
		db_cash.close()#@@@@@@
		db = MyLibs.SQLite.connect(path_to_DB)
		MyLibs.SQLite.InsertMany(table_name, Jobs_to_insert, db)
		db.close()
	if update_count !=0:
		db = MyLibs.SQLite.connect(path_to_DB)
		MyLibs.SQLite.UpdateManyByID(table_name, Jobs_to_update, db)
		db.close()
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
					'prefFreelancerLocationMandatory',	#:'INTEGER', # 0 (False) /1 (True) limit to Freelancer Location
					'clientRelation'] 		#New key, null

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
			#Setting time in '20.05.2020 16:18' format
			time_now = datetime.datetime.now()
			job['last_updated'] = time_now.isoformat()
			#Setting ID
			job['ID'] = int(job['uid'])
			job.pop('uid')
			#Ammount
			job['amount_currencyCode'] = job['amount']['currencyCode']
			job['amount_amount'] = job['amount']['amount']
			job.pop('amount')
			#WeeklyBudget
			if 'weeklyBudget' in job:
				if type(job['weeklyBudget']) == dict: 
					job['weeklyBudget_currencyCode'] = job['weeklyBudget'].get('currencyCode', None)
					#print(job['weeklyBudget_currencyCode'])
					#job['weeklyBudget_currencyCode'] = job['weeklyBudget']['currencyCode']
					job['weeklyBudget_amount'] = job['weeklyBudget'].get('amount', None)
					#print(job['weeklyBudget_amount'])
				job.pop('weeklyBudget')
			#HourlyBudget	
			if 'hourlyBudgetText' in job: 
				job['hourlyBudget_amount'] = job['hourlyBudgetText']
				job.pop('hourlyBudgetText')
			#Occupations
			job['occupations_category'] = job['occupations']['category']['prefLabel']
			#--------
			if len(job['occupations']['subcategories']) > 1: print(f'Attention!!\njob ID = {job["ID"]}\n Number of "subcategories" in "occupations" >1')
			job['occupations_subcategories'] = ('+').join([subcat['prefLabel'] for subcat in job['occupations']['subcategories']])

			#-------
			if type(job['occupations']['oservice'])== dict: job['occupations_oservice'] = job['occupations']['oservice']['prefLabel']
			job.pop('occupations')
			#Client
			for key in job['client'].keys():
				new_key = 'client' +'_'+ key
				if key == 'location': job[new_key] = job['client']['location']['country']
				else: job[new_key] = job['client'][key]
				#print(new_key, job[new_key])
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
					if i == 0: break #limit to 0 main locations!!!
					#new_name = f'prefFreelancerLocation_{i}'
					#job[new_name] = job['prefFreelancerLocation'][i]
				job['prefFreelancerLocation_all'] = pickle.dumps(job['prefFreelancerLocation']) #all locations (type - list)!!
				#print(pickle.loads(job['prefFreelancerLocation_all'])) #command to Load Locations 
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
					if i == 0: break #limit to 0 main skills!!!
					#new_name = f'skill_{i}'
					#job[new_name] = job[key][i]['prettyName']
				skills_All = []	
				for skill in job[key]: skills_All.append(skill['prettyName'])
				job['skills_all'] = pickle.dumps(skills_All)#all skills(type - list)!!
				#print(pickle.loads(job['skills_all'])) #command to Load skills 
			else: job['skills_all'] = None
			job.pop('skills')
			job.pop('attrs')
			#Tags
			if 'tags' in job:
				if job['tags'] == []: job['tags'] = None
				else: job['tags'] = ','.join(job['tags'])

						
		except Exception as e:
			import sys
			exc_type, exc_obj, exc_tb = sys.exc_info()
			print(f"Downgrade error in line:{exc_tb.tb_lineno}\n{e}\n title:{job['title']})")
			input('Press any key')
		#eqiualizing jobs structure to BD structure
		for key in MAIN_TABLE_1rang_structure:
			if key not in job: job[key] = None
	return Jobs
	
if __name__ == '__main__':
	pass
