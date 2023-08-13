import MyLibs.SQLite
import sys, pickle, datetime
import MyLibs.CSV_read_and_write
import DB_Manager_Upwork

	
if __name__ == '__main__':
	import json, time
	
	#=======with JSON all files
	import MyLibs.files_in_folder as ScanFolder
	File_list = ScanFolder.Abs_filenames(r'D:\xxxx\xxxx\Python\PY\Raw_Jsons\Full_DB_24_05')
	print('File_List', len(File_list))
	input('Press any key')
	
	Total_DB = []
	Search = []
	start = time.time()
	
	for file in File_list:
		try:
			js = open(file)
			json_data = js.read()
			js.close()
			json_PyObj = json.loads(json_data)
			Jobs = json_PyObj['searchResults']['jobs']
			assert Jobs != None, f'Jobs == None in {file}'
		except Exception as e:
			print(f"{file}\n{e}")
			input('Press any key')
		
		
		for job in Jobs:
			Search.append(job)
	print('Done!!')
