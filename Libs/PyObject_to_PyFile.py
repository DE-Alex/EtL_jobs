#Write Python object to Python file 
import pprint
def Write(PyObject, path_to_file):
	import os
	directory = os.path.dirname(path_to_file)
	if not os.path.exists(directory):
		os.makedirs(directory)
	
	file = open(path_to_file, 'w')
	file.write(pprint.pformat(PyObject))
	file.close()

def Read(path_to_file):
	file = open(path_to_file)
	Object = eval(file.read())
	file.close()
	return Object
	
	
	
if __name__ == '__main__':
	pass