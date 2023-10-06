import math
import os, sys
import requests, time
import configparser
from pathlib import Path
from datetime import datetime
from dateutil.tz import tzlocal
tzlocal = tzlocal()

import parse_json
import cookies_mod
import mitm.change_mitm_headers

parent_dir = os.path.abspath(os.path.join(sys.path[0], '..'))
config = configparser.ConfigParser() 
config.read(Path(parent_dir, 'pipeline.conf'))

filename_date_format = config['general']['filename_date_format']
logs_folder = Path(parent_dir, config['general']['logs_folder'])

err_path = Path(logs_folder, config['upwork']['errors_file'])
user_agent = config['upwork']['user_agent']
mitm_folder = Path(parent_dir, config['upwork']['scripts_folder'], config['upwork']['mitm_folder'])
mitm_cert_path = Path(mitm_folder, config['upwork']['mitm_certificate'])
proxy = config['upwork']['proxy']

mitm.change_mitm_headers.write_in(user_agent)
    
def requests_pattern(page = 1, subcat_uid = '', jobType = '', cHires = '', proposals = '', duration_v3 = ''):
    if page == 'start':
        request = 'https://www.upwork.com/nx/jobs/search/?sort=recency' #& на конце после recency?
        return request
    
    url_parts = ['https://www.upwork.com/ab/jobs/search/url?per_page=50','sort=recency']

    if subcat_uid != '':
        url_parts.append(f'subcategory2_uid={subcat_uid}')
    if jobType != '': 
        url_parts.append(f't={jobType}')
    if cHires != '': 
        url_parts.append(f'client_hires={cHires}')
    if proposals != '': 
        url_parts.append(f'proposals={proposals}')
    if duration_v3 != '': 
        url_parts.append(f'duration_v3={duration_v3}')
    if page > 1: 
        url_parts.append(f'page={page}')    
    
    request = ('&').join(url_parts)
    return request

def form_requests_list(json_data, previous_url):
    #use upwork's search options as filters for iteration
    subcategories = parse_json.parse_subcats_uids(json_data)
    filters = {0:subcategories,
               1:['0', '1'],                               #'jobType': 0-Hourly, 1 - Fixed price
               2:['0', '1-9', '10-'],                      #'clientHires': no hires, 1-9 hires, 10+ hires
               3:['0-4', '5-9', '10-14', '15-19', '20-49'],#'proposals': less than 5, 'a' to 'b' proposals
               4:['weeks', 'months', 'semester', 'ongoing']#'duration_v3'(project length): less 1 month, 1-3 months, 3-6 months, 6+ months
               }
    i = 0
    params = ['']*5
    req_list, previous_url = requests_generator(i, previous_url, params, filters)
    return req_list, previous_url

def requests_generator(i, previous_url, params, filters):
    req_list = []
    items = filters[i]
       
    for item in items:
        params[i] = item
        p0, p1, p2, p3, p4 = params
        check_page_url = requests_pattern(1, p0, p1, p2, p3, p4)
        result = send_request(check_page_url, previous_url)
        json_data = result.json()
        pages = parse_json.total_jobs(json_data)
        previous_url = check_page_url
            
        N = math.ceil(pages/50) #round to bigger number
        if N > 100 and i < 5:
            req, previous_url = requests_generator(i+1, previous_url, params, filters)
            req_list.extend(req)
        else:
            if N >= 100:
                N = 100
                print(f'\nToo many jobs in subcat uid={p0} with jobType = {p1}, clientHires = {p2} proposals = {p3} duration_v3 = {p4} !')
                print('Load only first 5000 jobs')
                import json
                now = datetime.now(tzlocal).replace(microsecond = 0)
                dt = datetime_to_str(now, filename_date_format)
                dump_path = Path(sys.path[0], 'Temp', f'{dt}_Error.json')
                with open(dump_path, 'a') as file:
                    json.dump(json_data, file)
            else:
                pass
            p0, p1, p2, p3, p4 = params
            req = [requests_pattern(i, p0, p1, p2, p3, p4) for i in range(1, N+1)]
            req_list.append(req)
            print(f'Requests: +{len(req)}')
    params[i] = ''
    return req_list, previous_url
     
def send_request(url, previous_url):
    cookies_jar = requests.cookies.RequestsCookieJar()
    
    if proxy == 'no': 
        proxy_dict = {}
    else:
        proxy_dict = {'http': f'http://{proxy}', 'https': f'https://{proxy}'}
        
    time.sleep(3)
    i = 0
    while True:
        i = i + 1
        cookies = cookies_mod.select_cookies()

        for cookie in cookies:
            if cookie['name'] == 'oauth2_global_js_token': 
                Token = 'Bearer ' + cookie['value']
            cookies_jar.set(cookie['name'],cookie['value'])
        
            
        my_headers={'User-Agent' : user_agent,
                    'Accept': 'application/json, text/plain, */*',
                    'Accept-Language' : 'en-US,en;q=0.5',
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
            if proxy == 'no':
                #default SSL
                SSL_verify = True 
            else:
                #mitm proxy SSL
                SSL_verify = mitm_cert_path
            req = requests.get(url, headers = my_headers, cookies = cookies_jar, proxies = proxy_dict, verify = SSL_verify)
            req.connection.close()
            
            if req.status_code == requests.codes.ok: 
                return req
            else:
                time_now = datetime.now(tzlocal).replace(microsecond = 0).isoformat()#datetime obj to str in isoformat
                with open(err_path, 'a') as file: 
                    file.write(f'{time_now} {i}:code {req.status_code}\n')
                
                if req.status_code == 403: 
                    print(f'{i}: 403 Forbidden. Paused for 5 min.')
                    time.sleep(300)
                else: 
                    print(f'{i}: status code {req.status_code}. Paused for 0.5 min.')
                    time.sleep(30)
            if i >= 6:
                print('Paused for 30 min.')
                time.sleep(1800)
                i = 0               
        except requests.exceptions.ProxyError as e: 
            print(f'{i}: ProxyError: ', e)
            time_now = datetime.now(tzlocal).replace(microsecond = 0).isoformat()#datetime obj to str in isoformat
            with open(err_path, 'a') as file: 
                file.write(time_now + '\n' + e + '\n')
            time.sleep(2)
    
if __name__ == '__main__':
    pass
    
    
