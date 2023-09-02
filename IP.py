import sys, time
import requests


def IpCheck(proxy = False):
	path_to_mtmproxy_certificate = 'D:\MTM_Proxy\mitmproxy_cert\mitmproxy-ca-cert.pem'
	URL = 'https://api.ipify.org'
	if proxy == False: ip = requests.get(URL).text
	else:
		proxyDict = {#"ftp" : f"ftp://{proxy}",
					"http" : f"http://{proxy}",
					"https" : f"https://{proxy}"}
		ip = requests.get(URL, proxies = proxyDict, verify = path_to_mtmproxy_certificate).text
	return ip

def IpLog(proxy, logfile = False):
	import MyLibs.PyObject_to_PyFile as PyFile
	while True:
		try:
			my_ip = IpCheck()
			proxy_ip = IpCheck(proxy)
			break
		except requests.exceptions.ConnectionError:
			print('IP check failed')
			time.sleep(5)
	if logfile: dict = PyFile.Read(logfile)
	else: dict == None
	if dict == None: dict = {proxy_ip:1}
	elif proxy_ip in dict.keys(): dict[proxy_ip] = dict[proxy_ip] + 1
	else: dict[proxy_ip] = 1
	if logfile: PyFile.Write(dict, logfile)
	print(f'''My IP:		   {my_ip}
My IP (with proxy):{proxy_ip}
It will be used {dict[proxy_ip]} time(s).
=========================''')
	return proxy_ip
	

if __name__ == '__main__':
	proxy = '127.0.0.1:35685'#mitmproxy(local network)

	#proxy = False
	# proxy = '167.172.146.246:8080' #Payed Proxy x.botproxy.net:8443

	ip = IpCheck()
	print('My public IP address is: {}'.format(ip))
	

		
	ip = IpCheck(proxy)
	print('My public IP address (with proxy) is: {}'.format(ip))
	
	

	
	# import requests

	# res = requests.get('http://httpbin.org/ip', proxies={'http': 'http://167.172.146.246:8080','https': 'http://167.172.146.246:8080'},)
	# print(res.text)
	logfile = 'D:\Shapovalov\svoe\Python\PY\Parser5\Log\IP.log'

	while True:
		# try:
			# ip = IpCheck(proxy)
			# print('My public IP address (with proxy) is: {}'.format(ip))
			# time.sleep(3)
		# except Exception as e:
			# print(e)
			# print('IP check failed')
			# time.sleep(1)

		IpLog(proxy, logfile)
		time.sleep(3600)
		
		
	
		
	
	