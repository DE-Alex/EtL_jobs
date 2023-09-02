import MyLibs.SQLite
import pickle
from MyLibs.Time import *

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
'workType':'TEXT',					#"Remote", "Permanent", "Occasional"
'duration':'TEXT',					#weeks - "Less than 1 month"/ months - "1 to 3 months"/ semester - "3 to 6 months"/ongoing - "more than 6 months"
'engagement':'TEXT',				#(workload) as needed: "Less than 30hrs/week" / full_time - "More than 10-30hrs/week"
'totalFreelancersToHire':'INTEGER',	#Number of FL to hire
#=====Money===
'amount_currencyCode':'TEXT',		#USD
'amount_amount':'INTEGER',			#Budget (fixed price)
'hourlyBudget_amount':'TEXT',		#$/hour payment
'weeklyBudget_currencyCode':'TEXT',
'weeklyBudget_amount':'INTEGER',	#$/week payment
#=====Client===
'skills_number':'INTEGER',
'skills_all':'BLOB',				#all skills (over 100 per some jobs and up to 6000 total) stored by pickle
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
'category2_uid': 'INTEGER',
'subcategory2_uid': 'INTEGER',

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

#Category ID, SubCategory ID, Name
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
	#	for row in A: file.write(str(row) + ',' + '\n')
	
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
				elif Uid_O == Uid_N and Label_O == Label_N:	found = True #change subUID
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
				elif Uid_O == Uid_N and Label_O == Label_N:	found = True #change subUID
				elif subUid_O == subUid_N and Label_O == Label_N: found = True #change  Uid
				elif subUid_O == subUid_N: found = True #change Uid and Label
				if found == True:
					Uid_tmp, subUid_tmp, Label_tmp = Uid_O, subUid_O, Label_O
			result2.append((Uid_tmp, subUid_tmp, Label_tmp, Uid_N, subUid_N, Label_N)) #(OLD, OLD, OLD, NEW, NEW, NEW)
		result = set(result1 + result2)

		time = datetime_to_str(now_local(), '%d.%m.%Y %H.%M')
		with open(err_log, 'a') as file: 
			file.write(time + '\n' + '(!) UIDs and Labels changed:\n')
			for row in result: file.write(str(row) + ',' + '\n')
		#save json to hard drive
		import json, sys
		with open(f'{sys.path[0]}\Log\{time}.json', 'w') as f: json.dump(json_PyObj, f)
	
def Create(table_name, table_columns, db):
	MyLibs.SQLite.Create_Table(table_name, 'ID', 'INTEGER', db, PrimaryKey = 'PRIMARY KEY')
	MyLibs.SQLite.AddColumnMany(table_name, table_columns, db)
	
def DropToDB(Jobs, DBpath, cashPath):
	assert type(Jobs) == list, 'DropToDB: Invalid type of input "Jobs" (non list)'
	db = MyLibs.SQLite.connect(DBpath)
	ID_list = MyLibs.SQLite.Select_ID(table_name, db)
	db.close()
	
	ins_Jobs = [job for job in Jobs if job['ID'] not in ID_list]#collect jobs to insertMany
	upd_Jobs = [job for job in Jobs if job['ID'] in ID_list] #collect jobs to updateMany
	
	ins_count = len(ins_Jobs)
	upd_count = len(upd_Jobs)

	db = MyLibs.SQLite.connect(DBpath)
	if ins_count !=0: MyLibs.SQLite.InsertMany(table_name, ins_Jobs, db)
	if upd_count !=0: MyLibs.SQLite.UpdateManyByID(table_name, upd_Jobs, db)
	db.close()
	
	db = MyLibs.SQLite.connect(cashPath)
	cID_list = MyLibs.SQLite.Select_ID(table_name, db)
	db.close()
	
	ins_Cash = [job for job in Jobs if job['ID'] not in cID_list]
	upd_Cash = [job for job in Jobs if job['ID'] in cID_list]

	db = MyLibs.SQLite.connect(cashPath)
	if len(ins_Cash) !=0: MyLibs.SQLite.InsertMany(table_name, ins_Cash, db)
	if len(upd_Cash) !=0: MyLibs.SQLite.UpdateManyByID(table_name, upd_Cash, db)
	db.close()
	return ins_count, upd_count
		
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
					'connectPrice',			#:'INTEGER',# payment to apply job?
					'prefFreelancerLocationMandatory',	#:'INTEGER', # 0 (False) /1 (True) limit to Freelancer Location
					'clientRelation',		#New key, null
					'multipleFreelancersToHirePredicted',#NoneType?
					'hourlyBudget']			#{"type": null, "min": null, "max": null} 

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
			time_now = datetime.now()
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
			job['category2_uid'] = job['occupations']['category']['uid']
			#--------
			if len(job['occupations']['subcategories']) > 1: print(f'Attention!!\njob ID = {job["ID"]}\n Number of "subcategories" in "occupations" >1')
			job['occupations_subcategories'] = ('+').join([subcat['prefLabel'] for subcat in job['occupations']['subcategories']])
			job['subcategory2_uid'] = ('+').join([subcat['uid'] for subcat in job['occupations']['subcategories']])

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
			#Ns = len(job['skills'])
			Na = len(job['attrs'])
			#if Ns >= Na:	
			#	key = 'skills'
			#	N = Ns
			#elif Ns < Na:
			if Na >0:
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
			#job.pop('skills')
			job.pop('attrs')
			#Tags
			if 'tags' in job:
				if job['tags'] == []: job['tags'] = None
				else: job['tags'] = ','.join(job['tags'])
						
		except Exception as e:
			import sys
			exc_type, exc_obj, exc_tb = sys.exc_info()
			print(f"Downgrade error in line:{exc_tb.tb_lineno}\n{e}\n title:{job['title']})")
			answer = input('save json to hard drive? y/n')
			if answer == 'y':
				#save json to hard drive
				import json, sys
				time = datetime_to_str(now_local(), '%d.%m.%Y %H.%M')
				PathToDump = f'{sys.path[0]}\Log\{time}.json'
				with open(PathToDump, 'w') as f: json.dump(Jobs, f)
				print(f'Saved to: {PathToDump}')
			input('Press any key')
			
			
		#eqiualizing jobs structure to BD structure
		for key in MAIN_TABLE_1rang_structure:
			if key not in job: job[key] = None
		#Searching new keys that can be added by Upwork
		NewKeys = (set(job.keys()) - set(MAIN_TABLE_1rang_structure.keys())) - {'ID'}
		if len(NewKeys) != 0:
			print(f'Attention! New keys in job (ID = {job["ID"]}):')
			for key in	NewKeys:
				print(f'- {key} : {type(job[key])}')
			answer = input('save json to hard drive? y/n')
			if answer == 'y':
				#save json to hard drive
				import json, sys
				time = datetime_to_str(now_local(), '%d.%m.%Y %H.%M')
				PathToDump = f'{sys.path[0]}\Log\{time}.json'
				with open(PathToDump, 'w') as f: json.dump(Jobs, f)
				print(f'Saved to: {PathToDump}')
			input('Press any key')
	return Jobs
	
if __name__ == '__main__':
	#pass
	import json, time
	path_from = r'D:\Shapovalov\svoe\Python\PY\Raw_Jsons\01.11.2021 06.42'
	
	path_to = r'D:\Shapovalov\svoe\Python\PY\DB_Upwork\Jobs.sqlite3'#Upwork jobs
	#path_to = r'D:\Shapovalov\svoe\Python\PY\Parser3\MyLibs\Test\test_SQLbase.sqlite3'
	#path_to = r'D:\Shapovalov\svoe\Python\PY\DB_Upwork\24_05.sqlite3'#Upwork jobs
	
	#Connect	
	db = MyLibs.SQLite.connect(path_to)
	#MyLibs.SQLite.BackUp(db, BackUp_path = r'D:\Shapovalov\svoe\Python\PY\DB_Upwork\back_up.sqlite3')
	#print("DB backup done: %s")
	
	#Delete table
	#MyLibs.SQLite.Delete_Table(table_name, db)
	#Create Table for Upwork DB
	#Create(table_name, MAIN_TABLE_1rang_structure, db)

	#=======with 1 JSON file
	# file = r'D:\Shapovalov\svoe\Python\PY\Raw_Jsons\old_Jobs\1.json'
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
			Jobs = clear_Upwork_data(json_PyObj)
			Jobs = Downgrade(Jobs)
			assert Jobs != None, f'Jobs == None in {file}'
		except Exception as e:
			print(f"{file}\n{e}")
			input('Press any key')
		Total_DB.append(Jobs)
	print("All jobs readed from files: %s" % (time.time() - start0))
	
	result = {'insert': 0, 'update': 0}
	start1 = time.time()
	for Jobs in Total_DB:	
		insert, update = DropToDB(Jobs, db)
		result['insert'] = result['insert'] + insert
		result['update'] = result['update'] + update
		print(f"Result: {result['insert']} jobs inserted, {result['update']} jobs updated")
	print(f"Total {result['insert'] + result['update']} jobs: {result['insert']} jobs inserted, {result['update']} jobs updated")
	db.close()	
	print('Done!!')
	delta = round((time.time() - start1))//60
	print(f"DB dumped in {delta} minutes")
	
	
