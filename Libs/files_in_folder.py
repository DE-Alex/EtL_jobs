#Creating list of files in folder
import os
def Abs_filenames(path_to_folder):
	File_List = []
	for root, dirs, files in os.walk(path_to_folder):
		for f in files:
			File_List.append(root + '\\' + f)
	return File_List
	
def Rel_filenames(path_to_folder):
	File_List = []
	for root, dirs, files in os.walk(path_to_folder):
		for f in files:
			File_List.append(f)
	return File_List
	

if __name__ == '__main__':
	import sys
	print '\n Absolute file names:'
	print Abs_filenames(sys.path[0])
	
	print '\n Relative file names:'
	print Rel_filenames(sys.path[0])
	