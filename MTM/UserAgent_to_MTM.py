def write_in(UserAgent):
	firstline = 'def request(flow):\n'
	secondline = f'	flow.request.headers["User-Agent"] = "{UserAgent}"'
	with open(r'D:\Shapovalov\svoe\Python\PY\Parser5\MTM\_mtm_setHeaders.py', 'w') as file:
		file.write(firstline + secondline)
	print('User-Agent updated')
	
		
if __name__ == '__main__': pass
	# print(r'D:\Shapovalov\svoe\Python\PY\Parser4\Proxy\_mtm_setHeaders.py')
	# UserAgent = 'Test_User-Agent'
	# write_in(UserAgent)