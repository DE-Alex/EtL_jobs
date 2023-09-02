import sys
from pathlib import Path

def write_in(user_agent):
	#firstline = 'def request(flow):\n'
	#secondline = f'    flow.request.headers["User-Agent"] = "{user_agent}"'
    
    text = 'def request(flow):\n    flow.request.headers["User-Agent"] = "{user_agent}"'
    
    path = Path(sys.path[0], 'MTM', 'mtm_setHeaders.py')
    
	with open(path, 'w') as file:
		#file.write(firstline + secondline)
        file.write(text)
	print('User-Agent updated')
	
		
if __name__ == '__main__': pass
	# print(r'D:\Shapovalov\svoe\Python\PY\Parser4\Proxy\_mtm_setHeaders.py')
	# UserAgent = 'Test_User-Agent'
	# write_in(UserAgent)