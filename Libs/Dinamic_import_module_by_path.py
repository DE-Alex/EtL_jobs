#!!!!!!!!!!!!!!!!!
import importlib
#!!!!!!!!!!!!!!!!!



def Import_by_path(path):
	#path - relative path from current working directory to module_path
	#example: we have file named '\Libs\CSV_read_and_write.py' with Libs as current work directory
	#path = '\\CSV_read_and_write' 
	#print 'Path to module:', path
	
	module_path = path[1:].replace('\\','.')
	print 'Module path:', module_path
	My_module = importlib.import_module(module_path)
	#print 'Import done!!!'
	return My_module

	
if __name__ == '__main__':
	
	path = '\\CSV_read_and_write' 
	Import_by_path(path)
	
	
