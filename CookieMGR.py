import MyLibs.SQLite
import MyLibs.PyObject_to_PyFile as PyFile
import lz4.block as lz4
import time
from datetime import datetime, timedelta

hostNames = ['www.upwork.com', '.www.upwork.com', '.upwork.com']

def ReadSqlite():
	path = r'C:\Users\User\AppData\Roaming\Mozilla\Firefox\Profiles\9abm4non.default-release\cookies.sqlite'
	table_name = 'moz_cookies'
	columns = ['name', 'value', 'host', 'lastAccessed']
	db = MyLibs.SQLite.connect(rf'file:{path}', uri = True)	#read only mode!
	data = MyLibs.SQLite.Select(table_name, db, select_col = columns)
	db.close()
	return data	
	
def ReadJson():
	path = r'C:\Users\User\AppData\Roaming\Mozilla\Firefox\Profiles\9abm4non.default-release\sessionstore-backups\recovery.jsonlz4'
	while True:
		try:
			file = open(path, "rb")
			if file.read(8) != b"mozLz40\0":
				print("Invalid magic number")
				input()
			binary_data= lz4.decompress(file.read())
			break
		except Exception as e:
			print(e)
	string = binary_data.decode('utf-8')
	string = string.replace('true', 'True')
	string = string.replace('false', 'False')
	string = string.replace('null', 'None')
	All_Json = eval(string)
	cookies = All_Json['cookies']
	return cookies, All_Json

def UpdateCookies():
	data = ReadSqlite()
	Cookies_SQL = []
	LA = []
	for row in data:
		name, value, host, lastAccessed = row
		if host in hostNames: 
			cookie = {'name': name, 'value': value}
			Cookies_SQL.append(cookie)
			LA.append(lastAccessed)
	cookies, _ = ReadJson()
	Cookies_json = []
	for cookie in cookies:
		if cookie['host'] in hostNames: 
			cookie = {'name': cookie['name'], 'value': cookie['value']}
			Cookies_json.append(cookie)
	MOZLcookies = Cookies_SQL + Cookies_json
	return MOZLcookies

	
if __name__ == '__main__':
	pass

	# UpdateCookies()	
	# input()
	# import time
	# data = ReadSqlite()
	# Cookies_SQL = []
	# for row in data:
		# name, value, host , expiry, creationTime = row
		# if host in hostNames: 
			# try: result = time.gmtime(expiry)
			# except: result = time.gmtime(expiry//100)
			# #result: tm_year=2019, tm_mon=12, tm_mday=7, tm_hour=12, tm_min=30, tm_sec=30, tm_wday=5, tm_yday=341, tm_isdst=0
			# expiry = f'{result.tm_hour}:{result.tm_min} {result.tm_mday}.{result.tm_mon}.{result.tm_year}'
			# #print(expiry)
			# cookie = {'name': name, 'value': value, 'expiry' : expiry}
			# Cookies_SQL.append(cookie)
	# cookies, All_Json = ReadJson()
	# Cookies_json = []
	# for cookie in cookies:
		# if cookie['host'] in hostNames: 
			# name = cookie['name']
			# value = cookie['value']
			# if 'expiry' not in list(cookie.keys()): expiry = '0'
			# else:
				# expiry = cookie['expiry']
				# #print(expiry, type(expiry), end = '')
				# result = time.gmtime(expiry)
				# expiry = f'{result.tm_hour}:{result.tm_min} {result.tm_mday}.{result.tm_mon}.{result.tm_year}'
				# #print(expiry)
			# cookie = {'name': name, 'value': value, 'expiry' : expiry}
			# Cookies_json.append(cookie)
	
	# cookies = Cookies_SQL + Cookies_json
	# tmp = []
	# for cookie in cookies:
		# expiry = cookie['expiry']
		# tmp.append(cookie['name'] + ' ' +  expiry)
	# import MyLibs.PyObject_to_PyFile
	# MyLibs.PyObject_to_PyFile.Write(tmp, r'D:\Shapovalov\svoe\Python\PY\Parser5\Cookies\cookies_json.txt')
	# MyLibs.PyObject_to_PyFile.Write(All_Json, r'D:\Shapovalov\svoe\Python\PY\Parser5\Cookies\All_Json.txt')
	