
#Return list of variables in Python module
def List (module):
	return list(module.__dict__.keys())
	

if __name__ == '__main__':
	import variables_in_module #imports itself
	print List(variables_in_module)
	