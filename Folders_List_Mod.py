import os
import pprint

#Actualization List of URL (Folders_List.py) to sites and names of their folders
def Folders_List (CWD):
	print '\n','.'*20,"Folder's Check",'.'*20,'\n'
	
	#import Python module from folder
	import Templates.Folders_List

	#check Python module for variable 'List'
	if 'List' not in list(Templates.Folders_List.__dict__.keys()):
		Old_List = {}
	else:
		Old_List = Templates.Folders_List.List
		
	#Creating list of dirs in Templates folder
	Dir_List = []
	for root, dirs, files in os.walk(CWD + '\\Templates'):
		for d in dirs:
			Dir_List.append(d)
			
	print 'Updating...'
	New_List = {}
	delta = len(Old_List.keys()) - len(Dir_List)
	if delta <= 0: #adding new folders to New_List
		for folder in Dir_List: 
			try:
				site_file = open(CWD + '\\Templates\\' + folder + '\\Site.txt')
				site = site_file.read().rstrip() #read and kill /n symbol 
				New_List[site] = folder
				site_file.close()
				print '%s ... Ok' %(folder)
			except IOError:
				print 'No Site.txt in folder %s' %(folder)
				
	elif delta > 0: #rewriting New_List from Old_List without deleted folders
		print 'Deleting old folders in Folders list...(%s)' %(delta)
		for site in Old_List:
			if Old_List[site] in Dir_List:
				print '%s ... Ok' %(site)
				New_List[site] = Old_List[site]
						
	#Write Python object to Python file 
	from Libs.PyObject_to_PyFile import Write
	Write(CWD + '\\Templates\\' + 'Folders_List.py', New_List)
	print 'List updated.'
	
	return New_List

	
	
if __name__ == '__main__':
	import sys
	if sys.path[0] == '\\storage\\emulated\\0\\qpython':
		CWD = sys.path[0] + '\\projects\\parser'
	else:
		CWD = sys.path[0]	
	
	print Folders_List(CWD)
	
	