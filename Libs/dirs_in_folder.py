#Creating list of dirs in folder
import os
def List(path_to_folder):
	Dir_List = []
	for root, dirs, files in os.walk(path_to_folder):
		for d in dirs:
			Dir_List.append(d)
	return Dir_List
	

if __name__ == '__main__':
	import sys
	print List(sys.path[0])
	