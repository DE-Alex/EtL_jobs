#Write Python object to Python file 
import pprint
def Write(path_to_file,PyObject):
	file = open(path_to_file, 'w')
	file.write(pprint.pformat(PyObject))
	file.close()

def Read(path_to_file):
	file = open(path_to_file)
	Object = eval(file.read())
	file.close()
	return Object
	
	
	
if __name__ == '__main__':
	import sys
	
	cc =   [u'\u041f\u0442, 30 \u043e\u043a\u0442 2020 03:19:34 GMT',
	u'\u0421\u0440, 24 \u043e\u043a\u0442 2029 18:55:29 GMT',
	u'\u041f\u043d, 26 \u043e\u043a\u0442 2020 18:57:32 GMT',
	u'\u0412\u0442, 26 \u043e\u043a\u0442 2021 19:11:54 GMT',
	u'\u041f\u043d, 24 \u0444\u0435\u0432 2020 18:55:28 GMT',
	u'\u0412\u0442, 26 \u043e\u043a\u0442 2021 18:57:33 GMT',
	u'\u041f\u043d, 28 \u043e\u043a\u0442 2019 19:11:54 GMT',
	u'\u0412\u0442, 26 \u043d\u043e\u044f 2019 18:55:29 GMT',
	u'\u041f\u0442, 24 \u0430\u043f\u0440 2020 18:57:33 GMT',
	u'\u0412\u0442, 04 \u0444\u0435\u0432 2020 18:55:29 GMT',
	u'\u0421\u0431, 29 \u043e\u043a\u0442 2022 18:57:34 GMT'
	]
	for item in cc:
		print item
	
	
	
	