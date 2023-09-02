import sqlite3
import lz4.block as lz4

def read_cookies_sqlight():
	path = r'C:\Users\User\AppData\Roaming\Mozilla\Firefox\Profiles\9abm4non.default-release\cookies.sqlite'
	table_name = 'moz_cookies'
	columns = ['name', 'value', 'host'] #, 'lastAccessed']
    select_col = (', ').join(columns)
    
    query = f'SELECT {select_col} FROM {table_name}'
    
    try:
        conn = MyLibs.SQLite.connect(rf'file:{path}', uri = True)	#uri=True - read only mode!
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
	except sqlite3.DatabaseError as err:
		print('In command: ', action)
		print('Error type: ', err)
		cursor.rollback()
		result = False
    finally:
        cursor.close()
        conn.close()
       
    return result
        
def read_cookies_json():
	path = r'C:\Users\User\AppData\Roaming\Mozilla\Firefox\Profiles\9abm4non.default-release\sessionstore-backups\recovery.jsonlz4'
	while True:
		try:
			file = open(path, "rb")
			if file.read(8) != b"mozLz40\0":
				print("Invalid magic number")
				input()
			binary = lz4.decompress(file.read())
			break
		except Exception as e:
			print(e)
	string = binary.decode('utf-8')
	string = string.replace('true', 'True')
	string = string.replace('false', 'False')
	string = string.replace('null', 'None')
	json_all = eval(string)
	cookies = json_all['cookies']
	return cookies

def select_cookies():
    hostNames = ['www.upwork.com', '.www.upwork.com', '.upwork.com']
    
	result_1 = read_cookies_sqlight()
	upw_cookies_sql = []
	#LA = []
	for row in result_1:
		name, value, host = row #, lastAccessed = row
		if host in hostNames: 
			cookie = {'name': name, 'value': value}
			upw_cookies_sql.append(cookie)
			#LA.append(lastAccessed)
            
	result_2 = read_cookies_json()
	upw_cookies_json = []
	for cookie in result_2:
		if cookie['host'] in hostNames: 
			cookie = {'name': cookie['name'], 'value': cookie['value']}
			upw_cookies_json.append(cookie)
            
	upw_cookies = upw_cookies_sql + upw_cookies_json
	return upw_cookies

if __name__ == '__main__':
	pass
