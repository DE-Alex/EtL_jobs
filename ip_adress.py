import sys
import time
import requests
import configparser
from pathlib import Path

config = configparser.ConfigParser()
config.read(Path(sys.path[0], 'pipeline.conf'))
proxy = config['parser_config']['proxy']

logs_folder = Path(sys.path[0], config['parser_paths']['logs_folder'])
ip_log_path = Path(logs_folder, config['parser_paths']['ip_file'])

mitm_folder = Path(sys.path[0], config['parser_paths']['mitm_folder'])
mitm_cert_path = Path(mitm_folder, config['parser_paths']['mitm_certificate'])

def request_service(proxy_port = False):
    URL = 'https://api.ipify.org'
    if proxy_port == False: 
        ip = requests.get(URL).text
    else:
        proxyDict = {"http" : f"http://{proxy_port}",
                    "https" : f"https://{proxy_port}"}
        ip = requests.get(URL, proxies = proxyDict, verify = mitm_cert_path).text
    return ip

def check_ip():
    while True:
        try:
            my_ip = request_service()
            if proxy != 'no':
                proxy_ip = request_service(proxy)
            else: proxy_ip = 'no proxy'
            break
        except requests.exceptions.ConnectionError:
            print('ip check failed')
            time.sleep(5)
            
    try:
        with open(ip_log_path) as file:
            result = file.read().split('\n')
        ip_logs = {key: int(value) for key, value in [i.split(':') for i in result if i != '']}
    except FileNotFoundError as e:
        print(f'{ip_log_path} not found.')
        ip_logs = None

    if ip_logs == None:
        ip_logs = {proxy_ip:1}
    elif proxy_ip in ip_logs.keys():
        ip_logs[proxy_ip] = ip_logs[proxy_ip] + 1
    else:
        ip_logs[proxy_ip] = 1
    if ip_log_path:
        with open (ip_log_path, 'w') as file:
            for key, value in ip_logs.items():
                file.write(f'{key}:{value}\n')
                
    print(f'''===========Proxy check==========
My IP             :{my_ip}
My IP (with proxy):{proxy_ip}
It was used {ip_logs[proxy_ip]-1} time(s) before.
================================''')
    return proxy_ip
    

if __name__ == '__main__':
    while True:
        check_ip()
        time.sleep(5)
        
        
    
        
    
    
