import json
import math
from MyLibs.requests_by_URL import Get_request

def requestGenerator(i, Auth, cat_uid = '', subcat_uid = '', Service = '', jobType = ''):
	if jobType != '': jobType = f'&t={jobType}'
	if cat_uid != '': cat_uid = f'category2_uid={cat_uid}&'
	if subcat_uid != '':
		subcat_uid = f'&subcategory2_uid={subcat_uid}'
		cat_uid = ''
	if Service != '':
		L = Service.replace(' ','+')
		Service = f'q={L}&'
	
	request = f'https://www.upwork.com/{Auth}url?{cat_uid}page={i}&per_page=50&{Service}sort=recency{subcat_uid}{jobType}'
	return request

def Jobs(json_PyObj, Auth, HomePage, UserAgent, cookies, proxy_port):
	occupations = json_PyObj['searchResults']['facets']['occupations']
	print(f"Total {json_PyObj['searchResults']['paging']['total']} jobs found")
	
	requests_List = []
	for category in occupations:
		N = math.ceil(category['count']/50) #round to bigger number
		if N < 4999:
			req = [requestGenerator(i, Auth, cat_uid = category['uid']) for i in range(1, N+1)]
			requests_List.extend(req)
		else:
			subcategories = category['occupations']
			for subcategory in subcategories:
				N = math.ceil(subcategory['count']/50)
				if N < 4999:
					req = [requestGenerator(i, Auth, subcat_uid = subcategory['uid']) for i in range(1, N+1)]
					requests_List.extend(req)
				else:
					Services = subcategory['occupations']
					for Service in Services:
						N = math.ceil(Service['count']/50)
						if N < 4999:
							req = [requestGenerator(i, Auth, cat_uid = category['uid'], subcat_uid = subcategory['uid'], Service = Service['label']) for i in range(1, N+1)]
							requests_List.extend(req)
						else:
							#============ t = 0 ============
							req = requestGenerator(1, Auth, cat_uid = category['uid'], subcat_uid = subcategory['uid'], Service = Service['label'], jobType = '0')
							get_req = Get_request(req, HomePage, UserAgent, cookies, proxy_port)
							HomePage = req
							json_PyObj = get_req.json()
							pages  = json_PyObj['searchResults']['paging']['total']
							N = math.ceil(pages/50)
							assert N < 4999, f"Attention! Again too many jobs in {category['label']}{subcategory['label']}{Service['label']}t=0!"
							req = [requestGenerator(i, Auth, cat_uid = category['uid'], subcat_uid = subcategory['uid'], Service = Service['label'], jobType = '0') for i in range(1, N+1)]
							requests_List.extend(req)
							#============ t = 1 ============
							req = requestGenerator(1, Auth, cat_uid = category['uid'], subcat_uid = subcategory['uid'], Service = Service['label'], t='&t=1')
							get_req = Get_request(req, HomePage, UserAgent, cookies, proxy_port)
							HomePage = req
							json_PyObj = get_req.json()
							pages  = json_PyObj['searchResults']['paging']['total']
							N = math.ceil(pages/50)
							assert N < 4999, f"Attention! Again too many jobs in {category['label']}{subcategory['label']}{Service['label']}t=1!"
							req = [requestGenerator(i, Auth, cat_uid = category['uid'], subcat_uid = subcategory['uid'], Service = Service['label'], jobType = '1') for i in range(1, N+1)]
							requests_List.extend(req)
	
	requests_List.sort()
	return HomePage, requests_List


	
if __name__ == '__main__':
	import MyLibs.PyObject_to_PyFile as PyFile
	with open(r'D:\xxx\xxx\xxx\PY\Raw_Jsons\Full_DB_24_05\1.json') as f:
		json_data = f.read()
		
	json_PyObj = json.loads(json_data)
	
	
	requests_List = Jobs(json_PyObj)
	PyFile.Write(requests_List,r'D:\xxx\xxx\xxx\PY\Parser3\DataToScrape\temp.txt')
	print(len(requests_List))	
	