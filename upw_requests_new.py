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
    #request = ('&').join([...])
    
    return request


def form_requests_list(json_data, previous_url, user_agent, err_log, proxy):
    #global user_agent, err_log, proxy
    occupations = json_data['searchResults']['facets']['occupations']
    print(f"Total {json_data['searchResults']['paging']['total']} jobs found")

    #different filters for iteration
    filters = {2:['0', '1'],                               #'jobType': 0-Hourly, 1 - Fixed price
               3:['0', '1-9', '10-'],                      #'clientHires': no hires, 1-9 hires, 10+ hires
               4:['0-4', '5-9', '10-14', '15-19', '20-49'],#'proposals': less than 5, 'a' to 'b' proposals
               5:['weeks', 'months', 'semester', 'ongoing']#'duration_v3'(project length): less 1 month, 1-3 months, 3-6 months, 6+ months
               }
               
    reqList = []
    i = 0
    params = ['']*5
    previous_url, reqList = requests_generator(i, reqList, previous_url, params)
    
    return previous_url, reqList

def requests_generator(i, reqList, previous_url, params):
    if i == 0:
        items = occupations
    elif i == 1:
        category = params[0]
        items = occupations[category]['occupations']
    elif i > 1:
        items = filters[i]
       
    for item in items:
        if i < 2:
            param[i] = item['uid']
            pages = item['count']
        else:
            param[i] = item
            p1, p2, p3, p4, p5 = params
            req = requests_pattern(1, p1, p2, p3, p4, p5)
            get_req = send_request(req, previous_url)
            previous_url = req
            result = get_req.json()
            pages = result['searchResults']['paging']['total']
            
        N = math.ceil(pages/50) #round to bigger number
        if N > 100 and i < 5:
            i = i + 1
            requests_generator(i, reqList, previous_url, params)
        else:
            if N > 100:
                N = 100
                cat_label = occupations[p1]['label']
                subcat_label = occupations[p1]['occupations'][p2]
                print(f"\nToo many jobs in {cat_label}{subcat_label} with jobType = {p3}, clientHires = {p4} proposals = {p5} duration_v3 = {p6} !")
                print('Load only first 5000 jobs')
                import json
                from pathlib import Path
                dt = datetime_to_str(now_local(), '%d.%m.%Y %H.%M')
                dump_path = Path(sys.path[0], 'Temp', f'{dt}_Error.json')
                with open(dump_path, 'a') as file:
                    json.dump(result, file)
       
            p1, p2, p3, p4, p5 = params
            req = [requests_pattern(i, p1, p2, p3, p4, p5) for i in range(1, N+1)]
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
	
    form_requests_list(json_data, previous_url, user_agent, err_log, proxy)
    
    
