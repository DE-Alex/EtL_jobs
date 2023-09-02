import math
import sys, requests, time, random
from MyLibs.Time import *

import CookieMGR
	
def req_Generator(i, cat_uid = '', subcat_uid = '', jobType = '', cHires = '', proposals = '', duration_v3 = ''):
	if cat_uid != '': cat_uid = f'category2_uid={cat_uid}&'
	if subcat_uid != '':
		subcat_uid = f'subcategory2_uid={subcat_uid}&'
		cat_uid = ''
	if jobType != '': jobType = f't={jobType}&'
	if cHires != '': cHires = f'client_hires={cHires}&'
	if proposals != '': proposals = f'proposals={proposals}&'
	if duration_v3 != '': duration_v3 = f'duration_v3={duration_v3}&'
	if i == 1: page = ''
	else: page = f'page={i}'
	
	#request = f'https://www.upwork.com/ab/jobs/search/url?per_page=50&sort=recency&user_location_match=2&{cat_uid}{subcat_uid}{jobType}{cHires}{proposals}{duration_v3}{page}'
	request = f'https://www.upwork.com/ab/jobs/search/url?per_page=50&sort=recency&{cat_uid}{subcat_uid}{jobType}{cHires}{proposals}{duration_v3}{page}'
	
	return request

def List(json_data, HomePage, UserAgent, err_log, proxy):

	Filters = {'jobType' : ['0', '1'], #0-Hourly, 1 - Fixed price
			'clientHires': ['0', '1-9', '10-'], #No hires, 1-9 hires, 10+ hires
			'proposals': ['0-4', '5-9', '10-14', '15-19', '20-49'], #Less than 5, 5 to 10 proposals, 10 to 15 proposals, 15 to 20 proposals, 20 to 50 proposals
			'duration_v3': ['weeks', 'months', 'semester', 'ongoing'] #project length: Less 1 month, 1-3 months, 3-6 months, 6+ months
			}
	
	occupations = json_data['searchResults']['facets']['occupations']
	print(f"Total {json_data['searchResults']['paging']['total']} jobs found")
	
	reqList = []
	for Cat in occupations:
		N = math.ceil(Cat['count']/50) #round to bigger number
		if N <= 100:
			req = [req_Generator(i, cat_uid = Cat['uid']) for i in range(1, N+1)]
			reqList.append(req)
			print(f'Requests: +{len(req)}')
		else:
			subCategories = Cat['occupations']
			for subCat in subCategories:
				N = math.ceil(subCat['count']/50)
				if N <= 100:
					req = [req_Generator(i, subcat_uid = subCat['uid']) for i in range(1, N+1)]
					reqList.append(req)
					print(f'Requests: +{len(req)}')
				else:
					#========= Filters ========== 
					#========= JobType = ['0', '1'] ======
					for jType in Filters['jobType']:
						req = req_Generator(1, cat_uid = Cat['uid'], subcat_uid = subCat['uid'], jobType = jType)
						get_req = reqGet(req, HomePage, UserAgent, err_log, proxy)
						HomePage = req
						json_PyObj = get_req.json()
						pages  = json_PyObj['searchResults']['paging']['total']
						N = math.ceil(pages/50)
						if N <= 100:
							req = [req_Generator(i, cat_uid = Cat['uid'], subcat_uid = subCat['uid'], jobType = jType) for i in range(1, N+1)]
							reqList.append(req)
							print(f'Requests: +{len(req)}')
						else:
							#========= clientHires = ['0', '1-9', '10-'] ======
							for hires in Filters['clientHires']:
								req = req_Generator(1, cat_uid = Cat['uid'], subcat_uid = subCat['uid'], jobType = jType, cHires = hires)
								get_req = reqGet(req, HomePage, UserAgent, err_log, proxy)
								HomePage = req
								json_PyObj = get_req.json()
								pages  = json_PyObj['searchResults']['paging']['total']
								N = math.ceil(pages/50)
								if N <= 100: 
									req = [req_Generator(i, cat_uid = Cat['uid'], subcat_uid = subCat['uid'], jobType = jType, cHires = hires) for i in range(1, N+1)]
									reqList.append(req)
									print(f'Requests: +{len(req)}')
								else:
									#========= Proposals = ['0-4', '5-9', '10-14', '15-19', '20-49'] ======
									for Prop in Filters['proposals']:
										req = req_Generator(1, cat_uid = Cat['uid'], subcat_uid = subCat['uid'], jobType = jType, cHires = hires, proposals = Prop)
										get_req = reqGet(req, HomePage, UserAgent, err_log, proxy)
										HomePage = req
										json_PyObj = get_req.json()
										pages  = json_PyObj['searchResults']['paging']['total']
										N = math.ceil(pages/50)
										if N <= 100: 
											req = [req_Generator(i, cat_uid = Cat['uid'], subcat_uid = subCat['uid'], jobType = jType, cHires = hires, proposals = Prop) for i in range(1, N+1)]
											reqList.append(req)
											print(f'Requests: +{len(req)}')
										else:
											#========= Project Length = ['weeks', 'months', 'semester', 'ongoing'] ======
											for PrLgth in Filters['duration_v3']:
												req = req_Generator(1, cat_uid = Cat['uid'], subcat_uid = subCat['uid'], jobType = jType, cHires = hires, proposals = Prop, duration_v3 = PrLgth)
												get_req = reqGet(req, HomePage, UserAgent, err_log, proxy)
												HomePage = req
												json_PyObj = get_req.json()
												pages  = json_PyObj['searchResults']['paging']['total']
												N = math.ceil(pages/50)
												if N > 100: 
													print(f"\nAttention! Again too many jobs in {Cat['label']}{subCat['label']} with jobType = {jType}, clientHires = {hires} proposals = {Prop} duration_v3 = {PrLgth} !")
													with open(err_log, 'a') as file: file.write(req + '\n')
													import MyLibs.PyObject_to_PyFile as PyFile
													PyFile.Write(reqList, sys.path[0] + rf'\Temp\Error_reqList.txt')
													print('cat_uid =', Cat['uid'], 'subcat_uid =', subCat['uid'])
													import json
													with open(sys.path[0] + rf'\Temp\Errors.json', 'a') as file: json.dump(json_PyObj, file)
													print('Load only first 5000 jobs')
													N = 100
												req = [req_Generator(i, cat_uid = Cat['uid'], subcat_uid = subCat['uid'], jobType = jType, cHires = hires, proposals = Prop, duration_v3 = PrLgth) for i in range(1, N+1)]
												reqList.append(req)
												print(f'Requests: +{len(req)}')
	return HomePage, reqList

	
def reqGet(URL, HomePage, UserAgent, err_log, proxy = False):
	from requests.packages.urllib3.exceptions import InsecureRequestWarning
	#requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
	cookies_jar = requests.cookies.RequestsCookieJar() #stored_attrs = ['domain', 'httpOnly', 'name', 'value', 'path', 'secure', 'expires']
	if proxy != False: proxyDict = {"http"  : f"http://{proxy}", "https" : f"https://{proxy}"}
	else: proxyDict = {}
		
	time.sleep(3)
	i = -1
	while True:
		i += 1
		cookies = CookieMGR.UpdateCookies()

		for cookie in cookies:
			if cookie['name'] == 'oauth2_global_js_token': 
				Token = 'Bearer ' + cookie['value']
			cookies_jar.set(cookie['name'],cookie['value'])
			
		My_headers={#'Host' : 'www.upwork.com', #don't set!??
					'User-Agent' : UserAgent,
					'Accept': 'application/json, text/plain, */*',
					'Accept-Language' : 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
					'Accept-Encoding' : 'gzip, deflate, br',
					'x-odesk-user-agent' : 'oDesk LM',
					'x-requested-with': 'XMLHttpRequest',
					# vnd-eo-trace-id: 6d8d7739bbfc359b-DME
					# vnd-eo-span-id: 5dec2525-d702-4baf-927d-d4bb8edb149f
					# vnd-eo-parent-span-id: 314cca39-8e37-4c74-bbf7-786fd7077907
					'X-KL-Ajax-Request': 'Ajax_Request',
					'Sec-Fetch-Dest': 'empty',
					'Sec-Fetch-Mode': 'cors',
					'Sec-Fetch-Site': 'same-origin',
					'Authorization': Token,
					'Referer': HomePage,
					'Connection': 'keep-alive',
					'TE': 'trailers'}
		try:
			path_to_mtmproxy_certificate = 'D:\\MTM_Proxy\\mitmproxy_cert\\mitmproxy-ca-cert.pem'
			req = requests.get(URL, headers = My_headers, cookies = cookies_jar, proxies = proxyDict, verify = path_to_mtmproxy_certificate)
			req.connection.close()
			
			if req.status_code == requests.codes.ok: return req
			else:
				date = datetime_to_str(now_local(), '%d.%m.%Y %H.%M')
				with open(err_log, 'a') as file: file.write(f'{date} {i}:code {req.status_code}\n')
				
				if req.status_code == 403: 
					print(f'{i}: 403 Forbidden.')
					print('Paused for 5 min.')
					time.sleep(300)
				else: 
					print(f'{i}: status code {req.status_code}.')
					print('Paused for 0.5 min.')
					time.sleep(30)
					#524 - lags
					#502 - reload MTM? - ok, after 5 min pause
					#401 - ok, after 5 min pause
			if i >= 5:
				print('Paused for 5 min.')
				time.sleep(300)
				i = 0				
		except requests.exceptions.ProxyError as e: 
			print(f'{i}: ProxyError: ', e)
			date = datetime_to_str(now_local(), '%d.%m.%Y %H.%M')
			with open(err_log, 'a') as file: 
				file.write(date + '\n' + e + '\n')
			time.sleep(2)
	
if __name__ == '__main__':
	import CookieMGR
	cookies = CookieMGR.main()
	
	URL = r'https://www.upwork.com/ab/jobs/search/url?per_page=50&sort=recency&user_location_match=2&page=100'
	#URL = 'https://api.ipify.org/'
	#HomePage = 'https://www.google.com/'
	HomePage = r"https://www.upwork.com/nx/jobs/search/?sort=recency"
	UserAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) Gecko/20100101 Firefox/101.0'
	proxy = '127.0.0.1:35685'
	err_log = sys.path[0] + rf'\#Errors.log'
	
	req = reqGet(URL, HomePage, UserAgent, err_log, proxy)

	
	if req.status_code == requests.codes.ok: print('Ok')
	else:print(f'{i}: status code {req.status_code}.')
	
	if req == False: print('Fail')
	json_PyObj = req.json()
	import json
	with open(sys.path[0] + rf'\Temp\Errors.json', 'w') as file: json.dump(json_PyObj, file)
													
	#HomePage, List(json_data, HomePage, UserAgent, cookies, err_log, proxy)
	
	
