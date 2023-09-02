#write and read python object to file
import pprint

def write(py_obj, file_path):
	import os
	directory = os.path.dirname(file_path)
	if not os.path.exists(directory):
		os.makedirs(directory)
	try:	
		with open (file_path, 'w') as file:
			file.write(pprint.pformat(py_obj))
	except:
		with open (file_path, 'w', encoding = 'utf-8') as file:
			file.write(pprint.pformat(py_obj))
			
def read(file_path):
	try:
		with open(file_path) as file:
			Object = eval(file.read())
			return Object
	except FileNotFoundError as e:
		print(f'{file_path} not found.')
		return None
		
	except SyntaxError as e:
		print(f'{file_path} non Python object.')
		return None	

	
	
if __name__ == '__main__': 
	#pass
	import sys
	from pathlib import Path
	file_path = Path(sys.path[0], 'test_file_with_py_code.txt')
	print("write to:", file_path)
	py_obj = [123, 456, 789]
	Write(py_obj, file_path)
	print('done')
	
	py_obj = Read(file_path)
	print('read:', py_obj)
