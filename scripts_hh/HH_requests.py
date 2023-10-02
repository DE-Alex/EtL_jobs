# -*- coding: utf-8 -*-
import math, requests, time, json, os, re
from shutil import copyfile
from MyLibs.Time import *
import HH_DB_Manager

API_url = r'https://api.hh.ru/vacancies'

cashPath = r'D:\Temp\HH_cash_.sqlite3'

BlackRoles = [
#'системный',
#'сетевой',
#'программист', 
#'аналитик', 
'авто','агент','агроном','администратор','андеррайтер','апте','артист','архитектор','аудитор','безопаснос','бизнес','бухгалтер','водитель','военнослужащий','воспитатель','врач','гео','главный инженер проекта','грузчик','дворник','дизайнер','директор','диспетчер','другое','журналист','зоотехник','инженер-конструктор','кадр','казначей','кассир','качеств','кладовщик','косметолог','кредит','курьер','лаборант','магаз','маляр','массажист','мастер','машинист','медицин','менеджер','мерчандайзер','механик','монтажник','начальник','оператор','официант','охран','оценщик','парикмахер','переводчик','персонал','писатель','повар','поддерж','полицейский','продавец','продаж','продюсер','промоутер','прораб','психолог','разнорабочий','редактор','режиссер','руководитель','сварщик','секретарь','слесарь','сметчик','супервайзер','тендер','тестировщик','технол','товаровед','токарь','торгов','уборщица','упаковщик','учитель','фармацевт','финанс','фитнес','фотограф','хостес','швея','экономист','эксплуатац','электромонтажник','энергетик','юрис']

# professional_role = {
	# 'Аналитик': 10,
	# 'Программист, разработчик':96,
	# 'Сетевой инженер': 112,
	# 'Системный инженер': 114,
	# 'BI-аналитик, аналитик данных':156, #включен в список 15.07.2023
	# 'DevOps-инженер':160,  				#включен в список 15.07.2023
	# 'другое':40 						#включен в список 15.07.2023
	# }

DefaultParams = {'per_page': 100, 'clusters': 'true', 'describe_arguments': 'true'}

class UrlsGenerator():
	def __init__(self, DB_Folder, emptyDB, ErrorLog, ReqDel):
		self.err_log = ErrorLog
		self.DB_Folder = DB_Folder
		self.emptyDB = emptyDB
		self.ReqDel = ReqDel
		
	def main(self, All_ID):
		self.Cash = []
		self.VacCount = 0
		self.TotalIns = 0
		self.TotalUpd = 0
	
		start = time.time()
		self.All_ID = All_ID
		jsObj = self.JsonGet()
		self.Filters = self.FormFilters(jsObj)
		while True:
			req = requests.get(r'https://api.hh.ru/areas')
			req.close()
			if req.status_code == requests.codes.ok: 
				self.Areas = req.json() #import Test_areas #self.Areas = Test_areas.lines
				break
			else:
				print('Error: https://api.hh.ru/areas')
				time.sleep(1)
		
		while True:
			req = requests.get(r'https://api.hh.ru/metro/1') # 1 == Moscow
			req.close()
			if req.status_code == requests.codes.ok:
				Moscow = req.json() #import Test_metro #Metro = Test_metro.lines
				tmp = []
				MoscowLines = Moscow['lines']
				for line in MoscowLines:
					tmp.append(line['id'])
					for station in line['stations']:
						tmp.append(station['id'])
				self.MetroID = tmp
				break
			else:
				print('Error: https://api.hh.ru/metro/1')
				time.sleep(1)
		clasters = {}
		self.Generator(clasters)
		self.DropToDB()
		delta = round((time.time() - start))//60
		print(f"Downloaded in {delta} minutes")
		print(f'Downloaded {self.VacCount} jobs')
		print(f"Total: {self.TotalIns} inserted, {self.TotalUpd} updated")
		
		
		return self.All_ID
		
	def FormFilters(self, jsObj):
		FiltID = ['professional_role',
				'experience',
				'schedule',
				'employment',
				#'salary',
				'area'
				#'only_with_salary',#'professional_area',#'industry',#label',
				]
		MyClusters = {cluster['id']:cluster['items'] for cluster in jsObj['clusters']}
		Filters = []
		for id in FiltID:
			values = []
			for item in MyClusters[id]:
				name = item['name'].lower()
				for label in BlackRoles:
					if label in name: 
						break
				else:
					list = item['url'].split('&')
					for str in list:
						match = re.compile(rf'{id}=(.+)').search(str)
						if match: 
							value = match.groups()[0]
					values.append(value)
			Filters.append({id: values})
		return Filters		
		
	def Generator(self, clasters):
		Filters = self.Filters
		for filter in Filters:
			id = list(filter.keys())[0]
			if id not in clasters.keys():
				clasters[id] = None
				values = filter[id]
				break
		else:
			msg = f'Filters Over, too Much Pages! \n {str(clasters)}'
			print(msg)
			self.ErrorsLog(msg)
			return clasters
			
		if id == 'area':
			areasObj = self.Areas
			clasters = self.AreasFilter(areasObj, clasters)
		else:
			for value in reversed(values):
				clasters[id] = value
				result = self.GetPages(clasters)
				if not result:
					clasters = self.Generator(clasters)
		del clasters[id]
		return clasters

	def AreasFilter(self, areasObj, clasters):
		for area in areasObj:
			name = area['name']
			value = area['id']
			childs = area['areas']
			clasters['area'] = value
			print(f'Name: {name} ({value})')
			result = self.GetPages(clasters)
			if result:
				pass
			elif not result and name == 'Москва':
				clasters = self.MetroFilter(clasters)
			elif not result and childs == []:
				input('Too many Vacancies!!!')
			else:
				clasters = self.AreasFilter(childs, clasters)
		return clasters
			
	def MetroFilter(self, clasters):
		clasters['metro'] = None
		for id in self.MetroID:
			#print('station_id:', id)
			clasters['metro'] = id
			result = self.GetPages(clasters)
			if not result:
				input('Too many Vacancies!!!')
		del clasters['metro']
		return clasters
	
	def GetPages(self, clasters):
		for page in range(20):
			jsObj = self.JsonGet(clasters, page)
			Vac = jsObj['found']
			N = jsObj['pages']
			if page == 0:
				print(f"Vacancies: {Vac} Pages: {jsObj['pages']}")			
			if Vac > 1950:
				print(f'Add new filter')
				return False
			actualJobs = self.DataCheck(jsObj['items'])
			L = len(actualJobs)
			if L > 0:
				print(f'page: {page+1} New jobs: {L}')
				self.CashToMem(actualJobs)
			elif L == 0:
				print(f'Nothing or too old jobs. Skip.')
			
			if page == (N -1):
				break
			
		return True

	def CashToMem(self, actualJobs):
		VacancyList = []
		N = 0
		print(f'Vacancy: ', end = '')
		for VacId in actualJobs:
			vacancy = self.JsonGet(id = VacId)
			N += 1
			print(f'{N} ', sep=' ', end='', flush=True)
			VacancyList.append(vacancy)
		Vacancies = [HH_DB_Manager.Downgrade(job) for job in VacancyList]
		self.Cash.extend(Vacancies)
		
		for job in Vacancies:
			id = job['ID']
			self.All_ID[id] = job['last_updated']
			
		print(f'\nTotal: {self.VacCount}')
		if len(self.Cash) >= 100:
			self.DropToDB()
		
	def DropToDB(self):
		data = self.Cash
		SortedJobs = {}
		NewID = {}
		for job in data:
			date = datetime_to_str(dateutil.parser.parse(job['created_at']), '%Y.%m')
			if date not in SortedJobs:
				SortedJobs[date] = []
			SortedJobs[date].append(job)
			NewID[job['ID']] = job['last_updated']
		insert, update = 0, 0
		for date in list(SortedJobs.keys()):
			path = rf'{self.DB_Folder}\{date}.sqlite3'
			if not os.path.exists(path):
				copyfile(self.emptyDB, path)
			jobs = SortedJobs[date]	
			ins, upd = HH_DB_Manager.DropToDB(jobs, path)
			insert += ins
			update += upd
		result = f"DB: {insert} inserted, {update} updated"
		print(result)
		
		self.TotalIns += insert
		self.TotalUpd += update
		self.Cash = []

	def DataCheck(self, jobs):
		All_ID = self.All_ID
		actualJobs = []
		for job in jobs:
			date_List = [dateutil.parser.parse(time) for time in [job['published_at'], job['created_at']] if time != None]
			date_List.sort()
			newest = date_List[-1]
			id = job['id']
			if id in list(All_ID.keys()):
				updated = dateutil.parser.parse(All_ID[id])
				if updated > newest:
					pass
				else:
					actualJobs.append(id)
			else: 
				actualJobs.append(id)
			#actualJobs.append(id) #@@@@@@@@@@@@@@@@@@@@@@@!!!!!!!!!!!
		return actualJobs

	def JsonGet(self, clasters = {}, page = 0, id = None):
		if id != None and id.isnumeric():
			url = f'https://api.hh.ru/vacancies/{id}?host=hh.ru'
			params = {}
			self.VacCount += 1
		else:
			url = API_url
			params = {key: val for key, val in DefaultParams.items()}
			for key, val in clasters.items():
				params[key] = val
			params['page'] = page
			print(params)#@@@@@@@
		#Request Delay
		time.sleep(self.ReqDel)
		i = -1
		while True:
			i += 1
			try:
				req = requests.get(url, params)
				req.close()
				if req.status_code == requests.codes.ok: 
					jsObj = req.json()
					#self.SaveJson(jsObj)
					return jsObj
				else:
					msg = f'{i}: status code {req.status_code}. Paused for 0.5 min.'
					print(msg)					
					self.ErrorsLog(msg)
					time.sleep(30)
				if i >= 5:
					print('Paused for 5 min.')
					time.sleep(300)
					i = 0				
			except requests.exceptions.ProxyError as e:
				msg = f'{i}: ProxyError: {str(e)}'
				print(msg)
				self.ErrorsLog(msg)
				time.sleep(2)
			except requests.exceptions.ConnectionError as e: 
				msg = f'{i}: ConnectionError.  {str(e)}'
				print(msg)
				self.ErrorsLog(msg)
				time.sleep(2)
	
	def ErrorsLog(self, msg):
		time = datetime_to_str(now_local(), '%d.%m.%Y %H.%M')
		with open(self.err_log, 'a') as file: 
			file.write(time + '\n' + msg + '\n')
	
	# def SaveJson(self, jsObj):	
		# JsonDir = r'D:\DB_HH\Json'
		# N = len(os.listdir(JsonDir))
		# nextFileName = rf'{JsonDir}\{N}.json'
		# with open(nextFileName, mode='w', encoding='utf8') as file:
			# file.write(json.dumps(jsObj, ensure_ascii=False))
			
if __name__ == '__main__':
	err_log = r'D:\Shapovalov\svoe\Python\PY\HH\Log\#HH_Errors.log'
	DB_Folder = rf'D:\DB_HH'
	
	T = UrlsGenerator(err_log)
	T.main({})
	
