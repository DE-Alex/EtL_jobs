import math
import sys, requests, time
import configparser
from pathlib import Path
from dateutil.tz import tzutc, tzlocal
from datetime import datetime, timedelta
tzlocal = tzlocal()
tzutc = tzutc()

import cookies_mod
import mitm.change_mitm_headers


config = configparser.ConfigParser()
config.read(Path(sys.path[0], 'pipeline.conf'))

proxy = config['parser_config']['proxy']
dt_format = config['parser_config']['date_format']
user_agent = config['parser_config']['user_agent']

logs_folder = Path(sys.path[0], config['parser_paths']['logs_folder'])
err_path = Path(logs_folder, config['parser_paths']['errors_file'])

mitm_folder = Path(sys.path[0], config['parser_paths']['mitm_folder'])
mitm_cert_path = Path(mitm_folder, config['parser_paths']['mitm_certificate'])

mitm.change_mitm_headers.write_in(user_agent)
    
def requests_pattern(page = 1, cat_uid = '', subcat_uid = '', jobType = '', cHires = '', proposals = '', duration_v3 = ''):
    if page == 'start':
        request = 'https://www.upwork.com/nx/jobs/search/?sort=recency' #& на конце после recency?
        return request
    
    url_parts = ['https://www.upwork.com/ab/jobs/search/url?per_page=50','sort=recency']

    if subcat_uid != '':
        url_parts.append(f'subcategory2_uid={subcat_uid}')
    elif cat_uid != '': 
        url_parts.append(f'category2_uid={cat_uid}')
        
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
    '''
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
        page_num = ''
    else: 
        page_num = f'page={page}'
    '''
    #request = f'https://www.upwork.com/ab/jobs/search/url?per_page=50&sort=recency&{cat_uid}{subcat_uid}{jobType}{cHires}{proposals}{duration_v3}{page_num}'
    return request


def form_requests_list(json_data, previous_url):
    occupations = json_data['searchResults']['facets']['occupations']
    print(f"Total {json_data['searchResults']['paging']['total']} jobs found")

    #job's search options as filters for iteration
    filters = {2:['0', '1'],                               #'jobType': 0-Hourly, 1 - Fixed price
               3:['0', '1-9', '10-'],                      #'clientHires': no hires, 1-9 hires, 10+ hires
               4:['0-4', '5-9', '10-14', '15-19', '20-49'],#'proposals': less than 5, 'a' to 'b' proposals
               5:['weeks', 'months', 'semester', 'ongoing']#'duration_v3'(project length): less 1 month, 1-3 months, 3-6 months, 6+ months
               }
               
    #req_list = []
    i = 0
    params = ['']*6
    previous_url, req_list = requests_generator(i, previous_url, params, occupations, filters)
    
    return req_list, previous_url

def requests_generator(i, previous_url, params, occupations, filters):
    req_list = []
    #print('i=', i)
    if i <= 1:
        items = occupations
    #elif i == 1:
    #    category = params[0]
    #    items = occupations[category]['occupations']
    elif i > 1:
        items = filters[i]
        #print('filters = ', items)
       
    for item in items:
        if i <= 1:
            params[i] = item['uid'] #uid of category/subcategory
            pages = item['count']
            occupations = item['occupations']
            #print(params[i], pages)
        else:
            params[i] = item
            #print(params)
            p0, p1, p2, p3, p4, p5 = params
            check_pages_url = requests_pattern(1, p0, p1, p2, p3, p4, p5)
            get_req = send_request(check_pages_url, previous_url)
            previous_url = check_pages_url
            result = get_req.json()
            pages = result['searchResults']['paging']['total']
            
        N = math.ceil(pages/50) #round to bigger number
        if N > 100 and i < 6:
            previous_url, req = requests_generator(i+1, previous_url, params, occupations, filters)
            req_list.extend(req)
        else:
            if N >= 100:
                N = 100
                cat_label = occupations[p1]['label']
                subcat_label = occupations[p1]['occupations'][p2]
                print(f"\nToo many jobs in {cat_label}{subcat_label} with jobType = {p3}, clientHires = {p4} proposals = {p5} duration_v3 = {p6} !")
                print('Load only first 5000 jobs')
                import json
                dt = datetime_to_str(now_local(), dt_format)
                dump_path = Path(sys.path[0], 'Temp', f'{dt}_Error.json')
                with open(dump_path, 'a') as file:
                    json.dump(result, file)
            else:
                pass
            p0, p1, p2, p3, p4, p5 = params
            #print(params)
            req = [requests_pattern(i, p0, p1, p2, p3, p4, p5) for i in range(1, N+1)]
            req_list.append(req)
            print(f'Requests: +{len(req)}')
            #print('Len req_list:', len(req_list))
    params[i] = ''
    #print('Len req_list:', len(req_list))
    
 
    # req_path = Path(logs_folder, f'requests.log')
    # import os
    # directory = os.path.dirname(req_path)
    # if not os.path.exists(directory):
        # os.makedirs(directory)
    # try:	
        # with open (req_path, 'w') as file:
            # for rec_group in req_list:
                # group_to_dump = ('\n').join(rec_group)
                # file.write(f'{group_to_dump}\n***\n')
    # except:
        # with open (req_path, 'w', encoding = 'utf-8') as file:
            # for rec in req_list:
                # group_to_dump = ('\n').join(rec_group)
                # file.write(f'{group_to_dump}\n***\n')
    
    return previous_url, req_list
     
def send_request(url, previous_url):

    cookies_jar = requests.cookies.RequestsCookieJar()
    
    if proxy != False: 
        proxy_dict = {"http"  : f"http://{proxy}", "https" : f"https://{proxy}"}
    else: 
        proxy_dict = {}
        
    time.sleep(3)
    i = -1
    while True:
        i += 1
        cookies = cookies_mod.select_cookies()

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
            req = requests.get(url, headers = my_headers, cookies = cookies_jar, proxies = proxy_dict, verify = mitm_cert_path)
            req.connection.close()
            
            if req.status_code == requests.codes.ok: 
                return req
            else:
                time_now = datetime.strftime(datetime.now(tzlocal), dt_format)#datetime obj to str
                with open(err_path, 'a') as file: 
                    file.write(f'{time_now} {i}:code {req.status_code}\n')
                
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
            time_now = datetime.strftime(datetime.now(tzlocal), dt_format)#datetime obj to str
            with open(err_path, 'a') as file: 
                file.write(time_now + '\n' + e + '\n')
            time.sleep(2)
    
if __name__ == '__main__':
    
    pass
    
    
