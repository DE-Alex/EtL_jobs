import math
import sys, requests, time
from MyLibs.Time import *

import cookies
	
def requests_pattern(page = 1, cat_uid = '', subcat_uid = '', jobType = '', cHires = '', proposals = '', duration_v3 = ''):
	if cat_uid != '': 
		cat_uid = f'category2_uid={cat_uid}&'
	if subcat_uid != '':
		subcat_uid = f'subcategory2_uid={subcat_uid}&'
		cat_uid = ''
	if jobType != '': 
		jobType = f't={jobType}&'
	if cHires != '': 
		cHires = f'client_hires={cHires}&'
	if proposals != '': 
		proposals = f'proposals={proposals}&'
	if duration_v3 != '': 
		duration_v3 = f'duration_v3={duration_v3}&'
	if page == 1: 
		page = ''
	else: 
		page = f'page={i}'
	
	request = f'https://www.upwork.com/ab/jobs/search/url?per_page=50&sort=recency&{cat_uid}{subcat_uid}{jobType}{cHires}{proposals}{duration_v3}{page}'
	
	return request

def form_requests_list(json_data, previous_url, user_agent, err_log, proxy):

	Filters = {'jobType' : ['0', '1'], 									#0-Hourly, 1 - Fixed price
			'clientHires': ['0', '1-9', '10-'], 						#No hires, 1-9 hires, 10+ hires
			'proposals': ['0-4', '5-9', '10-14', '15-19', '20-49'], 	#Less than 5, 5 to 10 proposals, 10 to 15 proposals, 15 to 20 proposals, 20 to 50 proposals
			'duration_v3': ['weeks', 'months', 'semester', 'ongoing'] 	#project length: Less 1 month, 1-3 months, 3-6 months, 6+ months
			}
	
	occupations = json_data['searchResults']['facets']['occupations']
	print(f"Total {json_data['searchResults']['paging']['total']} jobs found")
	
	reqList = []
	for Cat in occupations:
		N = math.ceil(Cat['count']/50) #round to bigger number
		if N <= 100:
			req = [requests_pattern(i, cat_uid = Cat['uid']) for i in range(1, N+1)]
			reqList.append(req)
			print(f'Requests: +{len(req)}')
		else:
			subCategories = Cat['occupations']
			for subCat in subCategories:
				N = math.ceil(subCat['count']/50)
				if N <= 100:
					req = [requests_pattern(i, subcat_uid = subCat['uid']) for i in range(1, N+1)]
					reqList.append(req)
					print(f'Requests: +{len(req)}')
				else:
					#========= Filters ========== 
					#========= JobType = ['0', '1'] ======
					for jType in Filters['jobType']:
						req = requests_pattern(1, cat_uid = Cat['uid'], subcat_uid = subCat['uid'], jobType = jType)
						get_req = send_request(req, previous_url, user_agent, err_log, proxy)
						previous_url = req
						json_PyObj = get_req.json()
						pages  = json_PyObj['searchResults']['paging']['total']
						N = math.ceil(pages/50)
						if N <= 100:
							req = [requests_pattern(i, cat_uid = Cat['uid'], subcat_uid = subCat['uid'], jobType = jType) for i in range(1, N+1)]
							reqList.append(req)
							print(f'Requests: +{len(req)}')
						else:
							#========= clientHires = ['0', '1-9', '10-'] ======
							for hires in Filters['clientHires']:
								req = requests_pattern(1, cat_uid = Cat['uid'], subcat_uid = subCat['uid'], jobType = jType, cHires = hires)
								get_req = send_request(req, previous_url, user_agent, err_log, proxy)
								previous_url = req
								json_PyObj = get_req.json()
								pages  = json_PyObj['searchResults']['paging']['total']
								N = math.ceil(pages/50)
								if N <= 100: 
									req = [requests_pattern(i, cat_uid = Cat['uid'], subcat_uid = subCat['uid'], jobType = jType, cHires = hires) for i in range(1, N+1)]
									reqList.append(req)
									print(f'Requests: +{len(req)}')
								else:
									#========= Proposals = ['0-4', '5-9', '10-14', '15-19', '20-49'] ======
									for Prop in Filters['proposals']:
										req = requests_pattern(1, cat_uid = Cat['uid'], subcat_uid = subCat['uid'], jobType = jType, cHires = hires, proposals = Prop)
										get_req = send_request(req, previous_url, user_agent, err_log, proxy)
										previous_url = req
										json_PyObj = get_req.json()
										pages  = json_PyObj['searchResults']['paging']['total']
										N = math.ceil(pages/50)
										if N <= 100: 
											req = [requests_pattern(i, cat_uid = Cat['uid'], subcat_uid = subCat['uid'], jobType = jType, cHires = hires, proposals = Prop) for i in range(1, N+1)]
											reqList.append(req)
											print(f'Requests: +{len(req)}')
										else:
											#========= Project Length = ['weeks', 'months', 'semester', 'ongoing'] ======
											for PrLgth in Filters['duration_v3']:
												req = requests_pattern(1, cat_uid = Cat['uid'], subcat_uid = subCat['uid'], jobType = jType, cHires = hires, proposals = Prop, duration_v3 = PrLgth)
												get_req = send_request(req, previous_url, user_agent, err_log, proxy)
												previous_url = req
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
												req = [requests_pattern(i, cat_uid = Cat['uid'], subcat_uid = subCat['uid'], jobType = jType, cHires = hires, proposals = Prop, duration_v3 = PrLgth) for i in range(1, N+1)]
												reqList.append(req)
												print(f'Requests: +{len(req)}')
	return previous_url, reqList

	
def send_request(url, previous_url, user_agent, err_log, proxy = False):
	cookies_jar = requests.cookies.RequestsCookieJar()
    
	if proxy != False: 
		proxy_dict = {"http"  : f"http://{proxy}", "https" : f"https://{proxy}"}
	else: 
		proxy_dict = {}
		
	time.sleep(3)
	i = -1
	while True:
		i += 1
		cookies = cookies.select_cookies()

		for cookie in cookies:
			if cookie['name'] == 'oauth2_global_js_token': 
				Token = 'Bearer ' + cookie['value']
			cookies_jar.set(cookie['name'],cookie['value'])
			
		my_headers={'User-Agent' : user_agent,
					'Accept': 'application/json, text/plain, */*',
					'Accept-Language' : 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
					'Accept-Encoding' : 'gzip, deflate, br',
					'x-odesk-user-agent' : 'oDesk LM',
					'x-requested-with': 'XMLHttpRequest',
					'X-KL-Ajax-Request': 'Ajax_Request',
					'Sec-Fetch-Dest': 'empty',
					'Sec-Fetch-Mode': 'cors',
					'Sec-Fetch-Site': 'same-origin',
					'Authorization': Token,
					'Referer': previous_url,
					'Connection': 'keep-alive',
					'TE': 'trailers'}
		try:
			#положитьМТМ_сертификат в папку МТМ
            mtmproxy_certificate = 'D:\\MTM_Proxy\\mitmproxy_cert\\mitmproxy-ca-cert.pem'
			req = requests.get(url, headers = my_headers, cookies = cookies_jar, proxies = proxy_dict, verify = mtmproxy_certificate)
			req.connection.close()
			
			if req.status_code == requests.codes.ok: 
                return req
			else:
				date = datetime_to_str(now_local(), '%d.%m.%Y %H.%M')
				with open(err_log, 'a') as file: 
                    file.write(f'{date} {i}:code {req.status_code}\n')
				
				if req.status_code == 403: 
					print(f'{i}: 403 Forbidden. Paused for 5 min.')
					time.sleep(300)
				else: 
					print(f'{i}: status code {req.status_code}. Paused for 0.5 min.')
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
    pass
	
	
