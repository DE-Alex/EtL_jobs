#Write Python object to Python file 
import pprint
import os

def Write(PyObject, path_to_file):
	file = open(path_to_file, 'w')
	file.write(pprint.pformat(PyObject))
	file.close()

def Read_all(path_to_file):
	file = open(path_to_file)
	try:
		Object = eval(file.read())
	except:
		print path_to_file, "is epmty. DB_proxy = []"
		Object = []
	file.close()
	return Object

def Read_good_proxy(rating, path_to_proxy_DB):
	Proxy_DB = Read_all(path_to_proxy_DB)
	Good_proxy = []
	for proxy_info in Proxy_DB: #proxy_info = [N_rating,ip_port,N_alive,N_total]
		N_rating = proxy_info[0] #N_rating = N_alive/N_total
		if N_rating >= rating: Good_proxy.append(proxy_info)
	return Good_proxy
	
def Load_DB(path_to_proxy_DB, path_to_new_proxy):
		
	proxy_DB = Read_all(path_to_proxy_DB)
	#print 'Proxy_DB:', proxy_DB
	proxy_list = [line[1] for line in proxy_DB]
	#print 'proxy_list:', proxy_list
	
	try:
		New_hosts = [host.strip() for host in open(path_to_new_proxy).readlines()] #[ip:port,ip:port]
		#print 'New_hosts:', New_hosts
	except:
		New_hosts = [] #if no file with new hosts
		
	Difference = list(set(New_hosts) - set(proxy_list)) #Difference (New hosts that are not in proxy_DB
	for new_proxy in Difference:
		proxy_DB.append([None,new_proxy,0,0])
	#print 'New proxy added:', Difference
	print 'Total %d proxy added' %(len(Difference))
	
		
	proxy_DB.sort(reverse = True)
	Write(proxy_DB, path_to_proxy_DB)
	
	return proxy_DB
	
	
	
	
if __name__ == '__main__':
	import os
	path_to_proxy_DB = os.path.dirname(__file__) + '\DB_proxy_test.txt'
	
	path_to_new_proxy = os.path.dirname(__file__) + '\New_proxy_test.txt'

	Load_DB(path_to_proxy_DB, path_to_new_proxy)
	