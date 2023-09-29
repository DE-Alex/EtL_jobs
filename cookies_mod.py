import sys
import sqlite3
import lz4.block as lz4
import sqlite3
import configparser
from pathlib import Path

config = configparser.ConfigParser()
config.read(Path(sys.path[0], 'pipeline.conf'))
cookies_sqlight_path = config["parser_config"]["FireFox_cookies_sqlight_path"]
cookies_lz4_path = config["parser_config"]["FireFox_cookies_lz4_path"]

def read_cookies_sqlight():
    #In Linux FireFox block sqlite file with cookies
    #Let's copy file to read cookies later
    source_path = Path(cookies_sqlight_path)
    tmp_path = Path(sys.path[0], 'Temp', 'cookies.sqlite')
    tmp_path.write_bytes(source_path.read_bytes())
    path = str(tmp_path)
   
    query = '''SELECT name, 
                      value,
                      host
                      /*lastAccessed*/
               FROM 
                    moz_cookies;'''
    try:
        conn = sqlite3.connect(rf'file:{path}', uri = True)   #uri=True - read only mode!
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
    except sqlite3.DatabaseError as err:
        print('In command: ', query)
        print('Error type: ', err)
        result = False
    finally:
        cursor.close()
        conn.close()
    return result
        
def read_cookies_json():
    path = cookies_lz4_path
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
    cookies = select_cookies()
    print('cookies:', len(cookies))
