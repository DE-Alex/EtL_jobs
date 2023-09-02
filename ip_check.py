import time
import requests

def request_ip(proxy = False):
    path_to_mtmproxy_certificate = 'D:\MTM_Proxy\mitmproxy_cert\mitmproxy-ca-cert.pem'
    URL = 'https://api.ipify.org'
    if proxy == False: 
        ip = requests.get(URL).text
    else:
        proxyDict = {#"ftp" : f"ftp://{proxy}",
                    "http" : f"http://{proxy}",
                    "https" : f"https://{proxy}"}
        ip = requests.get(URL, proxies = proxyDict, verify = path_to_mtmproxy_certificate).text
    return ip

def test_ip(proxy, logfile = False):
    import py_object_to_file as pyfile
    while True:
        try:
            my_ip = request_ip()
            proxy_ip = request_ip(proxy)
            break
        except requests.exceptions.ConnectionError:
            print('ip check failed')
            time.sleep(5)
    if logfile: 
        ip_logs = pyfile.read(logfile)
    else: 
        ip_logs == None
    if ip_logs == None:
        ip_logs = {proxy_ip:1}
    elif proxy_ip in ip_logs.keys():
        ip_logs[proxy_ip] = ip_logs[proxy_ip] + 1
    else:
        ip_logs[proxy_ip] = 1
        
    if logfile:
        pyfile.write(ip_logs, logfile)
        
    print(f'''My IP:           {my_ip}
My IP (with proxy):{proxy_ip}
It was used {ip_logs[proxy_ip]-1} time(s) before.
=========================''')
    return proxy_ip
    

if __name__ == '__main__':
    proxy = '127.0.0.1:35685'#mitmproxy

    #proxy = False
    # proxy = '167.172.146.246:8080' #Payed Proxy x.botproxy.net:8443

    ip = request_ip()
    print('My public IP address is: {}'.format(ip))
    

        
    ip = request_ip(proxy)
    print('My public IP address (with proxy) is: {}'.format(ip))
    
    

    
    # import requests

    # res = requests.get('http://httpbin.org/ip', proxies={'http': 'http://167.172.146.246:8080','https': 'http://167.172.146.246:8080'},)
    # print(res.text)
    logfile = 'D:\Shapovalov\svoe\Python\PY\Parser5\Log\IP.log'

    while True:
        # try:
            # ip = request_ip(proxy)
            # print('My public IP address (with proxy) is: {}'.format(ip))
            # time.sleep(3)
        # except Exception as e:
            # print(e)
            # print('IP check failed')
            # time.sleep(1)

        test_ip(proxy, logfile)
        time.sleep(3600)
        
        
    
        
    
    