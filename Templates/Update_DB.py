import os

def Update(CWD):
	#Creating list of files in Templates folder
	File_List = []
	DB = {}
	for root, dirs, files in os.walk(CWD + '\\www_Upwork_com'):
		print files
		for f in files:
			print f
			File_List.append(f)
			from f import login, password, SiteURL
			DB[SiteURL] = login, password, f

	print DB	
		

	
	
if __name__ == '__main__':
	import sys
	if sys.path[0] == '\\storage\\emulated\\0\\qpython':
		CWD = sys.path[0] + '\\projects\\parser'
	else:
		CWD = sys.path[0]	
	print Update(CWD)

	
	