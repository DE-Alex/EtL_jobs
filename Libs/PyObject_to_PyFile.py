#Write Python object to Python file 
import pprint
def Write(path_to_file,PyObject):
	file = open(path_to_file, 'w')
	file.write('PythonObject = '+ pprint.pformat(PyObject))
	file.close()
	

if __name__ == '__main__':
	import sys
	path_to_file = sys.path[0]+ '\\Test_File_with_Py_code.py'
	print "Write to:", path_to_file
	PyObject = [123]
	Write(path_to_file,PyObject)
	print 'Done'
	