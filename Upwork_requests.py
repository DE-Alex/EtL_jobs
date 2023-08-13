import json, math
import sys, requests, time

	
def req_Generator(i, Auth, cat_uid = '', subcat_uid = '', Service = '', jobType = '', cHires = ''):
	#formatted values

	if cat_uid != '': cat_uid = f'category2_uid={cat_uid}&'
	if cHires != '': cHires = f'client_hires={cHires}&'
	if subcat_uid != '':
		subcat_uid = f'&subcategory2_uid={subcat_uid}'
		cat_uid = ''
	if Service != '':
		L = Service.replace(' ',' AND ')
		Service = f'q=({L})&'
	if jobType != '': jobType = f'&t={jobType}'
		
	request = f'https://www.upwork.com/{Auth}url?{cat_uid}{cHires}page={i}&per_page=50&{Service}sort=recency{subcat_uid}{jobType}'
	
	return request
	
def req_html_gen(Auth, Auth2, ciphertext):
	request = f'https://www.upwork.com/{Auth}{Auth2}{ciphertext}.html'
	return request
	

def List(json_data, Auth, HomePage, UserAgent, cookies, proxy):

	Filters = {'jobType' : ['0', '1'], #1-Fixed price, 2 - Hourly
			'clientHires': ['0', '1-9', '10-']} #No hires, 1-9 hires, 10+ hires
			#'proposals': ['0-4', '5-9', '10-14', '15-19', '20-49'] #Less than 5, 5 to 10 proposals, 10 to 15 proposals, 15 to 20 proposals, 20 to 50 proposals
			#}
	
	occupations = json_data['searchResults']['facets']['occupations']
	print(f"Total {json_data['searchResults']['paging']['total']} jobs found")
	
	requests_List = []
	for category in occupations:
		N = math.ceil(category['count']/50) #round to bigger number
		if N <= 100:

			req = [req_Generator(i, Auth, cat_uid = category['uid']) for i in range(1, N+1)]
			requests_List.append(req)
		else:
			subcategories = category['occupations']
			for subcategory in subcategories:
				N = math.ceil(subcategory['count']/50)
				if N <= 100:
					req = [req_Generator(i, Auth, subcat_uid = subcategory['uid']) for i in range(1, N+1)]
					requests_List.append(req)
				else:
					Services = subcategory['occupations']
					for Service in Services:
						N = math.ceil(Service['count']/50)
						if N <= 100:
							req = [req_Generator(i, Auth, cat_uid = category['uid'], subcat_uid = subcategory['uid'], Service = Service['label']) for i in range(1, N+1)]
							requests_List.append(req)
						else:
							#=========Additional Filters=== 
							#========= JobType = ['0', '1'] ======
							for jType in Filters['jobType']:
								req = req_Generator(1, Auth, cat_uid = category['uid'], subcat_uid = subcategory['uid'], Service = Service['label'], jobType = jType)
								get_req = Get(req, HomePage, UserAgent, cookies, proxy)
								HomePage = req
								json_PyObj = get_req.json()
								pages  = json_PyObj['searchResults']['paging']['total']

								N = math.ceil(pages/50)
								if N <= 100:
									req = [req_Generator(i, Auth, cat_uid = category['uid'], subcat_uid = subcategory['uid'], Service = Service['label'], jobType = jType) for i in range(1, N+1)]
									requests_List.append(req)
								else:
									#========= clientHires = ['0', '1-9', '10-'] ======
									for hires in Filters['clientHires']:
										req = req_Generator(1, Auth, cat_uid = category['uid'], subcat_uid = subcategory['uid'], Service = Service['label'], jobType = jType, cHires = hires)
										get_req = Get(req, HomePage, UserAgent, cookies, proxy)
										HomePage = req
										json_PyObj = get_req.json()
										pages  = json_PyObj['searchResults']['paging']['total']

										N = math.ceil(pages/50)
										if N > 100: 
											print(f"\nAttention! Again too many jobs in {category['label']}{subcategory['label']}{Service['label']} with jobType = {jobType}, clientHires = {cHires} !")
											print('Load only first 5000 jobs')
											N = 100
										req = [req_Generator(i, Auth, cat_uid = category['uid'], subcat_uid = subcategory['uid'], Service = Service['label'], jobType = jType, cHires = hires) for i in range(1, N+1)]
										requests_List.append(req)
	return HomePage, requests_List

	
def Get(URL, HomePage, UserAgent, cookies, proxy = False):
	from requests.packages.urllib3.exceptions import InsecureRequestWarning
	requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
	cookies_jar = requests.cookies.RequestsCookieJar()
	for cookie in cookies:
		if cookie['name'] == 'XSRF-TOKEN': Token = cookie['value']
		cookies_jar.set(cookie['name'],cookie['value'], domain = cookie['domain'], path = cookie['path'], secure = cookie['secure'])
		
	My_headers={'Accept': 'application/json, text/plain, */*',
			'Referer': HomePage,
			'User-Agent': UserAgent,
			'X-Odesk-User-Agent': 'oDesk LM',
			'X-Requested-With': 'XMLHttpRequest',
			'X-Odesk-Csrf-Token': Token}
	if proxy != False:
		proxyDict = {#"ftp"   : f"ftp://{proxy}",
					"http"  : f"http://{proxy}",
					"https" : f"https://{proxy}"}
	else: proxyDict = {}
	for i in range(5):
		try:
			req = requests.get(URL, headers = My_headers, cookies = cookies_jar, proxies = proxyDict, verify = False)
			req.connection.close()
			
			if req.status_code == requests.codes.ok: return req
			elif req.status_code == 403:
				print('Status code - 403 Forbidden. Blocked!')
				break
			else: 
				print(f'Status code - {req.status_code}. Retry - {i}')	
				time.sleep(2)
		except requests.exceptions.ProxyError as e: print(f'ProxyError. i={i}. Continue...')
		except Exception as e:
			import sys
			type, value, traceback = sys.exc_info()
			print(f"error in line:{traceback.tb_lineno/ntype/nvalue}")
			module = e.__class__.__module__
			if module is None or module == str.__class__.__module__: Error_class_name = e.__class__.__name__
			else: Error_class_name = module + '.' + e.__class__.__name__
			print(Error_class_name)
			input('Paused. Press any key.')
	return False

def Get_HTML(URL, HomePage, UserAgent, cookies, proxy = False):
	from requests.packages.urllib3.exceptions import InsecureRequestWarning
	requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
	cookies_jar = requests.cookies.RequestsCookieJar()
	for cookie in cookies:
		if cookie['name'] == 'XSRF-TOKEN': Token = cookie['value']
		if cookie['name'] == 'oauth2_global_js_token': JS_Token = cookie['value']
		cookies_jar.set(cookie['name'],cookie['value'], domain = cookie['domain'], path = cookie['path'], secure = cookie['secure'])
		
	My_headers={'Host': 'www.upwork.com',
			'User-Agent': UserAgent,
			'Accept': 'application/json, text/plain, */*',
			'Referer': HomePage,
			'X-Oauth2-Required': 'true',
			'X-Odesk-User-Agent': 'oDesk LM',
			'X-Requested-With': 'XMLHttpRequest',
			'Authorization': 'Bearer ' + JS_Token,
			'X-Odesk-Csrf-Token': Token,
			'Connection': 'keep-alive',
			'TE':'Trailers'}
			
	if proxy != False:
		proxyDict = {#"ftp"   : f"ftp://{proxy}",
					"http"  : f"http://{proxy}",
					"https" : f"https://{proxy}"}
	else: proxyDict = {}
	for i in range(5):
		req = requests.get(URL, headers = My_headers, cookies = cookies_jar, proxies = proxyDict, verify = False)
		req.connection.close()
		
		if req.status_code == requests.codes.ok: return req
		elif req.status_code == 403:
			print('Status code - 403 Forbidden. Blocked!')
			return req
		else: 
			print(f'Status code - {req.status_code}. Retry - {i}')	
			time.sleep(2)

	return False
	
if __name__ == '__main__':
	pass
	