import MyLibs.SQLite
import MyLibs.Scan_DirsFiles

DB_Folder = rf'D:\DB_Upwork'
table_name = 'Jobs'

FilePaths, _ = MyLibs.Scan_DirsFiles.SubdirScanPaths(DB_Folder)
DB_files = [i for i in FilePaths if '.sqlite3' in i]


for file in DB_files:
	try:
		print(file, '...', end='')
		db = MyLibs.SQLite.connect(file)
		MyLibs.SQLite.AddColumn(table_name, 'teamUID', 'INTEGER', db)
		#MyLibs.SQLite.AddColumn(table_name, 'subcategory2_uid', 'INTEGER', db)
		db.close()
		print('OK')
	except Exception as e:
		print(e)
		
if __name__ == '__main__': pass

	
	